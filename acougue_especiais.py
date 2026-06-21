import streamlit as st
import pandas as pd
import io
import requests
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# ─────────────────────────────────────────────
# IMPORTAÇÕES PARA ESTILIZAÇÃO DO EXCEL
# ─────────────────────────────────────────────
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Gestão de Pedidos - Açougue Especial",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
# ─────────────────────────────────────────────
if 'reset_counter_acougue_especial' not in st.session_state:
    st.session_state['reset_counter_acougue_especial'] = 0

if 'usuario_logado_acougue_especial' not in st.session_state:
    st.session_state['usuario_logado_acougue_especial'] = None

# ─────────────────────────────────────────────
# CSS GLOBAL E DE IMPRESSÃO (PALETA VERMELHA)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;700&display=swap');

:root {
    --bg-main:        #0d1117;
    --bg-card:        #161b22;
    --bg-sidebar:     #0d1117;
    --red-dark:       #3a1010;
    --red-mid:        #6b1d1d;
    --red-accent:     #b32d2d;
    --red-bright:     #e63939;
    --red-glow:       rgba(179, 45, 45, .25);
    --text-primary:   #e6edf3;
    --text-muted:     #7d8590;
    --text-header:    #ffcccc;
    --border:         #21262d;
    --border-active:  #b32d2d;
    --row-hover:      rgba(179, 45, 45, .08);
    --row-selected:   rgba(179, 45, 45, .18);
}

.stApp, .main { background-color: var(--bg-main) !important; color: var(--text-primary) !important; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif !important; }
section[data-testid="stSidebar"] { background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 14px; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--red-mid) 0%, var(--red-accent) 100%) !important;
    color: #fff !important;
    border: 1px solid var(--red-accent) !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: .3px;
    transition: all .2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 18px var(--red-glow) !important;
}
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    transition: all .2s ease !important;
}
.stButton > button:hover {
    border-color: var(--red-accent) !important;
    color: var(--red-bright) !important;
    transform: translateY(-1px) !important;
}
.stTextInput input, .stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
.stTextInput input:focus, .stSelectbox > div > div:focus-within {
    border-color: var(--red-accent) !important;
    box-shadow: 0 0 0 3px var(--red-glow) !important;
}
.title-input input {
    font-weight: 700 !important;
    font-size: 16px !important;
    color: var(--red-bright) !important;
    padding: 2px 8px !important;
    background: transparent !important;
    border: 1px dashed #21262d !important;
}
.title-input input:focus { border: 1px dashed var(--red-accent) !important; }

[data-testid="stDataEditor"] [data-testid="glideDataEditor"] .gdg-header-cell,
[data-testid="stDataEditor"] .dvn-stack .gdg-header {
    background-color: var(--red-dark) !important;
    color: var(--text-header) !important;
}

[data-testid="stDataEditor"] {
    border-radius: 10px !important;
    overflow: hidden;
    border: 1px solid var(--red-mid) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,.4);
    font-size: 12px !important;
}
[data-testid="stDataEditor"] .gdg-cell.gdg-selected,
[data-testid="stDataEditor"] .gdg-cell[data-state="focused"],
[data-testid="stDataEditor"] .gdg-cell[aria-selected="true"] {
    background-color: var(--row-selected) !important;
    outline: 2px solid var(--red-accent) !important;
    outline-offset: -2px;
}
[data-testid="stDataEditor"] .gdg-row:hover .gdg-cell { background-color: var(--row-hover) !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    transition: box-shadow .25s ease, border-color .25s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--red-mid) !important;
    box-shadow: 0 6px 24px rgba(0,0,0,.35) !important;
}
[data-testid="stMetric"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 10px;
}
[data-testid="stMetricValue"] { color: var(--red-bright) !important; font-weight: 700; font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; }

.topbar-loja {
    background: linear-gradient(90deg, var(--red-dark) 0%, #1a0808 100%);
    border: 1px solid var(--red-mid);
    border-radius: 10px;
    padding: 10px 18px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-title { font-size: 18px; font-weight: 700; color: var(--text-header); }
.topbar-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.erp-badge { background-color: #2ea043; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 600; margin-left: 8px;}

/* IMPRESSÃO */
@media print {
    @page { size: A4 portrait; margin: 8mm 8mm; }

    /* Ajustes para evitar o espaço em branco gigante na quebra de página */
    .main .block-container { padding-top: 0 !important; margin-top: 0 !important; max-width: 100% !important; }
    h3 { page-break-after: avoid !important; break-after: avoid !important; }

    .stApp, .main, body, html {
        background-color: #ffffff !important;
        background-image: none !important;
        color: #000000 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    header, [data-testid="stSidebar"], [data-testid="stHeader"] { display: none !important; }
    [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"],
    div[data-testid="stVerticalBlockBorderWrapper"] { display: none !important; }
    [data-testid="stElementContainer"]:has(#print-section) {
        display: block !important; width: 100% !important;
    }
    #print-section { display: block !important; width: 100% !important; }
    #print-section h2 {
        font-size: 13px !important;
        margin: 0 0 6px 0 !important;
        padding-bottom: 3px !important;
        border-bottom: 2px solid #000 !important;
        color: #000 !important;
        display: block !important;
        text-align: center !important;
    }
    #print-section h3 {
        font-size: 10px !important;
        font-weight: 700 !important;
        border-bottom: none !important;
        margin-top: 12px !important;
        margin-bottom: 3px !important;
        color: #000 !important;
    }
    .print-container { width: 100% !important; display: block !important; }

    table.print-table {
        width: 100% !important;
        border-collapse: collapse !important;
        color: #000000 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        line-height: 1.2 !important;
        display: table !important;
        table-layout: fixed !important;
        margin-bottom: 4px !important;
    }
    table.print-table th, table.print-table td {
        border: 1px solid #444 !important;
        padding: 2px 3px !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    table.print-table td { white-space: nowrap !important; }
    table.print-table th {
        background-color: #d5d5d5 !important;
        font-weight: bold !important;
        text-align: center !important;
        white-space: normal !important;
        word-break: break-word !important;
        vertical-align: middle !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    table.print-table tr { break-inside: avoid !important; page-break-inside: avoid !important; }

    /* Ajuste para 6 colunas na visão de loja */
    table.print-loja { font-size: 10px !important; }
    table.print-loja th:nth-child(1), table.print-loja td:nth-child(1) { width: 12% !important; text-align: left !important; }
    table.print-loja th:nth-child(2), table.print-loja td:nth-child(2) { width: 8% !important; text-align: center !important; }
    table.print-loja th:nth-child(3), table.print-loja td:nth-child(3) { width: 40% !important; text-align: left !important; }
    table.print-loja th:nth-child(4), table.print-loja td:nth-child(4) { width: 12% !important; text-align: center !important; }
    table.print-loja th:nth-child(5), table.print-loja td:nth-child(5) { width: 12% !important; text-align: center !important; }
    table.print-loja th:nth-child(6), table.print-loja td:nth-child(6) {
        width: 16% !important; text-align: center !important;
        font-weight: bold !important; background-color: #eeeeee !important;
        -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    }

    table.print-forn { font-size: 7.5px !important; }
    table.print-forn th:nth-child(1), table.print-forn td:nth-child(1) { width: 7% !important; text-align: center !important; }
    table.print-forn th:nth-child(2), table.print-forn td:nth-child(2) { width: 29% !important; text-align: left !important; }
    table.print-forn th:nth-child(n+3):nth-child(-n+10),
    table.print-forn td:nth-child(n+3):nth-child(-n+10) { width: 6.5% !important; text-align: center !important; }
    table.print-forn th:nth-child(11), table.print-forn td:nth-child(11) {
        width: 8% !important; text-align: center !important;
        font-weight: bold !important; background-color: #eeeeee !important;
        -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    }

    table.print-sep { font-size: 9px !important; }
    table.print-sep th:nth-child(1), table.print-sep td:nth-child(1) { width: 11% !important; text-align: left !important; }
    table.print-sep th:nth-child(2), table.print-sep td:nth-child(2) { width: 7%  !important; text-align: center !important; }
    table.print-sep th:nth-child(3), table.print-sep td:nth-child(3) { width: 26% !important; text-align: left !important; }
    table.print-sep th:nth-child(n+4):nth-child(-n+11),
    table.print-sep td:nth-child(n+4):nth-child(-n+11) { width: 6% !important; text-align: center !important; }
    table.print-sep th:nth-child(12), table.print-sep td:nth-child(12) {
        width: 7% !important; text-align: center !important;
        font-weight: bold !important; background-color: #eeeeee !important;
        -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    }
}

@media screen {
    #print-section { display: none !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES E PRODUTOS INICIAIS DA MATRIZ
# ─────────────────────────────────────────────
LOJAS = ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06", "Loja 07", "Loja 08"]
MAPA_LOJAS = {l: l for l in LOJAS}

produtos_iniciais = [
    {"Fornecedor": "PIONEIRO", "Código": 655527, "Descrição Oficial": "Coracao Frango 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655518, "Descrição Oficial": "Coxa Frango 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655509, "Descrição Oficial": "Coxa Sobrecoxa 500g Pioneiro S/Osso S/Pele Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655590, "Descrição Oficial": "Coxinha Asa 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655493, "Descrição Oficial": "Figado Frango 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655350, "Descrição Oficial": "File Peito 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655369, "Descrição Oficial": "File Sassami 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655606, "Descrição Oficial": "Frango Passarinho 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655341, "Descrição Oficial": "Meio Asa 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655332, "Descrição Oficial": "Moela Frango 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "PIONEIRO", "Código": 655323, "Descrição Oficial": "Sobrecoxa 500g Pioneiro Bdj Resf", "Nome Personalizado": ""},
    {"Fornecedor": "FRANGO PARANÁ", "Código": 139773, "Descrição Oficial": "Pe Frango Kg Bdj", "Nome Personalizado": ""},
    {"Fornecedor": "FRANGO PARANÁ", "Código": 140982, "Descrição Oficial": "Dorso Kg", "Nome Personalizado": ""},
    {"Fornecedor": "FRANGO PARANÁ", "Código": 379043, "Descrição Oficial": "Peito Frango Kg Parana", "Nome Personalizado": ""},
    {"Fornecedor": "FRANGO PARANÁ", "Código": 82679,  "Descrição Oficial": "Frango Kg Parana", "Nome Personalizado": ""},
    {"Fornecedor": "FRANGO PARANÁ", "Código": 526748, "Descrição Oficial": "Pescoco Frango Kg", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - TEMPERADOS", "Código": 48323,  "Descrição Oficial": "Coxinha Asa Temp Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - TEMPERADOS", "Código": 20350,  "Descrição Oficial": "Frango Pass Temp Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - TEMPERADOS", "Código": 48330,  "Descrição Oficial": "Meio Asa Temp Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - TEMPERADOS", "Código": 168951, "Descrição Oficial": "Sobrecoxa Temp Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352259, "Descrição Oficial": "Coxa Frango Kg Big Band Padrao Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352161, "Descrição Oficial": "Coxa Sobrecoxa Kg Big Band Padrao Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352213, "Descrição Oficial": "Coxinha Asa Kg Big Band Padrao Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352204, "Descrição Oficial": "File Peito Kg Big Band Padrao Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352240, "Descrição Oficial": "File Sassami Kg Big Band Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352189, "Descrição Oficial": "Meio Asa Kg Big Band Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352268, "Descrição Oficial": "Moela Kg Big Band Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352222, "Descrição Oficial": "Peito Frango Kg Big Band Padrao Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BANDEJAS", "Código": 352170, "Descrição Oficial": "Sobrecoxa Kg Big Band Padrao Resf", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BALCÃO", "Código": 75305, "Descrição Oficial": "Coxa Sobrecoxa Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BALCÃO", "Código": 18005, "Descrição Oficial": "Coxinha Asa Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX BALCÃO", "Código": 75343, "Descrição Oficial": "File Peito Kg Big", "Nome Personalizado": ""},
    {"Fornecedor": "BIG FRANGO - MIX CONGELADO", "Código": 548236, "Descrição Oficial": "Sambiquira Frango 1kg Big Frango", "Nome Personalizado": ""},
]

# ─────────────────────────────────────────────
# FUNÇÃO DE ESTILIZAÇÃO DE EXCEL COM CORES
# ─────────────────────────────────────────────
def gerar_excel_estilizado(df, sheet_name="Resumo"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]

        # Estilos com as cores do App
        header_fill = PatternFill(start_color='6B1D1D', end_color='6B1D1D', fill_type='solid') # Vermelho Escuro
        alt_row_fill = PatternFill(start_color='F9F2F2', end_color='F9F2F2', fill_type='solid') # Fundo alternado
        header_font = Font(color='FFFFFF', bold=True)
        border_style = Border(
            left=Side(style='thin', color='CCCCCC'),
            right=Side(style='thin', color='CCCCCC'),
            top=Side(style='thin', color='CCCCCC'),
            bottom=Side(style='thin', color='CCCCCC')
        )

        for row_idx, row in enumerate(worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column)):
            for cell in row:
                cell.border = border_style
                if row_idx == 0:
                    # Formata o Cabeçalho
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    # Fundo alternado para as linhas
                    if row_idx % 2 == 0:
                        cell.fill = alt_row_fill
                    
                    # Alinhamento dinâmico: Centraliza números e deixa textos à esquerda
                    if isinstance(cell.value, (int, float)):
                        cell.alignment = Alignment(horizontal='center', vertical='center')
                    else:
                        cell.alignment = Alignment(horizontal='left', vertical='center')

        # Autoajuste de largura das colunas
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            worksheet.column_dimensions[col_letter].width = max_length + 2

        # 🖨️ CONFIGURAÇÃO AUTOMÁTICA DE IMPRESSÃO
        worksheet.sheet_properties.pageSetUpPr.fitToPage = True
        worksheet.page_setup.fitToWidth = 1
        worksheet.page_setup.fitToHeight = False
        worksheet.page_setup.orientation = worksheet.ORIENTATION_LANDSCAPE
        worksheet.page_margins.left = 0.25
        worksheet.page_margins.right = 0.25
        worksheet.page_margins.top = 0.75
        worksheet.page_margins.bottom = 0.75

    return buffer.getvalue()

# ─────────────────────────────────────────────
# CONEXÃO GOOGLE SHEETS & FUNÇÕES DE DADOS
# ─────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

WS_PRODUTOS = "AcEspeciais_Produtos"
WS_PEDIDOS  = "AcEspeciais_Pecas"
WS_MEDIA_90D = "AcEspeciais_90d"  # NOVO ABA MÉDIA 90D

def parse_bool(x):
    if isinstance(x, bool): return x
    if isinstance(x, (int, float)): return bool(x) and not pd.isna(x)
    return str(x).strip().upper() in ['TRUE', 'VERDADEIRO', '1', 'V', 'SIM', 'YES', 'T', 'X']

def notificar_telegram(mensagem):
    try:
        bot_token = st.secrets["telegram"]["bot_token"]
        chat_id = st.secrets["telegram"]["chat_id"]
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensagem}
        resposta = requests.post(url, json=payload)
        return resposta.status_code == 200
    except KeyError:
        st.error("⚠️ Credenciais do Telegram não configuradas no secrets.toml.")
        return False
    except Exception as e:
        st.error(f"⚠️ Erro de conexão ao enviar o Telegram: {e}")
        return False

@st.cache_data(ttl=15)
def carregar_catalogo_acougue():
    try:
        df = conn.read(worksheet=WS_PRODUTOS, ttl=0, usecols=list(range(20)))
    except ValueError as e:
        if "Spreadsheet must be specified" in str(e):
            st.error("🚨 **Erro Crítico:** URL da Planilha não especificada nas configurações do Streamlit Cloud (Secrets).")
            st.info("No painel do Streamlit, vá em **App settings > Secrets** e adicione o bloco correspondente.")
            st.stop()
        else:
            raise e
    except Exception as e:
        st.error(f"Erro ao conectar na aba {WS_PRODUTOS}: {e}")
        st.stop()

    if df.empty or "Fornecedor" not in df.columns:
        df_init = pd.DataFrame(produtos_iniciais)
        for loja in LOJAS: df_init[loja] = True
        conn.update(worksheet=WS_PRODUTOS, data=df_init)
        df = df_init.copy()

    need_update = False

    if "Descrição" in df.columns and "Descrição Oficial" not in df.columns:
        df = df.rename(columns={"Descrição": "Descrição Oficial"})
        need_update = True

    if "Nome Personalizado" not in df.columns:
        df["Nome Personalizado"] = ""
        need_update = True

    if need_update:
        conn.update(worksheet=WS_PRODUTOS, data=df.drop(columns=["Descrição"], errors="ignore"))

    novas_colunas = {}
    for col in df.columns:
        col_str = str(col).strip()
        for loja in LOJAS:
            if loja.lower() in col_str.lower():
                novas_colunas[col] = loja
    df = df.rename(columns=novas_colunas)

    for loja in LOJAS:
        if loja not in df.columns:
            df[loja] = False
        else:
            df[loja] = df[loja].apply(parse_bool)

    if "Código" in df.columns:
        df["Código"] = pd.to_numeric(df["Código"], errors='coerce').fillna(0).astype(int)

    def obter_nome_final(row):
        apelido = str(row.get("Nome Personalizado", "")).strip()
        if apelido and apelido.lower() != "nan":
            return apelido
        return str(row.get("Descrição Oficial", "")).strip()

    df["Descrição"] = df.apply(obter_nome_final, axis=1)
    return df

@st.cache_data(ttl=15)
def carregar_pedidos():
    try:
        df_pedidos = conn.read(worksheet=WS_PEDIDOS, ttl=0)
    except ValueError as e:
        if "Spreadsheet must be specified" in str(e):
            st.error("🚨 **Erro Crítico:** URL da Planilha não especificada nas configurações do Streamlit Cloud (Secrets).")
            st.stop()
        else:
            raise e
    except Exception as e:
        st.error(f"Erro ao conectar na aba {WS_PEDIDOS}: {e}")
        st.stop()

    df_cat = carregar_catalogo_acougue()

    if df_pedidos.empty or "Código" not in df_pedidos.columns:
        df_init = df_cat[["Fornecedor", "Código", "Descrição"]].copy()
        for loja in LOJAS:
            df_init[loja] = 0
        if not df_init.empty:
            conn.update(worksheet=WS_PEDIDOS, data=df_init)
        return df_init

    df_pedidos = df_pedidos.drop(columns=["Descrição", "Fornecedor"], errors="ignore")
    df_pedidos = pd.merge(df_cat[["Código", "Fornecedor", "Descrição"]], df_pedidos, on="Código", how="left")

    if "Código" in df_pedidos.columns:
        df_pedidos["Código"] = pd.to_numeric(df_pedidos["Código"], errors='coerce').fillna(0).astype(int)

    for loja in LOJAS:
        if loja in df_pedidos.columns:
            df_pedidos[loja] = pd.to_numeric(df_pedidos[loja], errors='coerce').fillna(0).astype(int)

    return df_pedidos

@st.cache_data(ttl=60)
def carregar_media_90d():
    try:
        df = conn.read(worksheet=WS_MEDIA_90D, ttl=0)
        if df.empty or "codigo" not in df.columns:
            return pd.DataFrame(columns=["loja", "codigo", "qtde_media_semanal"])
        return df
    except Exception as e:
        return pd.DataFrame(columns=["loja", "codigo", "qtde_media_semanal"])

def salvar_pedidos(df_to_save):
    conn.update(worksheet=WS_PEDIDOS, data=df_to_save)
    st.cache_data.clear()

def salvar_catalogo(df_to_save):
    df_clean = df_to_save.drop(columns=["Descrição"], errors="ignore")
    conn.update(worksheet=WS_PRODUTOS, data=df_clean)
    st.cache_data.clear()


# ─────────────────────────────────────────────
# SISTEMA DE LOGIN
# ─────────────────────────────────────────────
if st.session_state['usuario_logado_acougue_especial'] is None:
    st.write("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            h1, h2 = st.columns([4, 1])
            with h1:
                st.markdown("""
                    <h2 style='margin-bottom:0'>Portal de Pedidos</h2>
                    <p style='color:#7d8590;font-size:14px;margin-top:4px'>Açougue Especial — Molicenter</p>
                """, unsafe_allow_html=True)
            with h2:
                st.write("")
                try:
                    st.image("passaro_logo.png", width=60)
                except Exception:
                    st.markdown("🍗", unsafe_allow_html=True)

            st.divider()
            usuarios_permitidos = ["Selecione..."] + ["Administrador"] + LOJAS
            usuario_selecionado = st.selectbox("👤 Usuário de acesso:", usuarios_permitidos)

            senha_digitada = st.text_input("🔑 Senha de acesso:", type="password", autocomplete="off")

            st.write("<br>", unsafe_allow_html=True)

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
                if usuario_selecionado == "Selecione...":
                    st.error("⚠️ Por favor, selecione um usuário.")
                elif usuario_selecionado == "Administrador" and senha_digitada == "moli0000":
                    st.session_state['usuario_logado_acougue_especial'] = usuario_selecionado
                    st.rerun()
                elif usuario_selecionado in LOJAS and senha_digitada == "moli1234":
                    st.session_state['usuario_logado_acougue_especial'] = usuario_selecionado
                    st.rerun()
                elif senha_digitada:
                    st.error("⚠️ Senha incorreta. Tente novamente.")

            st.markdown('<p style="font-size: 11px; color: #7d8590; text-align: center; margin-top: 10px;">🔒 Acesso restrito — Molicenter © 2026</p>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# PÓS-LOGIN
# ─────────────────────────────────────────────
usuario_atual = st.session_state['usuario_logado_acougue_especial']
acesso_total  = usuario_atual == "Administrador"

if not acesso_total:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"]  { display: none !important; }
        .main .block-container { max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("passaro_logo.png", width=72)
    except Exception:
        st.markdown("🍗")

    st.markdown(f"### Olá, *{usuario_atual}*")
    st.caption("Sistema de Pedidos — Açougue Especial")
    st.divider()

    if acesso_total:
        perfil_navegacao = st.radio("📍 Navegação:", [
            "Visão por Fornecedor (Resumo)",
            "Separação e Fechamento",
            "Visão das Lojas",
            "Catálogo de Produtos"
        ])
    else:
        perfil_navegacao = "Visão das Lojas"

    st.divider()

    df_ped = carregar_pedidos()
    if not df_ped.empty and set(LOJAS).issubset(df_ped.columns):
        total_preenchidos = (df_ped[LOJAS] > 0).any(axis=1).sum()
    else:
        total_preenchidos = 0

    st.metric("Itens c/ pedido", total_preenchidos, help="Itens com ao menos 1 quantidade preenchida")

    st.divider()

    if st.button("🔄 Sincronizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.session_state['reset_counter_acougue_especial'] += 1
        st.rerun()

    # -- NOVO BOTÃO DE ATUALIZAR MÉDIA 90D --
    if st.button("📊 Atualizar média 90d", use_container_width=True):
        try:
            conn_pg = st.connection("banco_erp", type="sql")
            query_media = 'SELECT loja, codigo, qtde_media_semanal FROM "python_90dSEMANA"'
            df_media = conn_pg.query(query_media, ttl=0)
            
            if not df_media.empty:
                conn.update(worksheet=WS_MEDIA_90D, data=df_media)
                st.success("✅ Média 90d sincronizada do ERP para o Sheets!")
                st.cache_data.clear()
            else:
                st.warning("Nenhum dado retornado da view.")
        except Exception as e:
            if "No database configured" in str(e) or "missing" in str(e).lower():
                st.error("⚠️ Aviso: As credenciais do banco_erp também precisam estar nos Secrets do Streamlit.")
            else:
                st.error(f"⚠️ Erro ao atualizar média 90d do PostgreSQL: {e}")

    st.write("<br>", unsafe_allow_html=True)

    if st.button("🚪 Sair / Logout", use_container_width=True):
        st.session_state['usuario_logado_acougue_especial'] = None
        st.rerun()

# ─────────────────────────────────────────────
# FUNÇÃO MODAL DE CONFIRMAÇÃO PARA ZERAR
# ─────────────────────────────────────────────
@st.dialog("🚨 Confirmação Necessária")
def modal_zerar_pedidos():
    st.markdown("Tem certeza que deseja **zerar todos os pedidos** de todas as lojas?")
    st.markdown("⚠️ *Esta ação irá zerar as quantidades diretamente no Google Sheets.*")

    st.write("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ Não, cancelar", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("✔️ Sim, zerar tudo", type="primary", use_container_width=True):
            st.session_state['reset_counter_acougue_especial'] += 1
            df_main = carregar_pedidos()
            for loja in LOJAS:
                if loja in df_main.columns:
                    df_main[loja] = 0
            salvar_pedidos(df_main)
            st.rerun()

# ─────────────────────────────────────────────
# ROTA 1 — SEPARAÇÃO E FECHAMENTO (Admin)
# ─────────────────────────────────────────────
if perfil_navegacao == "Separação e Fechamento":
    st.markdown("""
    <div class="page-header hide-print" style="background: linear-gradient(90deg, var(--red-dark) 0%, #1a0808 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 22px;">
        <span style="font-size: 26px; margin-right: 12px;">📊</span>
        <div style="display: inline-block; vertical-align: top;">
            <div style="font-size: 20px; font-weight: 700; color: var(--text-header);">Separação e Fechamento — Açougue Especial</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Consolidado geral de quantidades por Fornecedor e Código</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        df_base = carregar_pedidos()

        if df_base.empty:
            st.warning("A base de pedidos está vazia. Cadastre produtos no Catálogo primeiro.")
            st.stop()

        df_base["TOTAL GERAL"] = df_base[LOJAS].sum(axis=1)

        col_cfg = {
            "Fornecedor":  st.column_config.TextColumn("Fornecedor", disabled=True),
            "Código":      st.column_config.NumberColumn("Cód.", width=80, format="%d", disabled=True),
            "Descrição":   st.column_config.TextColumn("Produto", disabled=True),
            "TOTAL GERAL": st.column_config.NumberColumn("TOTAL ▶️", width=90, format="%d", disabled=True),
        }
        for loja, novo_nome in MAPA_LOJAS.items():
            col_cfg[loja] = st.column_config.NumberColumn(novo_nome, format="%d", min_value=0, step=1)

        cols_order = ["Fornecedor", "Código", "Descrição"] + LOJAS + ["TOTAL GERAL"]
        df_exibir = df_base[cols_order]

        df_editado = st.data_editor(
            df_exibir,
            hide_index=True,
            use_container_width=True,
            height=600,
            column_config=col_cfg,
            key=f"sep_editor_{st.session_state['reset_counter_acougue_especial']}"
        )

        html_table = df_editado.to_html(index=False, classes=["print-table", "print-sep"])
        st.markdown(f"""<div id="print-section">
<h2 style="color: black; margin-bottom: 10px; text-align: center; border-bottom: 2px solid black; padding-bottom: 5px;">
    Visão por Fornecedor (Resumo) — Açougue Especial &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style="font-size: 11px; font-weight: bold; color: #000000;">{agora}</span>
</h2>
<div class="print-container">
{html_print_content}
</div>
</div>""", unsafe_allow_html=True)

        st.divider()
        col_salvar, col_csv, col_excel, col_print, col_zerar = st.columns([2.5, 1.2, 1.2, 1.5, 2.5])

        with col_salvar:
            if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                df_to_save = df_editado.drop(columns=["TOTAL GERAL"])
                salvar_pedidos(df_to_save)
                st.success("✅ Pedidos salvos na nuvem com sucesso!")
                st.rerun()

        with col_csv:
            df_csv = df_editado.copy().rename(columns=MAPA_LOJAS)
            csv = df_csv.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ CSV", data=csv, file_name="separacao_acougue_especial.csv", mime="text/csv", use_container_width=True)

        with col_excel:
            df_exp = df_editado.copy().rename(columns=MAPA_LOJAS)
            excel_data = gerar_excel_estilizado(df_exp, "Separação Acougue")
            st.download_button("⬇️ Excel", data=excel_data, file_name="separacao_acougue_especial.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

        with col_print:
            if st.button("🖨️ Imprimir", use_container_width=True):
                components.html(
                    "<script>"
                    "var s=document.createElement('style');"
                    "s.id='__sep_land__';"
                    "s.innerHTML='@media print{@page{size:A4 landscape!important;margin:6mm 10mm!important;}}';"
                    "window.parent.document.head.appendChild(s);"
                    "window.parent.print();"
                    "setTimeout(function(){"
                    "var e=window.parent.document.getElementById('__sep_land__');"
                    "if(e)e.remove();"
                    "},3000);"
                    "</script>",
                    height=0
                )

        with col_zerar:
            if st.button("🚨 Zerar Todos os Pedidos", use_container_width=True, key="btn_zerar_sep_esp"):
                modal_zerar_pedidos()

# ─────────────────────────────────────────────
# ROTA 2 — VISÃO DAS LOJAS
# ─────────────────────────────────────────────
elif perfil_navegacao == "Visão das Lojas":
    if acesso_total:
        loja_selecionada = st.selectbox("👁️ Visualizar como:", LOJAS)
    else:
        loja_selecionada = usuario_atual

    col_info, col_logout = st.columns([8, 2])
    with col_info:
        id_loja = MAPA_LOJAS.get(loja_selecionada, loja_selecionada)
        st.markdown(f"""
        <div class="topbar-loja hide-print">
            <div class="topbar-left">
                <span style="font-size:22px">🍗</span>
                <div>
                    <div class="topbar-title">{loja_selecionada} — Açougue Especial <span class="erp-badge">🟢 Conectado ao ERP</span></div>
                    <div class="topbar-sub">Preencha a quantidade de cada produto</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sair / Logout", use_container_width=True):
            st.session_state['usuario_logado_acougue_especial'] = None
            st.rerun()

    df_cat = carregar_catalogo_acougue()
    df_cat_loja = df_cat[df_cat[loja_selecionada] == True].copy()

    if df_cat_loja.empty:
        st.warning(f"Nenhum produto habilitado para a {loja_selecionada} no momento.")
        st.stop()

    df_all = carregar_pedidos()
    df_loja_view = pd.merge(
        df_cat_loja[["Fornecedor", "Código", "Descrição"]],
        df_all[["Fornecedor", "Código", loja_selecionada]],
        on=["Fornecedor", "Código"],
        how="left"
    )
    df_loja_view[loja_selecionada] = df_loja_view[loja_selecionada].fillna(0).astype(int)
    df_loja_view = df_loja_view.rename(columns={loja_selecionada: "Qtde"})

    mapa_banco_erp = {
        "Loja 01": "001", "Loja 02": "002", "Loja 03": "003",
        "Loja 04": "004", "Loja 05": "005", "Loja 06": "006",
        "Loja 07": "007", "Loja 08": "008"
    }
    cod_empresa_banco = mapa_banco_erp.get(loja_selecionada, "001")

    # 1. Puxar Estoque do ERP
    try:
        conn_pg = st.connection("banco_erp", type="sql")

        query_erp = f"""
            SELECT cade_codempresa,
                   cade_codigo,
                   cadp_descricao,
                   estoque
            FROM "python_estoque"
            WHERE cade_codempresa::text = '{cod_empresa_banco}'
            ORDER BY cade_codempresa, cade_codigo
        """

        df_erp = conn_pg.query(query_erp, ttl=300)

        if not df_erp.empty:
            df_erp = df_erp.rename(columns={"cade_codigo": "Código", "estoque": "Estoque"})
            df_loja_view = pd.merge(df_loja_view, df_erp[["Código", "Estoque"]], on="Código", how="left")
        else:
            df_loja_view["Estoque"] = 0

    except Exception as e:
        if "No database configured" in str(e) or "missing" in str(e).lower():
             st.error("⚠️ Aviso: As credenciais do banco_erp também precisam estar nos Secrets do Streamlit para puxar o estoque.")
        else:
             st.error(f"⚠️ Erro ao puxar dados do ERP PostgreSQL: {e}")
        df_loja_view["Estoque"] = 0

    # 2. Puxar Média 90d do Google Sheets
    df_media_all = carregar_media_90d()
    if not df_media_all.empty and "loja" in df_media_all.columns:
        # Filtra a média apenas da loja atual
        df_media_loja = df_media_all[df_media_all["loja"].astype(str).str.zfill(3) == cod_empresa_banco].copy()
        df_media_loja = df_media_loja.rename(columns={"codigo": "Código", "qtde_media_semanal": "Média 90d"})
        df_media_loja = df_media_loja.drop_duplicates(subset=["Código"])
        df_media_loja["Código"] = pd.to_numeric(df_media_loja["Código"], errors='coerce').fillna(0).astype(int)
    else:
        df_media_loja = pd.DataFrame(columns=["Código", "Média 90d"])

    df_loja_view = pd.merge(df_loja_view, df_media_loja[["Código", "Média 90d"]], on="Código", how="left")

    # Trata Nulos
    df_loja_view["Estoque"] = df_loja_view["Estoque"].fillna(0).astype(int)
    df_loja_view["Média 90d"] = pd.to_numeric(df_loja_view["Média 90d"], errors='coerce').fillna(0.0).round(2)
    df_loja_view["Qtde"] = df_loja_view["Qtde"].fillna(0).astype(int)
    
    # Ordena colunas
    df_loja_view = df_loja_view[["Fornecedor", "Código", "Descrição", "Estoque", "Média 90d", "Qtde"]]

    with st.container(border=True):
        st.info("💡 **Dica:** O **Estoque** foi preenchido automaticamente com base no sistema ERP. Você pode preencher apenas a **Qtde** do pedido.")

        col_cfg_loja = {
            "Fornecedor": st.column_config.TextColumn("Fornecedor", width=150, disabled=True),
            "Código":     st.column_config.NumberColumn("Cód.", width=80, format="%d", disabled=True),
            "Descrição":  st.column_config.TextColumn("Produto", width=250, disabled=True),
            "Estoque":    st.column_config.NumberColumn("📦 Estoque", width=100, format="%d", disabled=True),
            "Média 90d":  st.column_config.NumberColumn("📊 Média 90d", width=100, format="%.2f", disabled=True),
            "Qtde":       st.column_config.NumberColumn("🛒 Qtde", width=120, min_value=0, step=1),
        }

        with st.container():
            df_editado = st.data_editor(
                df_loja_view,
                column_config=col_cfg_loja,
                hide_index=True,
                use_container_width=True,
                height=520,
                key=f"loja_acougue_especial_{st.session_state['reset_counter_acougue_especial']}"
            )

        df_imprimir = df_editado.copy()
        df_imprimir = df_imprimir.rename(columns={"Estoque": "Est.", "Média 90d": "Méd.90d", "Qtde": "Ped."})
        html_table_loja = df_imprimir.to_html(index=False, classes=["print-table", "print-loja"])

        st.markdown(f"""<div id="print-section">
<h2 style="color: black; margin-bottom: 10px; text-align: center; border-bottom: 2px solid black; padding-bottom: 5px;">
    Resumo do Pedido — {loja_selecionada}
</h2>
<div class="print-container">
{html_table_loja}
</div>
</div>""", unsafe_allow_html=True)

        itens_com_pedido = int((df_editado["Qtde"] > 0).sum())
        total_itens      = len(df_editado)
        total_unidades   = int(df_editado["Qtde"].sum())
        pct              = round(itens_com_pedido / total_itens * 100) if total_itens else 0

        st.divider()
        m1, m2, m3, col_print, col_aviso, col_btn = st.columns([1.5, 1.5, 1.5, 1.3, 2.4, 2.8])
        with m1: st.metric("Itens", f"{itens_com_pedido}/{total_itens}")
        with m2: st.metric("Unidades", total_unidades)
        with m3: st.metric("Cobertura", f"{pct}%")

        with col_print:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🖨️ Imprimir", use_container_width=True):
                components.html("<script>window.parent.print();</script>", height=0)

        with col_aviso:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🚫 Sem Pedido Hoje", use_container_width=True):
                df_main = carregar_pedidos()
                df_main[loja_selecionada] = 0
                salvar_pedidos(df_main)
                
                msg_aviso = f"🚨 *AVISO - Açougue Especial*\nA {loja_selecionada} informou que *NÃO* fará pedido de peças nesta semana."
                enviado = notificar_telegram(msg_aviso)
                
                if enviado:
                    st.success("✅ Supervisor avisado e pedido zerado!")
                else:
                    st.warning("⚠️ O pedido foi zerado, mas falhou ao enviar o Telegram (verifique as credenciais no Secrets).")

        with col_btn:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Pedido da Semana", type="primary", use_container_width=True):
                df_main = carregar_pedidos()

                for _, row in df_editado.iterrows():
                    mask = (
                        (df_main["Fornecedor"] == row["Fornecedor"]) &
                        (df_main["Código"] == row["Código"])
                    )
                    if mask.any():
                        df_main.loc[mask, loja_selecionada] = row["Qtde"]
                    else:
                        nova_linha = {"Fornecedor": row["Fornecedor"], "Código": row["Código"], "Descrição": row["Descrição"]}
                        for l in LOJAS: nova_linha[l] = 0
                        nova_linha[loja_selecionada] = row["Qtde"]
                        df_main = pd.concat([df_main, pd.DataFrame([nova_linha])], ignore_index=True)

                salvar_pedidos(df_main)
                st.success(f"✅ Pedido da {loja_selecionada} enviado para a nuvem com sucesso!")

# ─────────────────────────────────────────────
# ROTA 3 — VISÃO POR FORNECEDOR / RESUMO (Admin)
# ─────────────────────────────────────────────
elif perfil_navegacao == "Visão por Fornecedor (Resumo)":
    # CAPTURA A DATA E HORA ATUAL COM O FUSO HORÁRIO DE BRASÍLIA
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M')

    st.markdown("""
    <div class="hide-print" style="background: linear-gradient(90deg, var(--red-dark) 0%, #1a0808 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 22px;">
        <span style="font-size: 26px; margin-right: 12px;">🍗</span>
        <div style="display: inline-block; vertical-align: top;">
            <div style="font-size: 20px; font-weight: 700; color: var(--text-header);">Visão por Fornecedor — Açougue Especial</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Resumo consolidado agrupado pelas categorias/fornecedores de produtos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

   # ADICIONA A DATA/HORA NA TELA LOGO ACIMA DO QUADRO
    st.markdown(f"""
    <div class="hide-print" style="text-align: right; color: #ffffff; font-size: 15px; margin-top: -10px; margin-bottom: 15px;">
        Gerado em: <strong>{agora}</strong>
    </div>
    """, unsafe_allow_html=True)

    df_all = carregar_pedidos()
    df_cat = carregar_catalogo_acougue()

    if df_all.empty or df_cat.empty:
        st.warning("Não há dados de pedidos ou catálogo preenchidos.")
        st.stop()

    nomes_forn = df_cat["Fornecedor"].dropna().unique().tolist()

    html_print_content = ""

    for i in range(0, len(nomes_forn), 1):
        cols = st.columns(1, gap="small")
        for j, fornecedor in enumerate(nomes_forn[i:i+1]):

            df_forn = df_all[df_all["Fornecedor"] == fornecedor].copy()
            colunas_presentes = LOJAS
            df_forn = df_forn[["Código", "Descrição"] + colunas_presentes].copy()
            df_forn["TOTAL"] = df_forn[colunas_presentes].sum(axis=1)

            lojas_renomeadas = {l: MAPA_LOJAS[l] for l in colunas_presentes}
            df_forn = df_forn.rename(columns=lojas_renomeadas)

            lojas_cols_renomeadas = [MAPA_LOJAS[l] for l in colunas_presentes]

            col_cfg_forn = {
                "Código":    st.column_config.NumberColumn("Cód.", width=80, format="%d", disabled=True),
                "Descrição": st.column_config.TextColumn("Produto", disabled=False),
                "TOTAL":     st.column_config.NumberColumn("TOTAL", format="%d", disabled=True),
            }
            for c in lojas_cols_renomeadas:
                col_cfg_forn[c] = st.column_config.NumberColumn(c, format="%d", disabled=False, min_value=0)

            altura = (len(df_forn) * 35) + 42

            with cols[j]:
                with st.container(border=True):
                    st.markdown('<div class="title-input">', unsafe_allow_html=True)
                    st.text_input(
                        "Fornecedor",
                        value=f"🍗 {fornecedor}",
                        label_visibility="collapsed",
                        key=f"title_forn_{fornecedor}_{st.session_state['reset_counter_acougue_especial']}"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                    cols_order_forn = ["Código", "Descrição"] + lojas_cols_renomeadas + ["TOTAL"]
                    df_forn_edit = st.data_editor(
                        df_forn[cols_order_forn],
                        hide_index=True,
                        use_container_width=True,
                        column_config=col_cfg_forn,
                        height=altura,
                        num_rows="fixed",
                        key=f"forn_acougue_especial_{fornecedor}_{st.session_state['reset_counter_acougue_especial']}"
                    )

                    total_geral = int(df_forn_edit["TOTAL"].sum()) if "TOTAL" in df_forn_edit.columns else 0
                    st.markdown(f"""
                        <div style="text-align:right; font-weight:700; margin-top:6px; color:var(--red-bright); font-size:15px;">
                            Total Geral: {total_geral} unidades
                        </div>
                    """, unsafe_allow_html=True)

                    html_table = df_forn_edit.to_html(index=False, classes=["print-table", "print-forn"])
                    for loja in LOJAS:
                        partes = loja.split(" ")
                        if len(partes) == 2:
                            html_table = html_table.replace(
                                f"<th>{loja}</th>",
                                f"<th>{partes[0]}<br>{partes[1]}</th>"
                            )
                    html_print_content += f"<h3 style='color: black; margin-top: 10px; margin-bottom: 4px;'>🍗 {fornecedor}</h3>\n"
                    html_print_content += f"{html_table}\n"
                    html_print_content += f"<div style='text-align:right; font-weight:bold; font-size:11px; margin-top:3px; margin-bottom: 8px; color: black;'>Total do Fornecedor: {total_geral} unidades</div>\n"

        st.write("<br>", unsafe_allow_html=True)

    st.markdown(f"""<div id="print-section">
<h2 style="color: black; margin-bottom: 10px; text-align: center; border-bottom: 2px solid black; padding-bottom: 5px;">
    Visão por Fornecedor (Resumo) — Açougue Especial &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style="font-size: 11px; font-weight: normal; color: #333;">{agora}</span>
</h2>
<div class="print-container">
{html_print_content}
</div>
</div>""", unsafe_allow_html=True)

    st.divider()
    
    # ─────────────────────────────────────────────
    # BOTÕES DE EXPORTAÇÃO, IMPRESSÃO E LIMPEZA
    # ─────────────────────────────────────────────
    col_csv, col_excel, col_space, col_print, col_zerar = st.columns([1.5, 1.5, 2.0, 2.5, 2.5])
    
    # Unifica as informações para que tanto CSV quanto Excel usem os mesmos dados
    df_export = pd.DataFrame()
    for forn in nomes_forn:
        df_f = df_all[df_all["Fornecedor"] == forn].copy()
        if not df_f.empty:
            df_export = pd.concat([df_export, df_f], ignore_index=True)
            
    if not df_export.empty:
        df_export = df_export[["Código", "Descrição", "Fornecedor"] + LOJAS]
        df_export["TOTAL GERAL"] = df_export[LOJAS].sum(axis=1)
        df_export = df_export.rename(columns=MAPA_LOJAS)

    with col_csv:
        if not df_export.empty:
            csv_str = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Exportar CSV", data=csv_str, file_name="visao_fornecedor.csv", mime="text/csv", use_container_width=True)

    with col_excel:
        if not df_export.empty:
            excel_data = gerar_excel_estilizado(df_export, "Visão Fornecedores")
            st.download_button("⬇️ Exportar Excel", data=excel_data, file_name="visao_fornecedor.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    with col_print:
        if st.button("🖨️ Imprimir Resumo Geral", use_container_width=True):
            components.html(
                "<script>"
                "var s=document.createElement('style');"
                "s.id='__forn_port__';"
                "s.innerHTML='@media print{@page{size:A4 portrait!important;margin:8mm 8mm!important;}}';"
                "window.parent.document.head.appendChild(s);"
                "window.parent.print();"
                "setTimeout(function(){"
                "var e=window.parent.document.getElementById('__forn_port__');"
                "if(e)e.remove();"
                "},3000);"
                "</script>",
                height=0
            )

    with col_zerar:
        if st.button("🚨 Zerar Todos os Pedidos", use_container_width=True, key="btn_zerar_forn_esp"):
            modal_zerar_pedidos()

# ─────────────────────────────────────────────
# ROTA 4 — CATÁLOGO DE PRODUTOS
# ─────────────────────────────────────────────
elif perfil_navegacao == "Catálogo de Produtos":
    st.markdown("""
    <div class="page-header hide-print" style="background: linear-gradient(90deg, var(--red-dark) 0%, #1a0808 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 22px;">
        <span style="font-size: 26px; margin-right: 12px;">🗂️</span>
        <div style="display: inline-block; vertical-align: top;">
            <div style="font-size: 20px; font-weight: 700; color: var(--text-header);">Catálogo de Peças e Nomes Oficiais</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Atualize nomes direto do ERP ou crie apelidos personalizados. Os apelidos terão prioridade em todo o sistema.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_catalogo = carregar_catalogo_acougue()
    df_editor_input = df_catalogo.drop(columns=["Descrição"], errors="ignore")

    for loja in LOJAS:
        if loja in df_editor_input.columns:
            df_editor_input[loja] = df_editor_input[loja].fillna(False).astype(bool)

    df_editor_input["Código"] = pd.to_numeric(df_editor_input["Código"], errors='coerce').fillna(0).astype(int)

    cols_texto = ["Fornecedor", "Descrição Oficial", "Nome Personalizado"]
    for col in cols_texto:
        if col in df_editor_input.columns:
            df_editor_input[col] = df_editor_input[col].fillna("").astype(str)

    ordem_colunas = ["Fornecedor", "Código", "Descrição Oficial", "Nome Personalizado"] + LOJAS
    df_editor_input = df_editor_input[ordem_colunas]

    with st.container(border=True):

        opcoes_forn = [
            "PIONEIRO",
            "FRANGO PARANÁ",
            "BIG FRANGO - TEMPERADOS",
            "BIG FRANGO - MIX BANDEJAS",
            "BIG FRANGO - MIX BALCÃO",
            "BIG FRANGO - MIX CONGELADO",
        ]

        col_cfg_cat = {
            "Fornecedor":         st.column_config.SelectboxColumn("Fornecedor", options=opcoes_forn, width=200, required=True),
            "Código":             st.column_config.NumberColumn("Cód.", width=80, format="%d", required=True),
            "Descrição Oficial":  st.column_config.TextColumn("Nome Oficial (ERP)", width=280, disabled=False),
            "Nome Personalizado": st.column_config.TextColumn("Nome Personalizado (Apelido)", width=230),
        }
        for loja in LOJAS:
            col_cfg_cat[loja] = st.column_config.CheckboxColumn(loja, default=False)

        edited_cat = st.data_editor(
            df_editor_input,
            use_container_width=True,
            hide_index=True,
            height=600,
            num_rows="dynamic",
            column_config=col_cfg_cat,
            key=f"editor_catalogo_acougue_especial_{st.session_state['reset_counter_acougue_especial']}"
        )

        st.divider()
        col_atualizar, col_sync, _ = st.columns([2.5, 3, 3])

        with col_atualizar:
            if st.button("💾 Salvar Catálogo", type="primary", use_container_width=True):
                salvar_catalogo(edited_cat)
                st.session_state['reset_counter_acougue_especial'] += 1
                st.success("✅ Catálogo atualizado com sucesso!")
                st.rerun()

        with col_sync:
            if st.button("📥 Puxar Nomes do ERP", use_container_width=True):
                try:
                    conn_pg = st.connection("banco_erp", type="sql")
                    cods = tuple(edited_cat["Código"].tolist())

                    if len(cods) == 1:
                        cods_str = f"({cods[0]})"
                    else:
                        cods_str = str(cods)

                    query_nomes = f"SELECT cadp_codigo, cadp_descricao FROM cadprod WHERE cadp_codigo IN {cods_str}"
                    df_nomes = conn_pg.query(query_nomes, ttl=0)

                    for _, row in df_nomes.iterrows():
                        mask = edited_cat["Código"] == row["cadp_codigo"]
                        edited_cat.loc[mask, "Descrição Oficial"] = row["cadp_descricao"]

                    salvar_catalogo(edited_cat)
                    st.success("✅ Nomes Oficiais sincronizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    if "No database configured" in str(e) or "missing" in str(e).lower():
                        st.error("⚠️ Aviso: As credenciais de acesso ao PostgreSQL não foram encontradas no painel Secrets.")
                    else:
                        st.error(f"⚠️ Erro ao buscar nomes no banco ERP: {e}")
