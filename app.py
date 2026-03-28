import streamlit as st
import pandas as pd
from anthropic import Anthropic
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema C&T", layout="wide", page_icon="⚖️")

# --- ESTILO CLEAN C&T V3 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .main { background-color: #f5f6f8; color: #1a1d2e; }
    
    /* Sidebar Branca e Limpa */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #e2e4ea;
    }
    
    /* Remover Botões de Rádio do Menu Lateral */
    div[data-testid="stSidebarNav"] { display: none; }
    .stRadio > div { display: none; } /* Esconde o rádio padrão */

    /* Custom Menu Items */
    .menu-item {
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        margin-bottom: 5px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #4a4e6a;
    }
    .menu-active {
        background-color: #f0f1f4;
        color: #1a1d2e;
        font-weight: 600;
        border-left: 4px solid #d4af37;
    }

    /* Botão Dourado */
    .stButton>button { 
        background-color: #d4af37 !important; 
        color: #000 !important; 
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 3em !important;
    }

    /* Tabelas */
    .stDataFrame { background: white; border-radius: 12px; border: 1px solid #e2e4ea; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE BANCOS ---
for key in ['db_users', 'db_pessoas', 'db_processos', 'menu_choice']:
    if key not in st.session_state:
        if key == 'db_users':
            st.session_state[key] = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=['Nome', 'Email', 'Documento', 'Perfil'])
        elif key == 'menu_choice': st.session_state[key] = "📋 Processos"
        else: st.session_state[key] = pd.DataFrame()

if 'user_logged' not in st.session_state: st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("Sistema C&T")
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        user_choice = st.selectbox("Usuário", st.session_state.db_users['Nome'].tolist())
        if st.button("ACESSAR"):
            st.session_state.user_logged = user_choice
            st.rerun()
    st.stop()

# --- SIDEBAR CUSTOMIZADA (SEM BOTÕES) ---
with st.sidebar:
    st.markdown(f"### ⚖️ Costa & Tavares")
    st.caption(f"Logado como: {st.session_state.user_logged}")
    st.write("---")
    
    # Simulação de Menu por Botões (Look & Feel de cliques)
    def set_menu(choice): st.session_state.menu_choice = choice

    if st.button("👥 Pessoas", key="btn_pess", use_container_width=True): set_menu("👥 Pessoas")
    if st.button("📋 Processos", key="btn_proc", use_container_width=True): set_menu("📋 Processos")
    if st.button("👤 Usuários", key="btn_user", use_container_width=True): set_menu("👤 Usuários")
    if st.button("⚙️ Configurações", key="btn_conf", use_container_width=True): set_menu("⚙️ Configurações")
    
    st.write("---")
    if st.button("Sair", type="secondary"):
        st.session_state.user_logged = None
        st.rerun()

menu = st.session_state.menu_choice

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Gestão de Pessoas")
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        if st.button("+ Cadastrar Pessoa"): st.session_state.f_p_ct = True

    if st.session_state.get('f_p_ct'):
        with st.form("f_pessoa_ct"):
            st.subheader("Novo Cadastro de Pessoa")
            n = st.text_input("Nome Completo")
            d = st.text_input("CPF ou CNPJ")
            e = st.text_input("E-mail")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("Salvar"):
                new = pd.DataFrame([[n, d, e]], columns=['Nome', 'CPF_CNPJ', 'Email'])
                st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, new], ignore_index=True)
                st.session_state.f_p_ct = False
                st.rerun()
            if c2.form_submit_button("Cancelar"):
                st.session_state.f_p_ct = False
                st.rerun()
    
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO PROCESSOS ---
elif menu == "📋 Processos":
    st.header("Carteira de Processos")
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        if st.button("+ Cadastrar Processo"): st.session_state.f_pr_ct = True

    if st.session_state.get('f_pr_ct'):
        with st.form("f_proc_ct"):
            st.subheader("Vincular Novo Processo")
            cnj = st.text_input("Número do Processo (CNJ)")
            col_v, col_c = st.columns(2)
            vara = col_v.text_input("Vara")
            comarca = col_c.text_input("Comarca")
            
            st.write("---")
            # Validação dentro do formulário para evitar erro de botão ausente
            if st.session_state.db_pessoas.empty:
                st.warning("⚠️ Atenção: É necessário cadastrar uma pessoa no módulo 'Pessoas' antes de finalizar.")
                pessoa_list = ["Nenhuma pessoa cadastrada"]
            else:
                pessoa_list = st.session_state.db_pessoas['Nome'].tolist()
            
            pessoa = st.selectbox("Pessoa", pessoa_list)
            c1, c2 = st.columns(2)
            polo = c1.selectbox("Polo no Processo", ["Polo Ativo", "Polo Passivo", "Terceiro"])
            e_cli = c2.checkbox("É Cliente do Escritório?")
            
            b1, b2 = st.columns(2)
            if b1.form_submit_button("Confirmar Cadastro"):
                if st.session_state.db_pessoas.empty:
                    st.error("Impossível salvar: Cadastre a pessoa primeiro.")
                elif not e_cli:
                    st.error("Erro: Marque quem é o cliente.")
                elif not cnj:
                    st.error("CNJ obrigatório.")
                else:
                    new_p = pd.DataFrame([[cnj, vara, comarca, pessoa, polo, "Sim" if e_cli else "Não"]], 
                                        columns=['CNJ', 'Vara', 'Comarca', 'Pessoa', 'Polo', 'Cliente'])
                    st.session_state.db_processos = pd.concat([st.session_state.db_processos, new_p], ignore_index=True)
                    st.session_state.f_pr_ct = False
                    st.rerun()
            if b2.form_submit_button("Cancelar"):
                st.session_state.f_pr_ct = False
                st.rerun()

    st.dataframe(st.session_state.db_processos, use_container_width=True)

# --- DEMAIS MÓDULOS ---
elif menu == "👤 Usuários":
    st.header("Gestão de Equipe")
    st.dataframe(st.session_state.db_users, use_container_width=True)
