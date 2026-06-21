import streamlit as st
import base64
import os

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO DA PÁGINA (Única para todo o portal)
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
# 3. LINKS E VARIÁVEIS DE IMAGENS EXTERNAS
# ─────────────────────────────────────────────────────────────────────────────
IMG_FOLHAGEM = "https://images.unsplash.com/photo-1574316071802-0d684efa7bf5?w=400"
IMG_FLV      = "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=400"
IMG_ORIENTAL = "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400"
IMG_ACOUGUE  = "https://images.unsplash.com/photo-1544025162-d76694265947?w=400"
IMG_PADARIA  = "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400"

# Função inteligente que lê tanto Links da Web quanto Imagens Locais do GitHub
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
# 4. VARIÁVEIS DE SESSÃO GLOBAIS E CSS DO PAINEL
# ─────────────────────────────────────────────────────────────────────────────
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

if 'modulo_ativo' not in st.session_state:
    st.session_state['modulo_ativo'] = 'Home'

# Estilo específico para deixar os botões do Dashboard Brancos como na foto antiga
st.markdown("""
<style>
.main div[data-testid="stButton"] button[kind="secondary"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    transition: all 0.2s;
}
.main div[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 5. TELA DE LOGIN ÚNICA DO PORTAL
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state['usuario_logado'] is None:
    st.write("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            st.markdown("""
                <div style='text-align:center;'>
                    <h2 style='margin-bottom:0'>Portal de Pedidos</h2>
                    <p style='color:#7d8590;font-size:14px;'>Acesso Unificado — Molicenter</p>
                </div>
            """, unsafe_allow_html=True)
            st.divider()
            
            LOJAS_LOGIN = ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06", "Loja 07", "Loja 08"]
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
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 6. FUNÇÕES PARA GERAR A VITRINE DE CARDS (DASHBOARD ELEGANTE)
# ─────────────────────────────────────────────────────────────────────────────
def titulo_secao(icone, texto):
    st.markdown(f"""
    <div style="border-left: 4px solid #1375b7; padding-left: 10px; margin-bottom: 15px; margin-top: 25px;">
        <h4 style="margin: 0; color: #6db6e3; font-size: 14px; font-weight: 700; text-transform: uppercase;">{icone} {texto}</h4>
    </div>
    """, unsafe_allow_html=True)

def criar_card(titulo, subtitulo, caminho_imagem, emoji_fallback, chave_modulo):
    img_src = imagem_para_b64(caminho_imagem)
    
    with st.container(border=True):
        # A imagem fica travada em 110px de altura. Nada vai esticar a tela!
        if img_src:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 110px; margin-bottom: 12px;">
                <img src="{img_src}" style="max-height: 100%; max-width: 100%; object-fit: contain; border-radius: 6px;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; font-size: 55px; margin: 10px 0; height: 95px;'>{emoji_fallback}</h1>", unsafe_allow_html=True)
        
        # O botão do Streamlit que age como título da categoria
        if st.button(titulo, key=f"btn_{chave_modulo}", use_container_width=True):
            st.session_state['modulo_ativo'] = chave_modulo
            st.rerun()
            
        st.markdown(f"<p style='text-align:center; color:#7d8590; font-size:11px; margin-top:4px; margin-bottom:0px;'>{subtitulo}</p>", unsafe_allow_html=True)

def renderizar_dashboard():
    # Cabeçalho Azul com a Logo
    logo_src = imagem_para_b64("passaro_logo.png")
    img_tag = f'<img src="{logo_src}" width="40" style="margin-right: 15px;">' if logo_src else '📦 '
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #092c42 0%, #041421 100%); padding: 15px 25px; border-radius: 10px; border: 1px solid #134f75; display: flex; align-items: center; margin-bottom: 20px;">
        {img_tag}
        <h2 style="margin: 0; color: #e6edf3; font-size: 22px; font-weight: 700;">Gestão Pedidos - Molicenter</h2>
    </div>
    """, unsafe_allow_html=True)

    # --- LINHA 1 ---
    titulo_secao("🥬", "SETOR HORTIFRUTI (FLV)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: criar_card("Folhagem", "Seg a Sáb até 12:00hrs", IMG_FOLHAGEM, "🥬", "flv_folhagem")
    with c2: criar_card("FLV Normal", "Terças e Quintas", IMG_FLV, "🍎", "flv_normal")
    with c3: criar_card("FLV Ofertas", "Quintas-feiras", IMG_FLV, "🏷️", "flv_ofertas")
    with c4: criar_card("FLV Oriental", "Quintas-feiras", IMG_ORIENTAL, "🍣", "flv_oriental")

    # --- LINHA 2 ---
    titulo_secao("🥩", "SETOR AÇOUGUE E AVES")
    c1, c2, c3, _ = st.columns(4)
    with c1: criar_card("Pioneiro + BF + Paraná", "Seg a Sex até 11:00hrs", "Pioneiros.jpg", "🍗", "acougue_especiais")
    with c2: criar_card("Açougue Adriano", "Qua e Sáb até 15:00hrs", IMG_ACOUGUE, "🔪", "acougue_total")
    with c3: criar_card("Peças Açougue - Manoel", "Ter, Qui e Sáb", "img_manoel.jpg", "🥩", "acougue_pecas")

    # --- LINHA 3 ---
    titulo_secao("📦", "OUTROS SETORES E LOGÍSTICA")
    c1, c2, c3, _ = st.columns(4)
    with c1: criar_card("Embalagens", "Sexta-feira até 17:30hrs", "Embalagens.jpg", "🥡", "embalagem")
    with c2: criar_card("Padaria e Confeitaria", "Sábado", IMG_PADARIA, "🥖", "padaria_confeitaria")
    with c3: criar_card("Matéria Prima", "Até Sábado", "materiaprima.jpg", "🌾", "materia_prima")

# ─────────────────────────────────────────────────────────────────────────────
# 7. ROTEADOR DE TELAS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state['modulo_ativo'] == 'Home':
    renderizar_dashboard()
else:
    # Barra lateral padrão para navegação de retorno
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

    # Execução do módulo selecionado
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
