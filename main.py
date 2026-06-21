import streamlit as st

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
# 2. IMPORTAÇÃO DOS MÓDULOS (Ajustados com underline _)
# ─────────────────────────────────────────────────────────────────────────────
import flv_folhagem

# Descomente as linhas abaixo conforme for ajustando os outros ficheiros:
import flv_normal
import flv_ofertas
import flv_oriental
import acougue_total
import acougue_especiais
import acougue_pecas
#import embalagem
#import padaria_confeitaria
#import materia_prima

# ─────────────────────────────────────────────────────────────────────────────
# 3. VARIÁVEIS DE SESSÃO GLOBAIS
# ─────────────────────────────────────────────────────────────────────────────
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

if 'modulo_ativo' not in st.session_state:
    st.session_state['modulo_ativo'] = 'Home'

# ─────────────────────────────────────────────────────────────────────────────
# 4. TELA DE LOGIN ÚNICA DO PORTAL
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
# 5. FUNÇÃO PARA GERAR A VITRINE DE CARDS (DASHBOARD)
# ─────────────────────────────────────────────────────────────────────────────
def criar_card(titulo, subtitulo, nome_imagem, emoji_fallback, chave_modulo):
    with st.container(border=True):
        try:
            st.image(nome_imagem, use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; font-size: 50px; margin: 10px 0;'>{emoji_fallback}</h1>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:0px; font-size:16px;'>{titulo}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:gray; font-size:12px;'>{subtitulo}</p>", unsafe_allow_html=True)
        
        if st.button("Acessar", key=f"btn_{chave_modulo}", use_container_width=True):
            st.session_state['modulo_ativo'] = chave_modulo
            st.rerun()

def renderizar_dashboard():
    st.markdown("### 📦 Gestão Pedidos - Molicenter")
    st.divider()

    st.markdown("#### 🥬 SETOR HORTIFRUTI (FLV)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: criar_card("Folhagem", "Seg a Sáb até 12:00hrs", "img_folhagem.jpg", "🥬", "flv_folhagem")
    with c2: criar_card("FLV Normal", "Terças e Quintas", "img_flv_normal.jpg", "🍎", "flv_normal")
    with c3: criar_card("FLV Ofertas", "Quintas-feiras", "img_flv_ofertas.jpg", "🏷️", "flv_ofertas")
    with c4: criar_card("FLV Oriental", "Quintas-feiras", "img_flv_oriental.jpg", "🍣", "flv_oriental")

    st.write("<br>", unsafe_allow_html=True)
    
    st.markdown("#### 🥩 SETOR AÇOUGUE E AVES")
    c1, c2, c3, _ = st.columns(4)
    # Trocámos a chave do Pioneiro para "acougue_especiais"
    with c1: criar_card("Pioneiro + BF + Paraná", "Seg a Sex até 11:00hrs", "Pioneiros.jpg", "🍗", "acougue_especiais")
    # Colocámos a chave "acougue_total" no Adriano (ajuste depois se for o contrário)
    with c2: criar_card("Açougue Adriano", "Qua e Sáb até 15:00hrs", "img_adriano.jpg", "🔪", "acougue_total")
    with c3: criar_card("Peças Açougue - Manoel", "Ter, Qui e Sáb", "img_manoel.jpg", "🥩", "acougue_pecas")

    st.write("<br>", unsafe_allow_html=True)
    
    st.markdown("#### 📦 OUTROS SETORES E LOGÍSTICA")
    c1, c2, c3, _ = st.columns(4)
    with c1: criar_card("Embalagens", "Sexta-feira até 17:30hrs", "Embalagens.jpg", "🥡", "embalagem")
    with c2: criar_card("Padaria e Confeitaria", "Sábado", "img_padaria.jpg", "🥖", "padaria_confeitaria")
    with c3: criar_card("Matéria Prima", "Até Sábado", "materiaprima.jpg", "🌾", "materia_prima")

# ─────────────────────────────────────────────────────────────────────────────
# 6. ROTEADOR DE TELAS
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
    
    elif st.session_state['modulo_ativo'] == 'acougue_especiais':
        acougue_especiais.iniciar_tela()

    elif st.session_state['modulo_ativo'] == 'acougue_total':
        acougue_total.iniciar_tela()

    elif st.session_state['modulo_ativo'] == 'acougue_pecas':
        acougue_pecas.iniciar_tela()
        
    elif st.session_state['modulo_ativo'] == 'flv_normal':
        st.info("🍎 Módulo FLV Normal em construção...")
