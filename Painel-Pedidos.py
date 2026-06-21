import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira instrução Streamlit do arquivo)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portal de Pedidos - Molicenter",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO GLOBAIS
# ─────────────────────────────────────────────────────────────────────────────
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

if 'reset_counter_folhagem' not in st.session_state:
    st.session_state['reset_counter_folhagem'] = 0

# ─────────────────────────────────────────────────────────────────────────────
# 3. CONSTANTES GLOBAIS
# ─────────────────────────────────────────────────────────────────────────────
LOJAS = ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06", "Loja 07", "Loja 08"]
MAPA_LOJAS = {l: l for l in LOJAS}

# ─────────────────────────────────────────────────────────────────────────────
# 4. CONEXÕES E CACHE GLOBAL (Crucial para evitar travamentos)
# ─────────────────────────────────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)
conn_pg = st.connection("banco_erp", type="sql")

@st.cache_data(ttl=60)
def buscar_estoque_pg(loja_nome, codigos):
    if not codigos:
        return pd.DataFrame(columns=["Código", "Estoque"])
    
    loja_id = int(loja_nome.split()[-1])
    loja_id_str = f"{loja_id:03d}" 
    cods_str = ", ".join(map(str, set(codigos)))
    
    query = f"""
        SELECT 
            cade_codigo AS "Código",
            estoque AS "Estoque"
        FROM python_estoque
        WHERE cade_codempresa = '{loja_id_str}'
        AND cade_codigo IN ({cods_str})
    """
    try:
        df_est = conn_pg.query(query)
        return df_est
    except Exception as e:
        return pd.DataFrame({"Código": codigos, "Estoque": 0})

def buscar_produtos_pg(codigos):
    if not codigos:
        return pd.DataFrame(columns=["Código", "Descrição"])
        
    cods_str = ", ".join(map(str, set(codigos)))
    
    query = f"""
        SELECT DISTINCT
            cade_codigo AS "Código",
            cadp_descricao AS "Descrição"
        FROM python_estoque
        WHERE cade_codigo IN ({cods_str})
    """
    try:
        return conn_pg.query(query)
    except Exception as e:
        st.error(f"Erro ao buscar produtos na view python_estoque: {e}")
        return pd.DataFrame()

def atualizar_vendas_90d():
    query = """
    WITH vendas_90d AS (
         SELECT lpd.lcpd_codempresa AS loja,
            lpd.lcpd_codproduto AS codigo,
            lpd.lcpd_qtde AS quantidade,
            lpd.lcpd_dtmvto AS data_venda
           FROM lpd202605 lpd
          WHERE (lpd.lcpd_tipoprocesso::text = ANY (ARRAY['VN'::text, 'VP'::text, 'VD'::text, 'VX'::text, 'VB'::text, 'VC'::text])) AND (lpd.lcpd_codempresa::text <= '008'::text OR lpd.lcpd_codempresa::text = '031'::text) AND lpd.lcpd_situacao::text = 'N'::text
        UNION ALL
         SELECT lpd.lcpd_codempresa,
            lpd.lcpd_codproduto,
            lpd.lcpd_qtde,
            lpd.lcpd_dtmvto
           FROM lpd202604 lpd
          WHERE (lpd.lcpd_tipoprocesso::text = ANY (ARRAY['VN'::text, 'VP'::text, 'VD'::text, 'VX'::text, 'VB'::text, 'VC'::text])) AND (lpd.lcpd_codempresa::text <= '008'::text OR lpd.lcpd_codempresa::text = '031'::text) AND lpd.lcpd_situacao::text = 'N'::text
        UNION ALL
         SELECT lpd.lcpd_codempresa,
            lpd.lcpd_codproduto,
            lpd.lcpd_qtde,
            lpd.lcpd_dtmvto
           FROM lpd202603 lpd
          WHERE (lpd.lcpd_tipoprocesso::text = ANY (ARRAY['VN'::text, 'VP'::text, 'VD'::text, 'VX'::text, 'VB'::text, 'VC'::text])) AND (lpd.lcpd_codempresa::text <= '008'::text OR lpd.lcpd_codempresa::text = '031'::text) AND lpd.lcpd_situacao::text = 'N'::text
        )
    SELECT vendas_90d.loja,
        vendas_90d.codigo,
        round(sum(vendas_90d.quantidade) / 90.0, 2) AS media_dia
      FROM vendas_90d
     GROUP BY vendas_90d.loja, vendas_90d.codigo
     ORDER BY vendas_90d.loja, vendas_90d.codigo;
    """
    try:
        df_vendas = conn_pg.query(query)
        conn.update(worksheet="Folhagem_90d", data=df_vendas)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar vendas 90d: {e}")
        return False

@st.cache_data(ttl=15)
def carregar_catalogo_folhagem():
    df = conn.read(worksheet="Produtos_Folhagem", ttl=0, usecols=list(range(20)))
    if df.empty:
        return pd.DataFrame(columns=["Código", "Descrição", "Nome Personalizado", "Fornecedor"] + LOJAS)
    
    novas_colunas = {}
    for col in df.columns:
        col_str = str(col).strip()
        for loja in LOJAS:
            if loja.lower() in col_str.lower():
                novas_colunas[col] = loja
    df = df.rename(columns=novas_colunas)
    
    if "Nome Personalizado" not in df.columns:
        df["Nome Personalizado"] = ""
    df["Nome Personalizado"] = df["Nome Personalizado"].fillna("").astype(str)
    
    for col in LOJAS:
        if col not in df.columns:
            df[col] = False
        else:
            def parse_bool(x):
                if isinstance(x, bool): return x
                if isinstance(x, (int, float)): return bool(x) and not pd.isna(x)
                return str(x).strip().upper() in ['TRUE', 'VERDADEIRO', '1', 'V', 'SIM', 'YES', 'T', 'X']
            df[col] = df[col].apply(parse_bool)
            
    if "Código" in df.columns:
        df["Código"] = pd.to_numeric(df["Código"], errors='coerce').fillna(0).astype(int)
    return df

@st.cache_data(ttl=15)
def carregar_pedidos():
    df_pedidos = conn.read(worksheet="Folhagem", ttl=0)
    df_cat = carregar_catalogo_folhagem()
    
    if not df_pedidos.empty:
        novas_colunas_ped = {}
        for col in df_pedidos.columns:
            col_str = str(col).strip()
            for loja in LOJAS:
                if loja.lower() in col_str.lower():
                    novas_colunas_ped[col] = loja
        df_pedidos = df_pedidos.rename(columns=novas_colunas_ped)
    
    if df_pedidos.empty or "Fornecedor" not in df_pedidos.columns:
        df_init = df_cat[["Código", "Descrição", "Fornecedor"]].copy()
        for loja in LOJAS: df_init[loja] = 0
        if not df_init.empty:
            conn.update(worksheet="Folhagem", data=df_init)
        return df_init
    
    if "Código" in df_pedidos.columns:
        df_pedidos["Código"] = pd.to_numeric(df_pedidos["Código"], errors='coerce').fillna(0).astype(int)
    for loja in LOJAS:
        if loja in df_pedidos.columns:
            df_pedidos[loja] = pd.to_numeric(df_pedidos[loja], errors='coerce').fillna(0).astype(int)
    return df_pedidos

@st.cache_data(ttl=30)
def carregar_vendas_90d():
    try:
        return conn.read(worksheet="Folhagem_90d", ttl=0)
    except Exception:
        return pd.DataFrame(columns=["loja", "codigo", "media_dia"])

def salvar_pedidos(df_to_save):
    try:
        conn.update(worksheet="Folhagem", data=df_to_save)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro técnico ao salvar os pedidos: {e}")
        return False

def salvar_catalogo(df_to_save):
    try:
        conn.update(worksheet="Produtos_Folhagem", data=df_to_save)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro técnico ao salvar o catálogo: {e}")
        return False

# ─────────────────────────────────────────────────────────────────────────────
# 5. ESTILIZAÇÃO CSS GLOBAL (Aplicada em todo o portal)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;700&display=swap');
:root {
    --bg-main:        #0d1117;
    --bg-card:        #161b22;
    --bg-sidebar:     #0d1117;
    --green-dark:     #1a3a2a;
    --green-mid:      #1f4d35;
    --green-accent:   #2ea043;
    --green-bright:   #3fb950;
    --green-glow:     rgba(46,160,67,.25);
    --text-primary:   #e6edf3;
    --text-muted:     #7d8590;
    --text-header:    #cae8cb;
    --border:         #21262d;
    --border-active:  #2ea043;
}
.stApp, .main { background-color: var(--bg-main) !important; color: var(--text-primary) !important; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif !important; }
section[data-testid="stSidebar"] { background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--green-mid) 0%, var(--green-accent) 100%) !important;
    color: #fff !important; border: 1px solid var(--green-accent) !important;
    border-radius: 8px !important; font-weight: 700 !important; transition: all .2s ease !important;
}
.stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 4px 18px var(--green-glow) !important; }
.stButton > button { background: var(--bg-card) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stButton > button:hover { border-color: var(--green-accent) !important; color: var(--green-bright) !important; }
.stTextInput input, .stSelectbox > div > div { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text-primary) !important; }
[data-testid="stDataEditor"] { border-radius: 10px !important; overflow: hidden; border: 1px solid var(--green-mid) !important; box-shadow: 0 4px 20px rgba(0,0,0,.4); font-size: 12px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }
[data-testid="stMetric"] { background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 10px 10px; }
[data-testid="stMetricValue"] { color: var(--green-bright) !important; font-weight: 700; font-size: 1.8rem !important; }
.topbar-loja { background: linear-gradient(90deg, var(--green-dark) 0%, #0d2018 100%); border: 1px solid var(--green-mid); border-radius: 10px; padding: 10px 18px; margin-bottom: 18px; display: flex; align-items: center; justify-content: space-between; }
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-title { font-size: 18px; font-weight: 700; color: var(--text-header); }
.topbar-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.title-input input { font-weight: 700 !important; font-size: 16px !important; color: var(--green-bright) !important; background: transparent !important; border: 1px dashed #21262d !important; }

@media print {
    @page { margin: 5mm 10mm; } 
    .stApp, .main, body, html { background-color: #ffffff !important; color: #000000 !important; }
    header, [data-testid="stSidebar"], [data-testid="stHeader"], button, .stAlert, .stInfo { display: none !important; }
    #print-section { display: block !important; width: 100% !important; }
    table.print-table { width: 100%; border-collapse: collapse; font-size: 10px !important; color: #000000 !important; }
    table.print-table th, table.print-table td { border: 1px solid #000000 !important; padding: 2px 4px !important; }
    table.print-table th { background-color: #e0e0e0 !important; font-weight: bold; -webkit-print-color-adjust: exact; }
}
@media screen { #print-section { display: none !important; } }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 6. PORTAL DE LOGIN CENTRALIZADO
# ─────────────────────────────────────────────
if st.session_state['usuario_logado'] is None:
    st.write("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            h1, h2 = st.columns([4, 1])
            with h1:
                st.markdown("""
                    <h2 style='margin-bottom:0'>Portal de Pedidos</h2>
                    <p style='color:#7d8590;font-size:14px;margin-top:4px'>Acesso Unificado — Molicenter</p>
                """, unsafe_allow_html=True)
            with h2:
                st.write("<br>", unsafe_allow_html=True)
                st.markdown("<h1 style='margin:0; padding:0;'>📦</h1>", unsafe_allow_html=True)

            st.divider()
            usuarios_permitidos = ["Selecione..."] + ["Administrador"] + LOJAS
            usuario_selecionado = st.selectbox("👤 Usuário de acesso:", usuarios_permitidos)
            senha_digitada = st.text_input("🔑 Senha de acesso:", type="password", autocomplete="off")
            st.write("<br>", unsafe_allow_html=True)

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
                if usuario_selecionado == "Selecione...":
                    st.error("⚠️ Por favor, selecione um usuário.")
                elif usuario_selecionado == "Administrador" and senha_digitada == "moli0000":
                    st.session_state['usuario_logado'] = usuario_selecionado
                    st.rerun()
                elif usuario_selecionado in LOJAS and senha_digitada == "moli1234":
                    st.session_state['usuario_logado'] = usuario_selecionado
                    st.rerun()
                elif senha_digitada:
                    st.error("⚠️ Senha incorreta. Tente novamente.")
            st.markdown('<p style="font-size: 11px; color: #7d8590; text-align: center; margin-top: 10px;">🔒 Acesso restrito — Molicenter © 2026</p>', unsafe_allow_html=True)
    st.stop()

# Captura dados após autenticação bem-sucedida
usuario_atual = st.session_state['usuario_logado']
acesso_total  = (usuario_atual == "Administrador")

# Oculta controles de navegação nativos do Streamlit para usuários comuns se necessário
if not acesso_total:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"]  { display: none !important; }
        .main .block-container { max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 7. ENCAPSULAMENTO DO MÓDULO DE FOLHAGEM
# ─────────────────────────────────────────────────────────────────────────────
def modulo_folhagem():
    # Sub-Roteamento interno da Folhagem
    if acesso_total:
        st.sidebar.markdown("### 🥬 Menu Folhagem")
        perfil_navegacao = st.sidebar.radio("📍 Sub-Navegação:", [
            "Separação e Fechamento",
            "Visão das Lojas",
            "Visão Fornecedores (Resumo)",
            "Catálogo de Produtos" 
        ], key="nav_interna_folhagem")
    else:
        perfil_navegacao = "Visão das Lojas"

    # Diálogo interno para zerar registros
    @st.dialog("🚨 Confirmação Necessária")
    def modal_zerar_pedidos():
        st.markdown("Tem certeza que deseja **zerar todos os pedidos** de todas as lojas?")
        st.write("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("❌ Não, cancelar", use_container_width=True): st.rerun()
        with c2:
            if st.button("✔️ Sim, zerar tudo", type="primary", use_container_width=True):
                with st.spinner("Zerando base de dados..."):
                    st.session_state['reset_counter_folhagem'] += 1
                    df_main = carregar_pedidos()
                    for loja in LOJAS:
                        if loja in df_main.columns: df_main[loja] = 0
                    if salvar_pedidos(df_main): st.rerun()

    # ROTA 1 — SEPARAÇÃO E FECHAMENTO
    if perfil_navegacao == "Separação e Fechamento":
        st.markdown("""
        <div class="topbar-loja">
            <div class="topbar-left">
                <span style="font-size: 26px; margin-right: 12px;">📊</span>
                <div>
                    <div class="topbar-title">Separação e Fechamento — Folhagem</div>
                    <div class="topbar-sub">Consolidado geral de quantidades por fornecedor</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            df_base = carregar_pedidos()
            if df_base.empty:
                st.warning("A base de pedidos está vazia.")
                st.stop()
                
            df_base["TOTAL GERAL"] = df_base[LOJAS].sum(axis=1)
            col_cfg = {
                "Fornecedor":  st.column_config.TextColumn("Fornecedor", disabled=True),
                "Código":      st.column_config.NumberColumn("Cód", width=80, format="%d", disabled=True),
                "Descrição":   st.column_config.TextColumn("Produto", disabled=True),
                "TOTAL GERAL": st.column_config.NumberColumn("TOTAL ▶️", width=90, format="%d", disabled=True),
            }
            for loja in LOJAS:
                col_cfg[loja] = st.column_config.NumberColumn(loja, format="%d", min_value=0, step=1)

            cols_order = ["Fornecedor", "Código", "Descrição"] + LOJAS + ["TOTAL GERAL"]
            df_editado = st.data_editor(
                df_base[cols_order], hide_index=True, use_container_width=True, height=550,
                column_config=col_cfg, key=f"sep_editor_{st.session_state['reset_counter_folhagem']}"
            )

            html_table = df_editado.to_html(index=False, classes="print-table")
            st.markdown(f'<div id="print-section"><h2 style="color:black;text-align:center;">Resumo de Separação</h2>{html_table}</div>', unsafe_allow_html=True)

            st.divider()
            col_salvar, col_csv, col_excel, col_print, col_zerar = st.columns([2.5, 1.2, 1.2, 1.5, 2.5])
            with col_salvar:
                if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                    if salvar_pedidos(df_editado.drop(columns=["TOTAL GERAL"])):
                        st.success("✅ Salvo com sucesso!")
                        st.rerun()
            with col_csv:
                st.download_button("⬇️ CSV", data=df_editado.to_csv(index=False).encode("utf-8"), file_name="separacao_folhagem.csv", mime="text/csv", use_container_width=True)
            with col_excel:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_editado.to_excel(writer, index=False, sheet_name='Pedidos')
                st.download_button("⬇️ Excel", data=buffer.getvalue(), file_name="separacao_folhagem.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with col_print:
                if st.button("🖨️ Imprimir", use_container_width=True): components.html("<script>window.parent.print();</script>", height=0)
            with col_zerar:
                if st.button("🚨 Zerar Todos os Pedidos", use_container_width=True): modal_zerar_pedidos()

    # ROTA 2 — VISÃO DAS LOJAS
    elif perfil_navegacao == "Visão das Lojas":
        loja_selecionada = st.selectbox("👁️ Visualizar como:", LOJAS) if acesso_total else usuario_atual

        st.markdown(f"""
        <div class="topbar-loja">
            <div class="topbar-left">
                <span style="font-size:22px">🥬</span>
                <div>
                    <div class="topbar-title">{loja_selecionada} — Folhagem</div>
                    <div class="topbar-sub">Preencha a quantidade desejada de cada produto</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_cat = carregar_catalogo_folhagem()
        df_cat_loja = df_cat[df_cat[loja_selecionada] == True].copy()
        
        if df_cat_loja.empty:
            st.warning(f"Nenhum produto habilitado para a {loja_selecionada}.")
            st.stop()

        df_all = carregar_pedidos()
        df_all_clean = df_all.drop(columns=["Descrição"]) if "Descrição" in df_all.columns else df_all

        df_loja_view = pd.merge(df_cat_loja[["Fornecedor", "Código", "Descrição", "Nome Personalizado"]], df_all_clean[["Código", "Fornecedor", loja_selecionada]], on=["Código", "Fornecedor"], how="left")
        df_loja_view[loja_selecionada] = df_loja_view[loja_selecionada].fillna(0).astype(int)
        
        mask_p = (df_loja_view["Nome Personalizado"].notna()) & (df_loja_view["Nome Personalizado"].str.strip() != "")
        df_loja_view.loc[mask_p, "Descrição"] = df_loja_view.loc[mask_p, "Nome Personalizado"]
        
        df_estoque = buscar_estoque_pg(loja_selecionada, df_loja_view["Código"].unique().tolist())
        df_loja_view = pd.merge(df_loja_view, df_estoque, on="Código", how="left")
        df_loja_view["Estoque"] = df_loja_view["Estoque"].fillna(0).astype(int)

        df_vendas_90d = carregar_vendas_90d()
        if not df_vendas_90d.empty and "loja" in df_vendas_90d.columns:
            loja_id_str = f"{int(loja_selecionada.split()[-1]):03d}"
            df_vendas_loja = df_vendas_90d[df_vendas_90d["loja"].astype(str).str.zfill(3) == loja_id_str].copy()
            df_vendas_loja["codigo"] = pd.to_numeric(df_vendas_loja["codigo"], errors="coerce").fillna(0).astype(int)
            df_vendas_loja = df_vendas_loja.rename(columns={"codigo": "Código", "media_dia": "Venda 90d"})
            df_loja_view = pd.merge(df_loja_view, df_vendas_loja[["Código", "Venda 90d"]], on="Código", how="left")
        else:
            df_loja_view["Venda 90d"] = 0.0

        df_loja_view["Venda 90d"] = df_loja_view["Venda 90d"].fillna(0.0).astype(float)
        df_loja_view = df_loja_view.rename(columns={loja_selecionada: "Qtde"})

        with st.container(border=True):
            col_cfg_loja = {
                "Fornecedor": st.column_config.TextColumn("Fornecedor", width=150, disabled=True),
                "Código":     st.column_config.NumberColumn("Cód", width=65, format="%d", disabled=True),
                "Descrição":  st.column_config.TextColumn("Produto", width=220, disabled=True),
                "Estoque":    st.column_config.NumberColumn("📦 Estoque", width=80, format="%d", disabled=True),
                "Venda 90d":  st.column_config.NumberColumn("📊 Venda 90d", width=120, format="%.2f", disabled=True),
                "Qtde":       st.column_config.NumberColumn("🛒 Qtde", width=90, min_value=0, step=1),
            }
            df_editado = st.data_editor(df_loja_view[["Fornecedor", "Código", "Descrição", "Estoque", "Venda 90d", "Qtde"]], column_config=col_cfg_loja, hide_index=True, use_container_width=True, height=480, key=f"loja_folhagem_{st.session_state['reset_counter_folhagem']}")

        itens_p = int((df_editado["Qtde"] > 0).sum())
        st.divider()
        m1, m2, _, col_btn = st.columns([2.5, 2.2, 2.3, 3])
        m1.metric("Itens preenchidos", f"{itens_p} / {len(df_editado)}")
        m2.metric("Total unidades", int(df_editado["Qtde"].sum()))
        with col_btn:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Pedido da Semana", type="primary", use_container_width=True):
                df_main = carregar_pedidos()
                for _, row in df_editado.iterrows():
                    mask = (df_main["Fornecedor"] == row["Fornecedor"]) & (df_main["Código"] == row["Código"])
                    if mask.any():
                        df_main.loc[mask, loja_selecionada] = row["Qtde"]
                        df_main.loc[mask, "Descrição"] = row["Descrição"]
                if salvar_pedidos(df_main):
                    st.success("✅ Pedido Registrado!")
                    st.rerun()

    # ROTA 3 — VISÃO FORNECEDORES (RESUMO)
    elif perfil_navegacao == "Visão Fornecedores (Resumo)":
        st.markdown('<div class="topbar-loja"><div class="topbar-title">Visão por Fornecedor</div></div>', unsafe_allow_html=True)
        df_all = carregar_pedidos()
        df_cat = carregar_catalogo_folhagem()
        
        if df_all.empty or df_cat.empty:
            st.warning("Sem dados.")
            st.stop()

        for fornecedor in df_cat["Fornecedor"].dropna().unique():
            df_cat_forn = df_cat[df_cat["Fornecedor"] == fornecedor]
            lojas_forn = [l for l in LOJAS if df_cat_forn[l].any()]
            if not lojas_forn: continue 

            df_forn = df_all[df_all["Fornecedor"] == fornecedor].copy()
            colunas_p = [c for c in lojas_forn if c in df_forn.columns]
            df_forn = df_forn[["Código", "Descrição"] + colunas_p].copy()
            df_forn["TOTAL"] = df_forn[colunas_p].sum(axis=1)

            with st.container(border=True):
                st.markdown(f"#### 🥬 Fornecedor: {fornecedor}")
                st.caption(f"Atende: {' · '.join(colunas_p)}")
                
                col_cfg_f = {"Código": st.column_config.NumberColumn("Cód"), "TOTAL": st.column_config.NumberColumn("TOTAL", disabled=True)}
                st.data_editor(df_forn, hide_index=True, use_container_width=True, column_config=col_cfg_f, key=f"f_{fornecedor}_{st.session_state['reset_counter_folhagem']}")

    # ROTA 4 — CATÁLOGO DE PRODUTOS
    elif perfil_navegacao == "Catálogo de Produtos":
        st.markdown('<div class="topbar-loja"><div class="topbar-title">Catálogo de Folhagem</div></div>', unsafe_allow_html=True)
        df_catalogo = carregar_catalogo_folhagem()
        
        with st.container(border=True):
            col_cfg_cat = {
                "Código": st.column_config.NumberColumn("Cód.", width=80, format="%d"),
                "Descrição": st.column_config.TextColumn("Descrição (ERP)", disabled=True),
                "Nome Personalizado": st.column_config.TextColumn("Nome Personalizado"),
                "Fornecedor": st.column_config.TextColumn("Fornecedor"),
            }
            for loja in LOJAS: col_cfg_cat[loja] = st.column_config.CheckboxColumn(loja, default=False)
            
            edited_cat = st.data_editor(df_catalogo[["Fornecedor", "Código", "Descrição", "Nome Personalizado"] + LOJAS], use_container_width=True, hide_index=True, height=500, num_rows="dynamic", column_config=col_cfg_cat, key=f"cat_{st.session_state['reset_counter_folhagem']}")
            
        st.divider()
        col_salvar, col_puxar, _ = st.columns([2, 2, 6])
        with col_salvar:
            if st.button("💾 Salvar Catálogo", type="primary", use_container_width=True):
                if salvar_catalogo(edited_cat):
                    st.success("✅ Catálogo Salvo!")
                    st.rerun()
        with col_puxar:
            if st.button("🔄 Puxar Nomes do ERP", use_container_width=True):
                codigos = [int(c) for c in edited_cat["Código"].dropna().unique() if c > 0]
                if codigos:
                    df_pg = buscar_produtos_pg(codigos)
                    if not df_pg.empty:
                        dict_n = dict(zip(df_pg["Código"], df_pg["Descrição"]))
                        edited_cat["Descrição"] = edited_cat["Código"].map(dict_n).fillna(edited_cat["Descrição"])
                        if salvar_catalogo(edited_cat):
                            st.success("✅ Nomes Sincronizados com o ERP!")
                            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 8. OUTROS MÓDULOS (Espaço reservado para expansão futura)
# ─────────────────────────────────────────────────────────────────────────────
def modulo_padaria():
    st.title("🥖 Setor de Padaria")
    st.info("Espaço reservado para a migração do script de pedidos da Padaria.")

def modulo_checkin():
    st.title("📍 Check-in de Promotores")
    st.info("Espaço reservado para a migração do script de Check-in de Promotores.")


# ─────────────────────────────────────────────────────────────────────────────
# 9. CONTROLE LATERAL MASTER (Roteamento entre Aplicativos)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.write(f"### Olá, **{usuario_atual}**")
    st.caption("Painel Central Molicenter")
    st.divider()
    
    if acesso_total:
        # Apenas administradores escolhem o setor de trabalho global
        setor_escolhido = st.selectbox(
            "📦 Selecione o Programa Master:",
            ["🥬 Folhagem", "🥖 Padaria", "📍 Check-in"]
        )
    else:
        # Lojas caem diretamente na Folhagem por padrão (ou configure como preferir)
        setor_escolhido = "🥬 Folhagem"
        
    st.write("<br><br>", unsafe_allow_html=True)

# Executa o módulo selecionado no Roteador Master
if "Folhagem" in setor_escolhido:
    modulo_folhagem()
elif "Padaria" in setor_escolhido:
    modulo_padaria()
elif "Check-in" in setor_escolhido:
    modulo_checkin()

# Rodapé da barra lateral com os botões universais do sistema
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 Sincronizar Tudo (Limpar Cache)", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    if st.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state['usuario_logado'] = None
        st.rerun()
