import streamlit as st
import pandas as pd
from anthropic import Anthropic
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema C&T", layout="wide", page_icon="⚖️")

# --- ESTILO CLEAN C&T V4 (SEM RADIO BUTTONS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #f5f6f8; color: #1a1d2e; }
    
    /* Sidebar Estilo JurisFlow */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e4ea; }
    
    /* Custom Sidebar Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border: none !important;
        padding: 10px 15px !important;
    }
    
    /* Botão Dourado de Ação */
    .btn-acao > div > button {
        background-color: #d4af37 !important;
        color: #000 !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    /* Tabelas e Inputs */
    .stDataFrame { background: white; border-radius: 12px; border: 1px solid #e2e4ea; }
    input { border-radius: 8px !important; }
    
    /* Alerta Amarelo Moderno */
    .stAlert { border-radius: 10px !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS PRÉVIOS (TRIBUNAIS E ÓRGÃOS) ---
TRIBUNAIS = ["STF", "STJ", "TST", "TSE", "STM", "TJMG", "TJSP", "TJRJ", "TJBA", "TJPR", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "TRF6"]
TIPOS_ORGAO = ["Vara Cível", "Vara de Família", "Vara de Sucessões", "Vara Criminal", "Vara do Trabalho", "Câmara Cível", "Turma Recursal", "Órgão Especial"]
COMARCAS_EXEMPLO = ["Belo Horizonte", "Contagem", "Betim", "Nova Lima", "São Paulo", "Rio de Janeiro", "Curitiba", "Salvador"] # Lista expandível

# --- INICIALIZAÇÃO DE BANCOS ---
for key in ['db_users', 'db_pessoas', 'db_processos', 'menu_choice']:
    if key not in st.session_state:
        if key == 'db_users':
            st.session_state[key] = pd.DataFrame([['Alexandre (Admin)', 'alexandre@ct.adv.br', '000.000.000-00', 'Admin']], columns=['Nome', 'Email', 'Documento', 'Perfil'])
        elif key == 'menu_choice': st.session_state[key] = "📋 Processos"
        else: st.session_state[key] = pd.DataFrame()

if 'user_logged' not in st.session_state: st.session_state.user_logged = None

# --- SIDEBAR NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### ⚖️ Costa & Tavares")
    st.caption(f"Usuário: {st.session_state.user_logged}")
    st.write("---")
    
    if st.button("👥 Pessoas", use_container_width=True): st.session_state.menu_choice = "👥 Pessoas"
    if st.button("📋 Processos", use_container_width=True): st.session_state.menu_choice = "📋 Processos"
    if st.button("👤 Usuários", use_container_width=True): st.session_state.menu_choice = "👤 Usuários"
    if st.button("⚙️ Configurações", use_container_width=True): st.session_state.menu_choice = "⚙️ Configurações"
    
    st.write("---")
    if st.button("Sair", type="secondary"):
        st.session_state.user_logged = None
        st.rerun()

menu = st.session_state.menu_choice

# --- MÓDULO PROCESSOS ---
if menu == "📋 Processos":
    st.header("Carteira de Processos")
    
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        st.markdown('<div class="btn-acao">', unsafe_allow_html=True)
        if st.button("+ Cadastrar Processo"): st.session_state.f_pr_ct = True
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get('f_pr_ct'):
        with st.form("f_proc_complexo"):
            st.subheader("Vincular Novo Processo")
            
            # Número CNJ com máscara sugerida
            cnj = st.text_input("Número do Processo (CNJ)", placeholder="0000000-00.0000.0.00.0000")
            
            c1, c2, c3 = st.columns([1, 1, 1])
            tribunal = c1.selectbox("Tribunal", TRIBUNAIS)
            comarca = c2.selectbox("Comarca", COMARCAS_EXEMPLO) # Aqui no futuro carregamos a lista completa de 5k cidades
            instancia = c3.selectbox("Instância", ["1ª Instância", "2ª Instância", "Tribunais Superiores"])
            
            # Sub-itens de Instância
            sub_inst = ""
            if instancia == "1ª Instância":
                sub_inst = st.radio("Tipo de Juízo", ["Comum", "Juizado Especial"], horizontal=True)
            elif instancia == "2ª Instância":
                sub_inst = st.radio("Tipo de Órgão", ["Tribunal", "Turma Recursal"], horizontal=True)

            st.write("---")
            st.write("**Órgão Julgador**")
            c_o1, c_o2 = st.columns([1, 2])
            num_orgao = c_o1.text_input("Número (ex: 2ª, 5ª...)")
            tipo_orgao = c_o2.selectbox("Tipo de Órgão", TIPOS_ORGAO)
            
            st.write("---")
            if st.session_state.db_pessoas.empty:
                st.warning("⚠️ Atenção: É necessário cadastrar uma pessoa no módulo 'Pessoas' antes de finalizar.")
                p_vinculo = "Nenhuma cadastrada"
            else:
                p_vinculo = st.selectbox("Vincular Pessoa", st.session_state.db_pessoas['Nome'].tolist())
            
            col_p1, col_p2 = st.columns(2)
            polo = col_p1.selectbox("Polo no Processo", ["Polo Ativo", "Polo Passivo", "Terceiro"])
            e_cli = col_p2.checkbox("É Cliente do Escritório?")

            cb1, cb2 = st.columns(2)
            if cb1.form_submit_button("Confirmar Cadastro"):
                if not cnj or p_vinculo == "Nenhuma cadastrada" or not e_cli:
                    st.error("Verifique os campos obrigatórios (CNJ, Pessoa e Marcação de Cliente).")
                else:
                    new_data = pd.DataFrame([[cnj, tribunal, comarca, instancia, f"{num_orgao} {tipo_orgao}", p_vinculo, polo]], 
                                           columns=['CNJ', 'Tribunal', 'Comarca', 'Instância', 'Órgão', 'Pessoa', 'Polo'])
                    st.session_state.db_processos = pd.concat([st.session_state.db_processos, new_data], ignore_index=True)
                    st.session_state.f_pr_ct = False
                    st.rerun()
            if cb2.form_submit_button("Cancelar"):
                st.session_state.f_pr_ct = False
                st.rerun()

    st.dataframe(st.session_state.db_processos, use_container_width=True)

# --- MÓDULO PESSOAS (LISTA PRIMEIRO) ---
elif menu == "👥 Pessoas":
    st.header("Gestão de Pessoas")
    if st.button("+ Cadastrar Pessoa"): st.session_state.f_p_ct = True
    if st.session_state.get('f_p_ct'):
        with st.form("f_p"):
            n = st.text_input("Nome")
            d = st.text_input("CPF/CNPJ")
            e = st.text_input("Email")
            if st.form_submit_button("Salvar"):
                new_p = pd.DataFrame([[n, d, e]], columns=['Nome', 'CPF_CNPJ', 'Email'])
                st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, new_p], ignore_index=True)
                st.session_state.f_p_ct = False
                st.rerun()
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)

# --- MÓDULO CONFIGURAÇÕES (EDITAR LISTAS) ---
elif menu == "⚙️ Configurações":
    st.header("Configurações do Sistema")
    with st.expander("Editar Listas de Tribunais e Órgãos"):
        st.write("Em breve: Alexandre poderá adicionar/remover itens das listas de seleção aqui.")
