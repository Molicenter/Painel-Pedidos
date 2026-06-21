import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO DA PÁGINA (Única para todo o portal)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gestão Pedidos - Molicenter",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed" # Começa fechado para dar foco no Dashboard
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. IMPORTAÇÃO DOS MÓDULOS (Certifique-se de ter trocado - por _)
# ─────────────────────────────────────────────────────────────────────────────
# Descomente as linhas abaixo conforme for subindo os arquivos ajustados
# import flv_folhagem
# import flv_normal
# import flv_ofertas
# import flv_oriental
# import acougue_total
# import acougue_especiais
# import acougue_pecas
# import embalagem
# import padaria_confeitaria
# import materia_prima

# ─────────────────────────────────────────────────────────────────────────────
# 3. VARIÁVEIS DE SESSÃO
# ─────────────────────────────────────────────────────────────────────────────
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

# Esta variável controla qual tela está aberta (Dashboard ou um Pedido específico)
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
            
            # Ajuste a lista de lojas conforme sua necessidade
            usuarios_permitidos = ["Selecione...", "Administrador", "Loja 01", "Loja 02"] 
            usuario_selecionado = st.selectbox("👤 Usuário de acesso:", usuarios_permitidos)
            senha_digitada = st.text_input("🔑 Senha de acesso:", type="password", autocomplete="off")
            st.write("<br>", unsafe_allow_html=True)

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
                # Substitua por sua lógica de senha
                if usuario_selecionado != "Selecione..." and senha_digitada != "":
                    st.session_state['usuario_logado'] = usuario_selecionado
                    st.rerun()
                else:
                    st.error("⚠️ Preencha os dados corretamente.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# 5. FUNÇÃO PARA CRIAR OS CARDS DO DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def criar_card(titulo, subtitulo, nome_imagem, emoji_fallback, chave_modulo):
    """Cria um card visual padronizado para o menu"""
    with st.container(border=True):
        # Tenta carregar a imagem. Se não achar, usa um Emoji.
        try:
            st.image(nome_imagem, use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; font-size: 60px; margin: 20px 0;'>{emoji_fallback}</h1>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:0px; font-size:16px;'>{titulo}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:gray; font-size:12px;'>{subtitulo}</p>", unsafe_allow_html=True)
        
        # O botão que muda a tela
        if st.button("Acessar", key=f"btn_{chave_modulo}", use_container_width=True):
            st.session_state['modulo_ativo'] = chave_modulo
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 6. EXIBIÇÃO DO DASHBOARD (VITRINE DE APLICATIVOS)
# ─────────────────────────────────────────────────────────────────────────────
def renderizar_dashboard():
    st.markdown("### 🦆 Gestão Pedidos - Molicenter")
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
    with c1: criar_card("Pioneiro + BF + Paraná", "Seg a Sex até 11:00hrs", "Pioneiros.jpg", "🍗", "acougue_total")
    with c2: criar_card("Açougue Adriano", "Qua e Sáb até 15:00hrs", "img_adriano.jpg", "🔪", "acougue_especiais")
    with c3: criar_card("Peças Açougue - Manoel", "Ter, Qui e Sáb", "img_manoel.jpg", "🥩", "acougue_pecas")

    st.write("<br>", unsafe_allow_html=True)
    
    st.markdown("#### 📦 OUTROS SETORES E LOGÍSTICA")
    c1, c2, c3, _ = st.columns(4)
    with c1: criar_card("Embalagens", "Sexta-feira até 17:30hrs", "Embalagens.jpg", "🥡", "embalagem")
    with c2: criar_card("Padaria e Confeitaria", "Sábado", "img_padaria.jpg", "🥖", "padaria_confeitaria")
    with c3: criar_card("Matéria Prima", "Até Sábado", "materiaprima.jpg", "🌾", "materia_prima")


# ─────────────────────────────────────────────────────────────────────────────
# 7. ROTEADOR MASTER E MENU LATERAL
# ─────────────────────────────────────────────────────────────────────────────

# Se o usuário está na Home, exibe a Vitrine
if st.session_state['modulo_ativo'] == 'Home':
    renderizar_dashboard()

# Se clicou em algum módulo, carrega o arquivo Python correspondente
else:
    # ── BOTÃO DE VOLTAR NA BARRA LATERAL ──
    with st.sidebar:
        st.write(f"👤 Logado como: **{st.session_state['usuario_logado']}**")
        st.divider()
        if st.button("⬅️ Voltar ao Painel Central", use_container_width=True, type="primary"):
            st.session_state['modulo_ativo'] = 'Home'
            st.rerun()
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state['usuario_logado'] = None
            st.session_state['modulo_ativo'] = 'Home'
            st.rerun()

    # ── CHAMADA DOS MÓDULOS ──
    # Exemplo: chamando a função que inicia a tela dentro do seu arquivo.
    # Note que aqui estou supondo que a função principal de cada arquivo se chama "iniciar_tela()"
    
    if st.session_state['modulo_ativo'] == 'flv_folhagem':
        # flv_folhagem.iniciar_tela()
        st.info("🥬 Módulo de Folhagem em construção... (Descomente o import e a chamada no main.py)")
        
    elif st.session_state['modulo_ativo'] == 'flv_normal':
        # flv_normal.iniciar_tela()
        st.info("🍎 Módulo FLV Normal em construção...")
        
    elif st.session_state['modulo_ativo'] == 'embalagem':
        # embalagem.iniciar_tela()
        st.info("📦 Módulo de Embalagens em construção...")
        
    # (Adicione os elif para os outros módulos conforme for importando...)
    else:
        st.warning("Módulo não encontrado ou ainda não configurado.")
