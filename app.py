import streamlit as st
import pandas as pd
from anthropic import Anthropic
from docx import Document
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO NAVY & GOLD) ---
st.set_page_config(page_title="Costa & Tavares - Sistema Integrado", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #001f3f; color: #fdfdfd; }
    [data-testid="stSidebar"] { background-color: #00152b; border-right: 2px solid #d4af37; }
    h1, h2, h3, .stMetric { color: #d4af37 !important; }
    .stButton>button { background-color: #d4af37; color: #001f3f; font-weight: bold; width: 100%; border-radius: 8px; }
    div[data-testid="stExpander"] { border: 1px solid #d4af37; background-color: #002b55; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'db_pessoas' not in st.session_state:
    st.session_state.db_pessoas = pd.DataFrame(columns=['ID', 'Nome', 'CPF_CNPJ', 'Email', 'Telefone'])
if 'db_processos' not in st.session_state:
    st.session_state.db_processos = pd.DataFrame(columns=['CNJ', 'Cliente_Doc', 'Assunto', 'Vara', 'Tribunal', 'Status', 'Responsavel'])
if 'user_logged' not in st.session_state:
    st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("⚖️ Costa & Tavares - Acesso")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        user = st.selectbox("Usuário", ["Alexandre (Admin)", "Vinícius", "Bruna", "Naira"])
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            st.session_state.user_logged = user
            st.rerun()
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.title("C&T Enterprise")
    menu = st.radio("Navegação", ["📋 Processos", "👥 Pessoas", "🤖 IA Estratégica", "⚙️ Configurações"])
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Gestão de Clientes e Pessoas")
    with st.expander("➕ Cadastrar Nova Pessoa"):
        with st.form("form_p"):
            n = st.text_input("Nome")
            d = st.text_input("CPF ou CNPJ")
            e = st.text_input("E-mail")
            t = st.text_input("Telefone")
            if st.form_submit_button("Salvar"):
                if d in st.session_state.db_pessoas['CPF_CNPJ'].values:
                    st.error("Documento já existe.")
                else:
                    new = pd.DataFrame([[len(st.session_state.db_pessoas), n, d, e, t]], columns=st.session_state.db_pessoas.columns)
                    st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, new], ignore_index=True)
                    st.success("Cadastrado!")
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO PROCESSOS ---
elif menu == "📋 Processos":
    st.header("Carteira de Processos")
    with st.expander("🆕 Novo Processo"):
        if st.session_state.db_pessoas.empty:
            st.warning("Cadastre uma Pessoa antes de criar um processo.")
        else:
            with st.form("form_proc"):
                c = st.text_input("Número CNJ")
                cli = st.selectbox("Vincular Cliente", st.session_state.db_pessoas['Nome'].tolist())
                ass = st.text_input("Assunto")
                status = st.selectbox("Status", ["Ativo", "Sentenciado", "Acórdão", "Arquivado"])
                if st.form_submit_button("Salvar Processo"):
                    new_pr = pd.DataFrame([[c, cli, ass, "Vara 1", "Tribunal X", status, st.session_state.user_logged]], columns=st.session_state.db_processos.columns)
                    st.session_state.db_processos = pd.concat([st.session_state.db_processos, new_pr], ignore_index=True)
                    st.success("Processo salvo!")
    st.dataframe(st.session_state.db_processos, use_container_width=True)

# --- MÓDULO IA ESTRATÉGICA ---
elif menu == "🤖 IA Estratégica":
    st.header("Agente de IA do Sistema")
    if st.session_state.db_processos.empty:
        st.info("Nenhum processo cadastrado para análise.")
    else:
        p_sel = st.selectbox("Selecione o Processo:", st.session_state.db_processos['CNJ'].tolist())
        dados = st.session_state.db_processos[st.session_state.db_processos['CNJ'] == p_sel].iloc[0]
        
        st.write(f"💼 Analisando: **{dados['Cliente_Doc']}** | Assunto: **{dados['Assunto']}**")
        
        pergunta = st.chat_input("Dúvida estratégica sobre este caso...")
        if pergunta:
            try:
                client = Anthropic(api_key=st.secrets["CLAUDE_KEY"])
                prompt = f"Escritório C&T. Processo: {dados['CNJ']}. Cliente: {dados['Cliente_Doc']}. Pergunta: {pergunta}"
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    system="Você é o sistema jurídico da Costa & Tavares. Analise e sugira estratégias.",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(response.content[0].text)
            except Exception as e:
                st.error(f"Erro na conexão do Sistema: {e}")

# --- CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    if "Admin" in st.session_state.user_logged:
        st.header("Painel do Administrador")
        st.write(f"Configurações gerais para o escritório.")
        st.text_input("Nome do Escritório", "Costa & Tavares")
        st.number_input("Limite de Upload (MB)", 50)
    else:
        st.error("Acesso negado.")
