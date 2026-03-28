import streamlit as st
import pandas as pd
from anthropic import Anthropic
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JurisFlow C&T", layout="wide", page_icon="⚖️")

# --- ESTILO JURISFLOW (CLEAN & MODERN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Fundo Principal */
    .main { background-color: #f5f6f8; color: #1a1d2e; }
    
    /* Menu Lateral Claro */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #e2e4ea;
    }
    
    /* Títulos Clean */
    h1, h2, h3 { color: #1a1d2e !important; font-weight: 700 !important; letter-spacing: -0.5px; }

    /* Botão Principal Dourado (Ação) */
    .stButton>button { 
        background-color: #d4af37 !important; 
        color: #000 !important; 
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(212,175,55,0.3); }

    /* Inputs Modernos */
    .stTextInput>div>div>input, .stSelectbox>div>div>div { 
        background-color: #ffffff !important; 
        color: #1a1d2e !important; 
        border: 1px solid #d0d3dc !important;
        border-radius: 8px !important;
    }

    /* Cards e Tabelas */
    .stDataFrame { border: 1px solid #e2e4ea; border-radius: 12px; background: white; }
    
    /* Tabs Customizadas */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #fff; border: 1px solid #e2e4ea; 
        border-radius: 20px; color: #4a4e6a; padding: 5px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #3a5fe5 !important; color: white !important; border-color: #3a5fe5 !important; }

    /* Badge Cliente */
    .badge-cliente {
        background-color: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE BANCOS ---
for key in ['db_users', 'db_pessoas', 'db_processos', 'db_movimentacoes', 'db_memoria_ia']:
    if key not in st.session_state:
        if key == 'db_users':
            st.session_state[key] = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=['Nome', 'Email', 'Documento', 'Perfil'])
        else:
            st.session_state[key] = pd.DataFrame()

if 'user_logged' not in st.session_state: st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("JurisFlow")
    st.caption("Costa & Tavares Advogados")
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        user_choice = st.selectbox("Acesso Profissional", st.session_state.db_users['Nome'].tolist())
        if st.button("ENTRAR"):
            st.session_state.user_logged = user_choice
            st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ◈ JurisFlow")
    st.caption("Sistema Operacional")
    st.write("---")
    menu = st.radio("MENU", ["◈ Dashboard", "👥 Pessoas", "⊟ Processos", "👤 Usuários"])
    st.write("---")
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Pessoas")
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        if st.button("+ Cadastrar Pessoa"): st.session_state.f_p = True

    if st.session_state.get('f_p'):
        with st.form("f_pessoa"):
            st.subheader("Nova Pessoa")
            n = st.text_input("Nome Completo")
            d = st.text_input("CPF ou CNPJ")
            e = st.text_input("E-mail")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("Salvar"):
                new = pd.DataFrame([[n, d, e]], columns=['Nome', 'CPF_CNPJ', 'Email'])
                st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, new], ignore_index=True)
                st.session_state.f_p = False
                st.rerun()
            if c2.form_submit_button("Cancelar"):
                st.session_state.f_p = False
                st.rerun()
    
    st.write("### Base de Dados")
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO PROCESSOS ---
elif menu == "⊟ Processos":
    st.header("Processos")
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        if st.button("+ Novo Processo"): st.session_state.f_pr = True

    if st.session_state.get('f_pr'):
        with st.form("f_proc"):
            st.subheader("Vincular Processo")
            cnj = st.text_input("Número do Processo (CNJ)")
            col1, col2 = st.columns(2)
            vara = col1.text_input("Vara")
            com = col2.text_input("Comarca")
            
            st.write("---")
            if st.session_state.db_pessoas.empty:
                st.warning("⚠️ Cadastre uma pessoa primeiro.")
            else:
                pessoa = st.selectbox("Pessoa Vinculada", st.session_state.db_pessoas['Nome'].tolist())
                c1, c2 = st.columns(2)
                polo = c1.selectbox("Polo no Processo", ["Polo Ativo", "Polo Passivo", "Terceiro"])
                e_cli = c2.checkbox("É Cliente?")
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("Salvar Processo"):
                    if not e_cli: st.error("Obrigatório marcar pelo menos um cliente.")
                    else:
                        new_p = pd.DataFrame([[cnj, vara, com, pessoa, polo, "Sim" if e_cli else "Não"]], 
                                            columns=['CNJ', 'Vara', 'Comarca', 'Pessoa', 'Polo', 'Cliente'])
                        st.session_state.db_processos = pd.concat([st.session_state.db_processos, new_p], ignore_index=True)
                        st.session_state.f_pr = False
                        st.rerun()
                if b2.form_submit_button("Cancelar"):
                    st.session_state.f_pr = False
                    st.rerun()

    st.write("### Carteira")
    st.dataframe(st.session_state.db_processos, use_container_width=True)

# --- MÓDULO USUÁRIOS ---
elif menu == "👤 Usuários":
    st.header("Usuários")
    if st.button("+ Novo Usuário"): st.session_state.f_u = True
    if st.session_state.get('f_u'):
        with st.form("f_u"):
            n, e, d = st.columns(3)
            un = n.text_input("Nome")
            ue = e.text_input("Email")
            ud = d.text_input("Documento")
            perf = st.selectbox("Perfil", ["Advogado", "Admin", "Estagiário"])
            if st.form_submit_button("Salvar"):
                nu = pd.DataFrame([[un, ue, ud, perf]], columns=['Nome', 'Email', 'Documento', 'Perfil'])
                st.session_state.db_users = pd.concat([st.session_state.db_users, nu], ignore_index=True)
                st.session_state.f_u = False
                st.rerun()
    st.dataframe(st.session_state.db_users, use_container_width=True)

# --- DASHBOARD ---
elif menu == "◈ Dashboard":
    st.header("Dashboard Operacional")
    st.write("Bem-vindo ao JurisFlow, Alexandre.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Processos", len(st.session_state.db_processos))
    c2.metric("Pessoas", len(st.session_state.db_pessoas))
    c3.metric("Usuários", len(st.session_state.db_users))
