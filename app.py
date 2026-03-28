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
    .badge-cliente { background-color: #d4af37; color: #001f3f; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE BANCOS ---
if 'db_users' not in st.session_state:
    st.session_state.db_users = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=['Nome', 'Email', 'Documento', 'Perfil'])
if 'db_pessoas' not in st.session_state:
    st.session_state.db_pessoas = pd.DataFrame(columns=['Nome', 'CPF_CNPJ', 'Email'])
if 'db_processos' not in st.session_state:
    st.session_state.db_processos = pd.DataFrame(columns=['CNJ', 'Vara', 'Comarca', 'Pessoa', 'Polo', 'E_Cliente', 'Status'])

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
                else:
                    nova_p = pd.DataFrame([[p_nome, p_doc, p_mail]], columns=st.session_state.db_pessoas.columns)
                    st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, nova_p], ignore_index=True)
                    st.session_state.f_p_aberto = False
                    st.rerun()
            if cb2.form_submit_button("CANCELAR"):
                st.session_state.f_p_aberto = False
                st.rerun()
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
                st.subheader("🆕 Vincular Processo")
                cnj = st.text_input("Número CNJ")
                c1, c2 = st.columns(2)
                vara = c1.text_input("Vara")
                comarca = c2.text_input("Comarca")
                
                st.write("---")
                lista_p = st.session_state.db_pessoas['Nome'].tolist()
                pessoa_sel = st.selectbox("Vincular Pessoa", ["Nenhuma cadastrada"] if not lista_p else lista_p)
                
                col_p1, col_p2 = st.columns(2)
                polo = col_p1.selectbox("Polo no Processo", ["Polo Ativo", "Polo Passivo", "Terceiro"])
                e_cliente = col_p2.checkbox("Marcar como Cliente do escritório")
                
                cb1, cb2 = st.columns(2)
                if cb1.form_submit_button("SALVAR PROCESSO"):
                    if not cnj:
                        st.warning("⚠️ CNJ obrigatório.")
                    elif pessoa_sel == "Nenhuma cadastrada":
                        st.warning("⚠️ Selecione uma pessoa.")
                    elif not e_cliente:
                        st.error("❌ Erro: É obrigatório marcar pelo menos uma pessoa como cliente.")
                    else:
                        novo_p = pd.DataFrame([[cnj, vara, comarca, pessoa_sel, polo, "Sim" if e_cliente else "Não", "Ativo"]], 
                                             columns=st.session_state.db_processos.columns)
                        st.session_state.db_processos = pd.concat([st.session_state.db_processos, novo_p], ignore_index=True)
                        st.session_state.f_pr_aberto = False
                        st.rerun()
                if cb2.form_submit_button("CANCELAR"):
                    st.session_state.f_pr_aberto = False
                    st.rerun()

        # Exibição da Carteira com destaque de Cliente
        st.write("### Carteira Ativa")
        if not st.session_state.db_processos.empty:
            # Formatação simples para destaque
            df_view = st.session_state.db_processos.copy()
            df_view['Cliente?'] = df_view['E_Cliente'].apply(lambda x: "⭐ CLIENTE" if x == "Sim" else "-")
            st.dataframe(df_view[['CNJ', 'Vara', 'Comarca', 'Pessoa', 'Polo', 'Cliente?']], use_container_width=True)
        else:
            st.info("Nenhum processo cadastrado.")

# --- MÓDULO USUÁRIOS ---
elif menu == "👤 Usuários":
    st.header("Gestão de Equipe")
    col_t, col_b = st.columns([4, 1.2])
    with col_b:
        if st.button("➕ Cadastrar Usuário"): st.session_state.f_u_aberto = True
    
    if st.session_state.get('f_u_aberto'):
        with st.form("u_f"):
            un = st.text_input("Nome")
            ue = st.text_input("E-mail")
            ud = st.text_input("CPF/CNPJ")
            perf = st.selectbox("Perfil", ["Advogado", "Estagiário", "Admin"])
            if st.form_submit_button("SALVAR"):
                nu = pd.DataFrame([[un, ue, ud, perf]], columns=st.session_state.db_users.columns)
                st.session_state.db_users = pd.concat([st.session_state.db_users, nu], ignore_index=True)
                st.session_state.f_u_aberto = False
                st.rerun()
    st.dataframe(st.session_state.db_users, use_container_width=True)

elif menu == "⚙️ Configurações":
    st.header("Configurações Gerais")
