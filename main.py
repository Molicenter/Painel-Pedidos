import streamlit as st
import base64
import os

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gestão Pedidos - Molicenter",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. IMPORTAÇÃO DOS MÓDULOS
# ─────────────────────────────────────────────────────────────────────────────
import flv_folhagem
import flv_normal
import flv_ofertas
import flv_oriental
import acougue_total
import acougue_especiais
import acougue_pecas
import embalagem
import padaria_confeitaria
import materia_prima

# ─────────────────────────────────────────────────────────────────────────────
# 3. IMAGENS EXTERNAS
# ─────────────────────────────────────────────────────────────────────────────
IMG_FOLHAGEM = "https://images.unsplash.com/photo-1574316071802-0d684efa7bf5?w=400"
IMG_FLV      = "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=400"
IMG_ORIENTAL = "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400"
IMG_ACOUGUE  = "https://images.unsplash.com/photo-1544025162-d76694265947?w=400"
IMG_PADARIA  = "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400"

@st.cache_data
def imagem_para_b64(caminho):
    if not caminho: return ""
    if caminho.startswith("http"): return caminho
    try:
        with open(caminho, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = caminho.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{encoded}"
    except:
        return ""

# ─────────────────────────────────────────────────────────────────────────────
# 4. VARIÁVEIS DE SESSÃO
# ─────────────────────────────────────────────────────────────────────────────
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

if 'modulo_ativo' not in st.session_state:
    st.session_state['modulo_ativo'] = 'Home'

# ─────────────────────────────────────────────────────────────────────────────
# 5. CSS
# ─────────────────────────────────────────────────────────────────────────────
zoom_value = "0.90" if st.session_state.get('usuario_logado') else "1.0"

st.markdown(f"""
<style>
/* ── Base ── */
.stApp, .main {{
    background-color: #0e1117 !important;
}}
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    max-width: 95% !important;
    zoom: {zoom_value} !important;
}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{background-color: transparent !important;}}

/* ── Banner ── */
.banner-container {{
    background: linear-gradient(135deg, #07263b 0%, #0e4a74 100%);
    padding: 12px 24px;
    border-radius: 8px;
    margin-bottom: 25px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 4px 15px rgba(0, 147, 233, 0.15);
    border: 1px solid rgba(255,255,255,0.1);
}}
.banner-logo {{ height: 40px; width: auto; object-fit: contain; }}
.banner-title {{
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #fff;
}}

/* ── Cards ── */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: #1a1c24 !important;
    border-radius: 8px !important;
    border: 1px solid #30363d !important;
    transition: all 0.25s ease !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: #5cb3e6 !important;
    background-color: #1f222b !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    padding: 12px !important;
    gap: 6px !important;
}}

/* ── Títulos de setor ── */
.linha-titulo-sec {{
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #5cb3e6;
    margin-bottom: 8px;
    margin-top: 15px;
    font-weight: 700;
    border-left: 3px solid #1f8bbf;
    padding-left: 8px;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 6. TELA DE LOGIN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state['usuario_logado'] is None:
    st.write("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])

    with col2:
        with st.container(border=True):
            st.write("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div style='text-align:center;'>
                    <h2 style='margin-bottom:0; color:white;'>Portal de Pedidos</h2>
                    <p style='color:#7d8590;font-size:14px;'>Acesso Unificado — Molicenter</p>
                </div>
            """, unsafe_allow_html=True)
            st.divider()

            LOJAS_LOGIN = ["Loja 01", "Loja 02", "Loja 03", "Loja 04",
                           "Loja 05", "Loja 06", "Loja 07", "Loja 08"]
            usuarios_permitidos = ["Selecione...", "Administrador"] + LOJAS_LOGIN
            usuario_selecionado = st.selectbox("👤 Usuário de acesso:", usuarios_permitidos)
            senha_digitada = st.text_input("🔑 Senha de acesso:", type="password", autocomplete="off")
            st.write("<br>", unsafe_allow_html=True)

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
                if usuario_selecionado == "Selecione...":
                    st.error("⚠️ Por favor, selecione um usuário.")
                elif usuario_selecionado == "Administrador" and senha_digitada == "moli0000":
                    st.session_state['usuario_logado'] = usuario_selecionado
                    st.rerun()
                elif usuario_selecionado in LOJAS_LOGIN and senha_digitada == "moli1234":
                    st.session_state['usuario_logado'] = usuario_selecionado
                    st.rerun()
                elif senha_digitada:
                    st.error("⚠️ Senha incorreta. Tente novamente.")

            st.write("<br>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 7. CAPTURA DE NAVEGAÇÃO VIA QUERY PARAM (antes de renderizar)
# ─────────────────────────────────────────────────────────────────────────────
nav = st.query_params.get("nav", None)
if nav:
    st.query_params.clear()
    st.session_state['modulo_ativo'] = nav
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 8. FUNÇÃO DOS CARDS
# ─────────────────────────────────────────────────────────────────────────────
def criar_card(titulo, subtitulo, caminho_imagem, emoji_fallback, chave_modulo):
    img_src = imagem_para_b64(caminho_imagem)

    with st.container(border=True):
        # Imagem com inline style (garante largura total)
        if img_src:
            st.markdown(f"""
            <div style="width:100%; height:115px; border-radius:4px; overflow:hidden;
                        margin-bottom:6px; background:#0e1117;">
                <img src="{img_src}" style="width:100%; height:100%;
                           object-fit:cover; display:block;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="width:100%; height:115px; border-radius:4px;
                        background:#0e1117; display:flex;
                        align-items:center; justify-content:center;">
                <span style="font-size:40px;">{emoji_fallback}</span>
            </div>
            """, unsafe_allow_html=True)

        # Botão HTML puro — visual branco/preto, clique via JS query param
        st.markdown(f"""
        <button onclick="
            const url = new URL(window.parent.location.href);
            url.searchParams.set('nav', '{chave_modulo}');
            window.parent.location.href = url.toString();
        " style="
            width: 100%;
            min-height: 36px;
            background-color: #ffffff;
            color: #000000;
            font-weight: 700;
            font-size: 13px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 4px;
            padding: 5px 10px;
            box-sizing: border-box;
        ">{titulo}</button>
        """, unsafe_allow_html=True)

        # Horário centralizado
        st.markdown(f"""
        <div style="font-size:11px; color:#c9d1d9; line-height:1.5;
                    min-height:32px; display:flex; align-items:center;
                    justify-content:center; text-align:center;
                    margin-top:6px; padding:0 4px;">
            {subtitulo}
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 9. DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def renderizar_dashboard():
    logo_src = imagem_para_b64("passaro_logo.png")
    img_tag = f'<img src="{logo_src}" class="banner-logo" alt="Logo">' if logo_src else '<span style="font-size:28px">🛒</span>'

    st.markdown(f"""
    <div class="banner-container">
        {img_tag}
        <div class="banner-title">Gestão Pedidos - Molicenter</div>
    </div>
    """, unsafe_allow_html=True)

    # --- LINHA 1: FLV ---
    st.markdown('<div class="linha-titulo-sec">🥦 Setor Hortifruti (FLV)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: criar_card("Folhagem", "Seg a Sáb até 12:00hrs", IMG_FOLHAGEM, "🥬", "flv_folhagem")
    with c2: criar_card("FLV Normal", "Terças-feira até 17:00hrs<br>Quintas-feira até 14:00hrs", IMG_FLV, "🍎", "flv_normal")
    with c3: criar_card("FLV Ofertas", "Quintas-feiras até 14:00hrs", IMG_FLV, "🏷️", "flv_ofertas")
    with c4: criar_card("FLV Oriental", "Quintas-feiras até 14:00hrs", IMG_ORIENTAL, "🍣", "flv_oriental")

    # --- LINHA 2: Açougue ---
    st.markdown('<div class="linha-titulo-sec">🥩 Setor Açougue e Aves</div>', unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns(4, gap="medium")
    with c1: criar_card("Pioneiro + BF + Paraná", "Seg a Sex até 11:00hrs", "Pioneiros.jpg", "🍗", "acougue_especiais")
    with c2: criar_card("Açougue Adriano", "Quartas-feira até 15:00hrs<br>Sábado até 15:00hrs", IMG_ACOUGUE, "🔪", "acougue_total")
    with c3: criar_card("Peças Açougue - Manoel", "Seg/Qua/Sex — Arap. 15:00h<br>Ter/Qui/Sáb — Maringá 15:00h", "img_manoel.jpg", "🥩", "acougue_pecas")

    # --- LINHA 3: Outros ---
    st.markdown('<div class="linha-titulo-sec">📦 Outros Setores e Logística</div>', unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns(4, gap="medium")
    with c1: criar_card("Embalagens", "Sexta-feira até as 17:30hrs", "Embalagens.jpg", "🥡", "embalagem")
    with c2: criar_card("Padaria e Confeitaria", "Sábado", IMG_PADARIA, "🥖", "padaria_confeitaria")
    with c3: criar_card("Matéria Prima", "Até Sábado", "materiaprima.jpg", "🌾", "materia_prima")

    st.write("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; margin-top:5px; padding-bottom:20px;
                color:#ffffff; font-size:14px; font-weight:500;">
        Molicenter Supermercados © 2026 — Painel Web de Pedidos Centralizados
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 10. ROTEADOR
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state['modulo_ativo'] == 'Home':
    renderizar_dashboard()
else:
    with st.sidebar:
        st.write(f"👤 Utilizador: **{st.session_state['usuario_logado']}**")
        st.divider()
        if st.button("⬅️ Voltar ao Painel Central", use_container_width=True, type="primary"):
            st.session_state['modulo_ativo'] = 'Home'
            st.rerun()
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state['usuario_logado'] = None
            st.session_state['modulo_ativo'] = 'Home'
            st.rerun()

    if st.session_state['modulo_ativo'] == 'flv_folhagem':
        flv_folhagem.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'flv_normal':
        flv_normal.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'flv_ofertas':
        flv_ofertas.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'flv_oriental':
        flv_oriental.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'embalagem':
        embalagem.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'padaria_confeitaria':
        padaria_confeitaria.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'materia_prima':
        materia_prima.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'acougue_especiais':
        acougue_especiais.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'acougue_total':
        acougue_total.iniciar_tela()
    elif st.session_state['modulo_ativo'] == 'acougue_pecas':
        acougue_pecas.iniciar_tela()
