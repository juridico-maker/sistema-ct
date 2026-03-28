import streamlit as st
import pandas as pd
from anthropic import Anthropic
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="C&T Enterprise", layout="wide", page_icon="⚖️")

# --- ESTILO NAVY & GOLD ---
st.markdown("""
    <style>
    .main { background-color: #001f3f; color: white; }
    [data-testid="stSidebar"] { background-color: #00152b; border-right: 3px solid #d4af37; }
    h1, h2, h3 { color: #d4af37 !important; }
    .stButton>button { background-color: #d4af37; color: #001f3f; font-weight: bold; border-radius: 5px; height: 3em; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #002b55; border: 1px solid #d4af37; color: white; border-radius: 5px; padding: 10px; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #002b55 !important; color: white !important; border: 1px solid #d4af37 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS EM MEMÓRIA ---
if 'db_users' not in st.session_state:
    st.session_state.db_users = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], 
                                            columns=['Nome', 'Email', 'Documento', 'Perfil'])
if 'db_pessoas' not in st.session_state:
    st.session_state.db_pessoas = pd.DataFrame(columns=['Nome', 'CPF_CNPJ', 'Email', 'Papel'])
if 'db_processos' not in st.session_state:
    st.session_state.db_processos = pd.DataFrame(columns=['CNJ', 'Cliente', 'Assunto', 'Vara', 'Status'])
if 'db_movimentacoes' not in st.session_state:
    st.session_state.db_movimentacoes = pd.DataFrame(columns=['CNJ', 'Data', 'Titulo', 'Descricao'])
if 'db_memoria_ia' not in st.session_state:
    st.session_state.db_memoria_ia = pd.DataFrame(columns=['CNJ', 'Role', 'Content'])
if 'user_logged' not in st.session_state:
    st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("⚖️ Costa & Tavares - Sistema Integrado")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        user_choice = st.selectbox("Selecione o Usuário", st.session_state.db_users['Nome'].tolist())
        if st.button("ENTRAR NO SISTEMA"):
            st.session_state.user_logged = user_choice
            st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("C&T Enterprise")
    st.write(f"Usuário: **{st.session_state.user_logged}**")
    menu = st.radio("Módulos", ["👥 Pessoas", "📋 Processos", "👤 Usuários", "⚙️ Configurações"])
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Gestão de Clientes e Partes")
    with st.container():
        st.subheader("📝 Cadastrar Nova Pessoa")
        with st.form("form_pessoa", clear_on_submit=True):
            c1, c2 = st.columns(2)
            p_nome = c1.text_input("Nome Completo")
            p_doc = c2.text_input("CPF ou CNPJ")
            p_mail = c1.text_input("E-mail")
            p_papel = c2.selectbox("Vínculo", ["Cliente", "Parte Contrária", "Terceiro"])
            if st.form_submit_button("CADASTRAR PESSOA"):
                if p_doc in st.session_state.db_pessoas['CPF_CNPJ'].values:
                    st.error("Documento já cadastrado.")
                else:
                    nova_p = pd.DataFrame([[p_nome, p_doc, p_mail, p_papel]], columns=st.session_state.db_pessoas.columns)
                    st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, nova_p], ignore_index=True)
                    st.success("Pessoa cadastrada!")
    st.write("---")
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO PROCESSOS ---
elif menu == "📋 Processos":
    st.header("Gestão de Processos")
    t1, t2 = st.tabs(["📂 Cadastro e Carteira", "⚡ Gestão Estratégica"])
    
    with t1:
        st.subheader("🆕 Novo Processo")
        if st.session_state.db_pessoas.empty:
            st.warning("Cadastre uma Pessoa antes de criar um processo.")
        else:
            with st.form("form_proc", clear_on_submit=True):
                cnj = st.text_input("Número CNJ")
                cliente = st.selectbox("Vincular Cliente", st.session_state.db_pessoas[st.session_state.db_pessoas['Papel']=='Cliente']['Nome'].tolist())
                assunto = st.text_input("Assunto / Tese")
                vara = st.text_input("Vara/Comarca")
                if st.form_submit_button("SALVAR PROCESSO"):
                    if cnj in st.session_state.db_processos['CNJ'].values:
                        st.error("Processo já existente.")
                    else:
                        new_proc = pd.DataFrame([[cnj, cliente, assunto, vara, "Ativo"]], columns=st.session_state.db_processos.columns)
                        st.session_state.db_processos = pd.concat([st.session_state.db_processos, new_proc], ignore_index=True)
                        st.success("Processo salvo na carteira!")
        st.write("---")
        st.dataframe(st.session_state.db_processos, use_container_width=True)

    with t2:
        if st.session_state.db_processos.empty:
            st.info("Nenhum processo para gerir.")
        else:
            p_sel = st.selectbox("Selecione o Processo:", st.session_state.db_processos['CNJ'].tolist())
            m1, m2 = st.tabs(["📌 Movimentações", "🤖 IA Estratégica"])
            
            with m1:
                with st.form("form_mov", clear_on_submit=True):
                    tit = st.text_input("Título (ex: Intimação de Sentença)")
                    dsc = st.text_area("Descrição do Ato")
                    if st.form_submit_button("REGISTRAR ATO"):
                        new_m = pd.DataFrame([[p_sel, datetime.date.today(), tit, dsc]], columns=st.session_state.db_movimentacoes.columns)
                        st.session_state.db_movimentacoes = pd.concat([st.session_state.db_movimentacoes, new_m], ignore_index=True)
                st.dataframe(st.session_state.db_movimentacoes[st.session_state.db_movimentacoes['CNJ'] == p_sel])

            with m2:
                # Memória do Processo
                memoria = st.session_state.db_memoria_ia[st.session_state.db_memoria_ia['CNJ'] == p_sel]
                for i, m in memoria.iterrows():
                    with st.chat_message(m['Role']): st.write(m['Content'])
                
                chat_input = st.chat_input("Dúvida estratégica ou rascunho de peça...")
                if chat_input:
                    with st.chat_message("user"): st.write(chat_input)
                    st.session_state.db_memoria_ia = pd.concat([st.session_state.db_memoria_ia, pd.DataFrame([[p_sel, "user", chat_input]], columns=st.session_state.db_memoria_ia.columns)], ignore_index=True)
                    
                    try:
                        client = Anthropic(api_key=st.secrets["CLAUDE_KEY"])
                        proc_data = st.session_state.db_processos[st.session_state.db_processos['CNJ'] == p_sel].iloc[0]
                        prompt = f"C&T. Processo {p_sel}. Cliente {proc_data['Cliente']}. Assunto: {proc_data['Assunto']}. Pergunta: {chat_input}"
                        resp = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=2000, messages=[{"role": "user", "content": prompt}])
                        resposta = resp.content[0].text
                        with st.chat_message("assistant"): st.write(resposta)
                        st.session_state.db_memoria_ia = pd.concat([st.session_state.db_memoria_ia, pd.DataFrame([[p_sel, "assistant", resposta]], columns=st.session_state.db_memoria_ia.columns)], ignore_index=True)
                    except: st.error("Erro na IA.")

# --- MÓDULO USUÁRIOS ---
elif menu == "👤 Usuários":
    if "Admin" in st.session_state.user_logged:
        st.header("Gestão de Equipe")
        with st.form("form_user", clear_on_submit=True):
            u_nome = st.text_input("Nome do Usuário")
            u_mail = st.text_input("E-mail")
            u_doc = st.text_input("CPF/CNPJ")
            u_perfil = st.selectbox("Perfil", ["Advogado", "Estagiário", "Admin"])
            if st.form_submit_button("CADASTRAR USUÁRIO"):
                new_u = pd.DataFrame([[u_nome, u_mail, u_doc, u_perfil]], columns=st.session_state.db_users.columns)
                st.session_state.db_users = pd.concat([st.session_state.db_users, new_u], ignore_index=True)
                st.success("Usuário adicionado!")
        st.dataframe(st.session_state.db_users, use_container_width=True)
    else:
        st.error("Acesso restrito ao Administrador.")

# --- CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    st.header("Configurações do Escritório")
    st.text_input("Nome Comercial", "Costa & Tavares Advogados")
    st.write("Configurações de Prompt e Backup em breve.")
