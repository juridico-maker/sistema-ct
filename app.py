import streamlit as st
import pandas as pd
from anthropic import Anthropic
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema C&T - Costa & Tavares", layout="wide", page_icon="⚖️")

# --- ESTILO CLEAN C&T (INSPIRADO NO MODELO VISUAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Layout Geral */
    .main { background-color: #f5f6f8; color: #1a1d2e; }
    
    /* Sidebar Branca (Estilo Moderno) */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #e2e4ea;
    }
    
    /* Tipografia Dourada e Escura */
    h1, h2, h3 { color: #1a1d2e !important; font-weight: 700 !important; }
    .stCaption { color: #9096b4; }

    /* Botão de Ação C&T (Dourado) */
    .stButton>button { 
        background-color: #d4af37 !important; 
        color: #000 !important; 
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Tabelas e Containers */
    .stDataFrame { background: white; border-radius: 12px; border: 1px solid #e2e4ea; }
    .stTabs [aria-selected="true"] { background-color: #d4af37 !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCOS DE DADOS ---
for key in ['db_users', 'db_pessoas', 'db_processos', 'db_movimentacoes', 'db_memoria_ia']:
    if key not in st.session_state:
        if key == 'db_users':
            st.session_state[key] = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=['Nome', 'Email', 'Documento', 'Perfil'])
        else:
            st.session_state[key] = pd.DataFrame()

if 'user_logged' not in st.session_state: st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("Sistema C&T")
    st.caption("Costa & Tavares Advogados Associados")
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        user_choice = st.selectbox("Selecione seu Usuário", st.session_state.db_users['Nome'].tolist())
        if st.button("ACESSAR PAINEL"):
            st.session_state.user_logged = user_choice
            st.rerun()
    st.stop()

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### ⚖️ Costa & Tavares")
    st.caption(f"Usuário: {st.session_state.user_logged}")
    st.write("---")
    menu = st.radio("MÓDULOS", ["👥 Pessoas", "📋 Processos", "👤 Usuários", "⚙️ Configurações"])
    st.write("---")
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- MÓDULO PESSOAS ---
if menu == "👥 Pessoas":
    st.header("Gestão de Pessoas")
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        if st.button("+ Cadastrar Pessoa"): st.session_state.f_p_ct = True

    if st.session_state.get('f_p_ct'):
        with st.form("f_pessoa_ct"):
            st.subheader("Novo Cadastro")
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
            if st.session_state.db_pessoas.empty:
                st.warning("⚠️ É necessário cadastrar uma pessoa primeiro.")
            else:
                pessoa = st.selectbox("Pessoa", st.session_state.db_pessoas['Nome'].tolist())
                c1, c2 = st.columns(2)
                polo = c1.selectbox("Polo no Processo", ["Polo Ativo", "Polo Passivo", "Terceiro"])
                e_cli = c2.checkbox("É Cliente do Escritório?")
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("Confirmar Cadastro"):
                    if not e_cli: st.error("Erro: É obrigatório identificar pelo menos um cliente.")
                    elif not cnj: st.error("Erro: CNJ obrigatório.")
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

# --- MÓDULO USUÁRIOS ---
elif menu == "👤 Usuários":
    st.header("Gestão de Equipe")
    if st.button("+ Cadastrar Usuário"): st.session_state.f_u_ct = True
    if st.session_state.get('f_u_ct'):
        with st.form("f_u_ct"):
            n, e, d = st.columns(3)
            un = n.text_input("Nome")
            ue = e.text_input("Email")
            ud = d.text_input("CPF/CNPJ")
            perf = st.selectbox("Perfil", ["Advogado", "Admin", "Estagiário"])
            if st.form_submit_button("Salvar"):
                nu = pd.DataFrame([[un, ue, ud, perf]], columns=['Nome', 'Email', 'Documento', 'Perfil'])
                st.session_state.db_users = pd.concat([st.session_state.db_users, nu], ignore_index=True)
                st.session_state.f_u_ct = False
                st.rerun()
    st.dataframe(st.session_state.db_users, use_container_width=True)
