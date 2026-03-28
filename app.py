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
    .stDataFrame { background-color: #002b55; border: 1px solid #d4af37; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS EM MEMÓRIA ---
for key, columns in {
    'db_users': ['Nome', 'Email', 'Documento', 'Perfil'],
    'db_pessoas': ['Nome', 'CPF_CNPJ', 'Email'],
    'db_processos': ['CNJ', 'Pessoa_Vinculada', 'Papel', 'Assunto', 'Status'],
    'db_movimentacoes': ['CNJ', 'Data', 'Titulo', 'Descricao'],
    'db_memoria_ia': ['CNJ', 'Role', 'Content']
}.items():
    if key not in st.session_state:
        if key == 'db_users':
            st.session_state[key] = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=columns)
        else:
            st.session_state[key] = pd.DataFrame(columns=columns)

if 'user_logged' not in st.session_state:
    st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("⚖️ Costa & Tavares - Acesso")
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
    menu = st.radio("Navegação", ["👥 Pessoas", "📋 Processos", "👤 Usuários", "⚙️ Configurações"])
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Gestão de Pessoas")
    
    col_t, col_b = st.columns([4, 1])
    with col_b:
        btn_nova_pessoa = st.button("➕ Cadastrar Pessoa")

    if btn_nova_pessoa or 'form_pessoa_aberto' in st.session_state:
        st.session_state.form_pessoa_aberto = True
        with st.form("form_pessoa", clear_on_submit=True):
            st.subheader("📝 Nova Pessoa")
            c1, c2 = st.columns(2)
            p_nome = c1.text_input("Nome Completo")
            p_doc = c2.text_input("CPF ou CNPJ")
            p_mail = st.text_input("E-mail")
            
            c_bot1, c_bot2 = st.columns(2)
            if c_bot1.form_submit_button("SALVAR"):
                if p_doc in st.session_state.db_pessoas['CPF_CNPJ'].values:
                    st.error("CPF/CNPJ já cadastrado.")
                else:
                    nova_p = pd.DataFrame([[p_nome, p_doc, p_mail]], columns=st.session_state.db_pessoas.columns)
                    st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, nova_p], ignore_index=True)
                    st.success("Cadastrado!")
                    del st.session_state.form_pessoa_aberto
                    st.rerun()
            if c_bot2.form_submit_button("CANCELAR"):
                del st.session_state.form_pessoa_aberto
                st.rerun()

    st.write("### Lista de Pessoas")
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO PROCESSOS ---
elif menu == "📋 Processos":
    st.header("Gestão de Processos")
    
    aba_lista, aba_gestao = st.tabs(["📂 Carteira de Processos", "⚡ Gestão Estratégica"])
    
    with aba_lista:
        col_t, col_b = st.columns([4, 1])
        with col_b:
            btn_novo_proc = st.button("➕ Cadastrar Processo")

        if btn_novo_proc or 'form_proc_aberto' in st.session_state:
            st.session_state.form_proc_aberto = True
            with st.form("form_proc"):
                st.subheader("🆕 Novo Processo")
                cnj = st.text_input("Número CNJ")
                
                if st.session_state.db_pessoas.empty:
                    st.warning("⚠️ Cadastre uma pessoa antes.")
                else:
                    p_vinculo = st.selectbox("Selecionar Pessoa", st.session_state.db_pessoas['Nome'].tolist())
                    papel = st.selectbox("Vínculo/Papel", ["Cliente", "Parte Contrária", "Assistente", "Terceiro"])
                    assunto = st.text_input("Assunto / Tese Principal")
                    
                    c_b1, c_b2 = st.columns(2)
                    if c_b1.form_submit_button("SALVAR PROCESSO"):
                        if cnj in st.session_state.db_processos['CNJ'].values:
                            st.error("CNJ já existe.")
                        else:
                            novo_p = pd.DataFrame([[cnj, p_vinculo, papel, assunto, "Ativo"]], columns=st.session_state.db_processos.columns)
                            st.session_state.db_processos = pd.concat([st.session_state.db_processos, novo_p], ignore_index=True)
                            st.success("Processo Salvo!")
                            del st.session_state.form_proc_aberto
                            st.rerun()
                    if c_b2.form_submit_button("CANCELAR"):
                        del st.session_state.form_proc_aberto
                        st.rerun()

        st.write("### Processos Ativos")
        st.dataframe(st.session_state.db_processos, use_container_width=True)

    with aba_gestao:
        if st.session_state.db_processos.empty:
            st.info("Nenhum processo para gerir.")
        else:
            p_sel = st.selectbox("Selecione o CNJ para trabalhar:", st.session_state.db_processos['CNJ'].tolist())
            m1, m2 = st.tabs(["📌 Movimentações", "🤖 IA Estratégica do Caso"])
            
            with m1:
                with st.form("f_mov", clear_on_submit=True):
                    t = st.text_input("Título do Ato")
                    d = st.text_area("Descrição")
                    if st.form_submit_button("REGISTRAR MOVIMENTAÇÃO"):
                        nm = pd.DataFrame([[p_sel, datetime.date.today(), t, d]], columns=st.session_state.db_movimentacoes.columns)
                        st.session_state.db_movimentacoes = pd.concat([st.session_state.db_movimentacoes, nm], ignore_index=True)
                st.dataframe(st.session_state.db_movimentacoes[st.session_state.db_movimentacoes['CNJ'] == p_sel])

            with m2:
                mem = st.session_state.db_memoria_ia[st.session_state.db_memoria_ia['CNJ'] == p_sel]
                for i, m in mem.iterrows():
                    with st.chat_message(m['Role']): st.write(m['Content'])
                
                chat_in = st.chat_input("Dúvida estratégica para este processo...")
                if chat_in:
                    st.session_state.db_memoria_ia = pd.concat([st.session_state.db_memoria_ia, pd.DataFrame([[p_sel, "user", chat_in]], columns=st.session_state.db_memoria_ia.columns)], ignore_index=True)
                    with st.chat_message("user"): st.write(chat_in)
                    
                    try:
                        client = Anthropic(api_key=st.secrets["CLAUDE_KEY"])
                        resp = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=2000, messages=[{"role": "user", "content": f"C&T Proc {p_sel}: {chat_in}"}])
                        txt = resp.content[0].text
                        st.session_state.db_memoria_ia = pd.concat([st.session_state.db_memoria_ia, pd.DataFrame([[p_sel, "assistant", txt]], columns=st.session_state.db_memoria_ia.columns)], ignore_index=True)
                        with st.chat_message("assistant"): st.write(txt)
                    except: st.error("Erro na IA.")

# --- DEMAIS MÓDULOS ---
elif menu == "👤 Usuários":
    st.header("Gestão de Equipe")
    if st.button("➕ Cadastrar Novo Usuário"): st.session_state.f_user = True
    if 'f_user' in st.session_state:
        with st.form("u_f"):
            n, e, d = st.columns(3)
            un = n.text_input("Nome")
            ue = e.text_input("Email")
            ud = d.text_input("CPF/CNPJ")
            perf = st.selectbox("Perfil", ["Advogado", "Estagiário", "Admin"])
            if st.form_submit_button("SALVAR"):
                nu = pd.DataFrame([[un, ue, ud, perf]], columns=st.session_state.db_users.columns)
                st.session_state.db_users = pd.concat([st.session_state.db_users, nu], ignore_index=True)
                del st.session_state.f_user
                st.rerun()
    st.dataframe(st.session_state.db_users)

elif menu == "⚙️ Configurações":
    st.header("Configurações do Sistema")
    st.text_input("Escritório", "Costa & Tavares")
