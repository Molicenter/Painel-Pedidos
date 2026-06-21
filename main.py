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

# ─────────────────────────────────────────────────────────────────────────────
# 5. CSS AVANÇADO (VISUAL COMPACTO E BOTÕES BRANCOS)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base do Tema ── */
.stApp, .main {
    background-color: #0a0a0a !important;
    color: #ffffff !important;
}

/* ── Controle de Largura, Espaços e Zoom (Simula 80%/67% do navegador) ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 98% !important;
    zoom: 0.85; /* Reduz a escala de toda a página para caber sem rolar */
}

/* Ocultar Menu e Cabeçalho Nativo do Streamlit */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* ── Banner Superior Azul Escuro ── */
.banner-container {
    background: linear-gradient(135deg, #07263b 0%, #0e4a74 100%);
    padding: 10px 24px;
    border-radius: 10px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 4px 15px rgba(0, 147, 233, 0.15);
    border: 1px solid rgba(255,255,255,0.1);
}
.banner-logo {
    height: 35px;
    width: auto;
    object-fit: contain;
}
.banner-title {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #fff;
    letter-spacing: 0.5px;
}

/* ── Container do Card do Dashboard ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(30, 30, 30, 0.6) !important;
    backdrop-filter: blur(8px) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 20px rgba(0, 147, 233, 0.25) !important;
    border-color: rgba(0, 147, 233, 0.5) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 10px !important; /* Espaçamento interno mais justo */
    gap: 6px !important;
}

/* ── Imagem do Card (Altura Reduzida) ── */
.card-img-container {
    width: 100%;
    height: 90px; /* Reduzido para caber mais conteúdo na tela */
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 2px;
    background-color: #1a1a1a;
}
.card-img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.9;
    transition: opacity 0.3s;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover .card-img-container img {
    opacity: 1.0;
}

/* ── Botões Brancos de Título (Forçando a cor nas letras) ── */
div[data-testid="stVerticalBlockBorderWrapper"] button {
    background-color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    width: 100% !important;
    min-height: 35px !important;
    padding: 4px 10px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] button p {
    color: #000000 !important; /* Força o texto do botão a ser preto */
    font-weight: 800 !important;
    font-size: 14px !important;
    margin: 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
    background-color: #e6e6e6 !important;
    transform: translateY(-1px);
}

/* ── Formatação de Texto de Horários ── */
.texto-horario {
    font-size: 11px;
    color: #a1a1aa;
    line-height: 1.3;
    font-weight: 500;
    min-height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-top: 2px;
}

/* ── Títulos das Linhas (Setores) ── */
.linha-titulo-sec {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #5cb3e6;
    margin-bottom: 8px;
    margin-top: 15px;
    font-weight: 700;
    border-left: 3px solid #1f8bbf;
    padding-left: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 6. TELA DE LOGIN ÚNICA DO PORTAL
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state['usuario_logado'] is None:
    st.write("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            st.markdown("""
                <div style='text-align:center;'>
                    <h2 style='margin-bottom:0; color:white;'>Portal de Pedidos</h2>
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
# 7. FUNÇÕES PARA GERAR A VITRINE DE CARDS (DASHBOARD)
# ─────────────────────────────────────────────────────────────────────────────
def criar_card(titulo, subtitulo, caminho_imagem, emoji_fallback, chave_modulo):
    img_src = imagem_para_b64(caminho_imagem)
    
    with st.container(border=True):
        if img_src:
            st.markdown(f"""
            <div class="card-img-container">
                <img src="{img_src}">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card-img-container" style="display:flex; justify-content:center; align-items:center;">
                <span style="font-size: 35px;">{emoji_fallback}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Botão branco com texto preto forçado pelo CSS
        if st.button(titulo, key=f"btn_{chave_modulo}", use_container_width=True):
            st.session_state['modulo_ativo'] = chave_modulo
            st.rerun()
            
        st.markdown(f'<div class="texto-horario">{subtitulo}</div>', unsafe_allow_html=True)

def renderizar_dashboard():
    # Banner Principal
    logo_src = imagem_para_b64("passaro_logo.png")
    img_tag = f'<img src="{logo_src}" class="banner-logo" alt="Logo">' if logo_src else '<span style="font-size:24px">🛒</span>'
    
    st.markdown(f"""
    <div class="banner-container">
        {img_tag}
        <div class="banner-title">Gestão Pedidos - Molicenter</div>
    </div>
    """, unsafe_allow_html=True)

    # --- LINHA 1 ---
    st.markdown('<div class="linha-titulo-sec">🥬 Setor Hortifruti (FLV)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: criar_card("Folhagem", "Seg a Sáb até 12:00hrs", IMG_FOLHAGEM, "🥬", "flv_folhagem")
    with c2: criar_card("FLV Normal", "Terças-feira até 17:00hrs<br>Quintas-feira até 14:00hrs", IMG_FLV, "🍎", "flv_normal")
    with c3: criar_card("FLV Ofertas", "Quintas-feiras até 14:00hrs", IMG_FLV, "🏷️", "flv_ofertas")
    with c4: criar_card("FLV Oriental", "Quintas-feiras até 14:00hrs", IMG_ORIENTAL, "🍣", "flv_oriental")

    # --- LINHA 2 ---
    st.markdown('<div class="linha-titulo-sec">🥩 Setor Açougue e Aves</div>', unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns(4, gap="medium")
    with c1: criar_card("Pioneiro + BF + Paraná", "Seg a Sex até 11:00hrs", "Pioneiros.jpg", "🍗", "acougue_especiais")
    with c2: criar_card("Açougue Adriano", "Quartas-feira até 15:00hrs<br>Sábado até 15:00hrs", IMG_ACOUGUE, "🔪", "acougue_total")
    with c3: criar_card("Peças Açougue - Manoel", "Seg/Qua/Sex - Arap. 15:00h<br>Ter/Qui/Sáb - Maringá 15:00h", "img_manoel.jpg", "🥩", "acougue_pecas")

    # --- LINHA 3 ---
    st.markdown('<div class="linha-titulo-sec">📦 Outros Setores e Logística</div>', unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns(4, gap="medium")
    with c1: criar_card("Embalagens", "Sexta-feira até as 17:30hrs", "Embalagens.jpg", "🥡", "embalagem")
    with c2: criar_card("Padaria e Confeitaria", "Sábado", IMG_PADARIA, "🥖", "padaria_confeitaria")
    with c3: criar_card("Matéria Prima", "Até Sábado", "materiaprima.jpg", "🌾", "materia_prima")

# ─────────────────────────────────────────────────────────────────────────────
# 8. ROTEADOR DE TELAS
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
