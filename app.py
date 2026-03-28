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
    .stButton>button { background-color: #d4af37; color: #001f3f; font-weight: bold; border-radius: 5px; height: 3em; border: none; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #002b55; border: 1px solid #d4af37; color: white; border-radius: 5px; padding: 10px; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #002b55 !important; color: white !important; border: 1px solid #d4af37 !important; }
    .stDataFrame { background-color: #002b55; border: 1px solid #d4af37; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE BANCOS ---
if 'db_users' not in st.session_state:
    st.session_state.db_users = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=['Nome', 'Email', 'Documento', 'Perfil'])
if 'db_pessoas' not in st.session_state:
    st.session_state.db_pessoas = pd.DataFrame(columns=['Nome', 'CPF_CNPJ', 'Email'])
if 'db_processos' not in st.session_state:
    st.session_state.db_processos = pd.DataFrame(columns=['CNJ', 'Pessoa_Vinculada', 'Papel', 'Assunto', 'Status'])
if 'db_movimentacoes' not in st.session_state:
    st.session_state.db_movimentacoes = pd.DataFrame(columns=['CNJ', 'Data', 'Titulo', 'Descricao'])
if 'db_memoria_ia' not in st.session_state:
    st.session_state.db_memoria_ia = pd.DataFrame(columns=['CNJ', 'Role', 'Content'])

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
    st.write(f"Sessão: **{st.session_state.user_logged}**")
    menu = st.radio("Navegação", ["👥 Pessoas", "📋 Processos", "👤 Usuários", "⚙️ Configurações"])
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Gestão de Pessoas")
    col_t, col_b = st.columns([4, 1.2])
    with col_b:
        if st.button("➕ Cadastrar Pessoa"):
            st.session_state.f_p_aberto = True

    if st.session_state.get('f_p_aberto'):
        with st.form("form_pessoa"):
            st.subheader("📝 Nova Pessoa")
            c1, c2 = st.columns(2)
            p_nome = c1.text_input("Nome Completo")
            p_doc = c2.text_input("CPF ou CNPJ")
            p_mail = st.text_input("E-mail")
            cb1, cb2 = st.columns(2)
            if cb1.form_submit_button("SALVAR"):
                if not p_nome or not p_doc:
                    st.error("Preencha Nome e CPF/CNPJ.")
                elif p_doc in st.session_state.db_pessoas['CPF_CNPJ'].values:
                    st.error("CPF/CNPJ já cadastrado.")
                else:
                    nova_p = pd.DataFrame([[p_nome, p_doc, p_mail]], columns=st.session_state.db_pessoas.columns)
                    st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, nova_p], ignore_index=True)
                    st.session_state.f_p_aberto = False
                    st.rerun()
            if cb2.form_submit_button("CANCELAR"):
                st.session_state.f_p_aberto = False
                st.rerun()

    st.write("### Lista de Pessoas")
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO PROCESSOS ---
elif menu == "📋 Processos":
    st.header("Gestão de Processos")
    aba_lista, aba_gestao = st.tabs(["📂 Carteira", "⚡ Gestão Estratégica"])
    
    with aba_lista:
        col_t, col_b = st.columns([4, 1.2])
        with col_b:
            if st.button("➕ Cadastrar Processo"):
                st.session_state.f_pr_aberto = True

        if st.session_state.get('f_pr_aberto'):
            with st.form("form_proc"):
                st.subheader("🆕 Novo Processo")
                cnj = st.text_input("Número CNJ")
                
                lista_pessoas = st.session_state.db_pessoas['Nome'].tolist()
                p_vinculo = st.selectbox("Vincular Pessoa", ["Nenhuma pessoa cadastrada"] if not lista_pessoas else lista_pessoas)
                papel = st.selectbox("Papel no Processo", ["Cliente", "Parte Contrária", "Assistente", "Terceiro"])
                assunto = st.text_input("Assunto / Tese Principal")
                
                cb1, cb2 = st.columns(2)
                if cb1.form_submit_button("SALVAR PROCESSO"):
                    if not cnj:
                        st.warning("⚠️ Erro: Sem número cadastrado (CNJ obrigatório).")
                    elif not lista_pessoas or p_vinculo == "Nenhuma pessoa cadastrada":
                        st.warning("⚠️ Erro: Sem pessoa vinculada. Cadastre uma pessoa no módulo 'Pessoas' primeiro.")
                    elif cnj in st.session_state.db_processos['CNJ'].values:
                        st.error("CNJ já cadastrado.")
                    else:
                        novo_p = pd.DataFrame([[cnj, p_vinculo, papel, assunto, "Ativo"]], columns=st.session_state.db_processos.columns)
                        st.session_state.db_processos = pd.concat([st.session_state.db_processos, novo_p], ignore_index=True)
                        st.session_state.f_pr_aberto = False
                        st.rerun()
                if cb2.form_submit_button("CANCELAR"):
                    st.session_state.f_pr_aberto = False
                    st.rerun()

        st.write("### Carteira Ativa")
        st.dataframe(st.session_state.db_processos, use_container_width=True)

    with aba_gestao:
        if st.session_state.db_processos.empty:
            st.info("Nenhum processo para gerir.")
        else:
            p_sel = st.selectbox("Selecionar Processo:", st.session_state.db_processos['CNJ'].tolist())
            st.write(f"Gerindo: **{p_sel}**")
            # Aqui seguem as abas de Movimentações e IA...

# --- MÓDULO USUÁRIOS ---
elif menu == "👤 Usuários":
    st.header("Gestão de Equipe")
    col_t, col_b = st.columns([4, 1.2])
    with col_b:
        if st.button("➕ Cadastrar Usuário"):
            st.session_state.f_u_aberto = True

    if st.session_state.get('f_u_aberto'):
        with st.form("form_user"):
            st.subheader("👤 Novo Usuário")
            un = st.text_input("Nome Completo")
            ue = st.text_input("E-mail")
            ud = st.text_input("CPF ou CNPJ")
            up = st.selectbox("Perfil de Acesso", ["Advogado", "Estagiário", "Admin"])
            
            cb1, cb2 = st.columns(2)
            if cb1.form_submit_button("SALVAR USUÁRIO"):
                if un and ue and ud:
                    nu = pd.DataFrame([[un, ue, ud, up]], columns=st.session_state.db_users.columns)
                    st.session_state.db_users = pd.concat([st.session_state.db_users, nu], ignore_index=True)
                    st.session_state.f_u_aberto = False
                    st.rerun()
                else:
                    st.error("Todos os campos são obrigatórios.")
            if cb2.form_submit_button("CANCELAR"):
                st.session_state.f_u_aberto = False
                st.rerun()
                
    st.write("### Usuários Cadastrados")
    st.dataframe(st.session_state.db_users, use_container_width=True)

elif menu == "⚙️ Configurações":
    st.header("Configurações do Sistema")
    st.text_input("Nome do Escritório", "Costa & Tavares")
