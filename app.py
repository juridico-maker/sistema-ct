import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema C&T", layout="wide", page_icon="⚖️")

# --- ESTILO CLEAN V4 (MODELO JURISFLOW) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #f5f6f8; color: #1a1d2e; }
    
    /* Sidebar Limpa */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e4ea; }
    
    /* Remover indicadores de rádio e botões feios */
    [data-testid="stSidebarNav"] { display: none; }
    .stRadio > div { display: none !important; } 

    /* Botões do Menu Lateral */
    .stButton > button {
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border: none !important;
        padding: 12px 20px !important;
        background-color: transparent !important;
        color: #4a4e6a !important;
        width: 100% !important;
        transition: 0.2s;
    }
    .stButton > button:hover { background-color: #f0f1f4 !important; color: #1a1d2e !important; }
    
    /* Botão de Ação Dourado */
    .btn-salvar > div > button {
        background-color: #d4af37 !important;
        color: #000 !important;
        font-weight: 700 !important;
        width: 100% !important;
    }

    /* Inputs Modernos */
    .stTextInput>div>div>input, .stSelectbox>div>div>div { 
        background-color: #ffffff !important; 
        border: 1px solid #d0d3dc !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LISTAS PRÉ-CADASTRADAS ---
TRIBUNAIS = ["STF", "STJ", "TST", "TSE", "STM", "TJMG", "TJSP", "TJRJ", "TJBA", "TJPR", "TJRS", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "TRF6"]
ORGAOS_TIPOS = ["Vara Cível", "Vara de Família", "Vara de Sucessões", "Vara Criminal", "Vara de Fazenda Pública", "Vara do Trabalho", "Câmara Cível", "Turma Recursal", "Órgão Especial"]
COMARCAS = ["Belo Horizonte", "Contagem", "Betim", "Nova Lima", "Ribeirão das Neves", "Sabará", "Uberlândia", "Juiz de Fora", "São Paulo", "Rio de Janeiro"]

# --- INICIALIZAÇÃO DE DADOS ---
if 'db_pessoas' not in st.session_state: st.session_state.db_pessoas = pd.DataFrame(columns=['Nome', 'CPF_CNPJ', 'Email'])
if 'db_processos' not in st.session_state: st.session_state.db_processos = pd.DataFrame(columns=['CNJ', 'Tribunal', 'Instância', 'Comarca', 'Órgão', 'Pessoa', 'Polo', 'Cliente'])
if 'menu_ct' not in st.session_state: st.session_state.menu_ct = "📋 Processos"
if 'user_logged' not in st.session_state: st.session_state.user_logged = "Alexandre (Admin)"

# --- SIDEBAR NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### ⚖️ Costa & Tavares")
    st.caption(f"Usuário: {st.session_state.user_logged}")
    st.write("---")
    
    if st.button("👥 Pessoas"): st.session_state.menu_ct = "👥 Pessoas"
    if st.button("📋 Processos"): st.session_state.menu_ct = "📋 Processos"
    if st.button("👤 Usuários"): st.session_state.menu_ct = "👤 Usuários"
    if st.button("⚙️ Configurações"): st.session_state.menu_ct = "⚙️ Configurações"
    
    st.write("---")
    st.button("Sair", type="secondary")

menu = st.session_state.menu_ct

# --- MÓDULO PROCESSOS ---
if menu == "📋 Processos":
    st.header("Carteira de Processos")
    
    col_t, col_b = st.columns([5, 1.2])
    with col_b:
        if st.button("+ Cadastrar Processo"): st.session_state.f_proc = True

    if st.session_state.get('f_proc'):
        with st.form("form_processo_ct"):
            st.subheader("Vincular Novo Processo")
            
            cnj = st.text_input("Número do Processo (CNJ)", placeholder="0000000-00.0000.0.00.0000")
            
            c1, c2, c3 = st.columns(3)
            tribunal = c1.selectbox("Tribunal", TRIBUNAIS)
            instancia = c2.selectbox("Instância", ["1ª Instância", "2ª Instância", "Tribunais Superiores"])
            comarca = c3.selectbox("Comarca", COMARCAS) # Autocomplete funcional pelo selectbox
            
            # Detalhamento de Instância
            detalhe_inst = ""
            if instancia == "1ª Instância":
                detalhe_inst = st.radio("Tipo de Juízo", ["Comum", "Juizado Especial"], horizontal=True)
            elif instancia == "2ª Instância":
                detalhe_inst = st.radio("Tipo de Órgão", ["Tribunal", "Turma Recursal"], horizontal=True)

            st.write("---")
            st.write("**Órgão Julgador**")
            o1, o2 = st.columns([1, 2])
            num_orgao = o1.text_input("Número (ex: 2ª, 15ª)")
            tipo_orgao = o2.selectbox("Órgão Julgado", ORGAOS_TIPOS)
            
            st.write("---")
            st.write("**Partes e Vínculo**")
            if st.session_state.db_pessoas.empty:
                st.warning("⚠️ Atenção: É necessário cadastrar uma pessoa no módulo 'Pessoas' antes de finalizar.")
                p_nome = "Nenhuma pessoa cadastrada"
            else:
                p_nome = st.selectbox("Pessoa Vinculada", st.session_state.db_pessoas['Nome'].tolist())
            
            cp1, cp2 = st.columns(2)
            polo = cp1.selectbox("Polo no Processo", ["Polo Ativo", "Polo Passivo", "Terceiro"])
            e_cliente = cp2.checkbox("Marcar como Cliente do Escritório")

            st.markdown('<div class="btn-salvar">', unsafe_allow_html=True)
            cb1, cb2 = st.columns(2)
            if cb1.form_submit_button("CONFIRMAR CADASTRO"):
                if not cnj: st.error("Erro: Número CNJ é obrigatório.")
                elif st.session_state.db_pessoas.empty: st.error("Erro: Cadastre a pessoa primeiro.")
                elif not e_cliente: st.error("Erro: É obrigatório marcar pelo menos um cliente.")
                else:
                    new_pr = pd.DataFrame([[cnj, tribunal, instancia, comarca, f"{num_orgao} {tipo_orgao}", p_nome, polo, "Sim" if e_cliente else "Não"]], 
                                         columns=['CNJ', 'Tribunal', 'Instância', 'Comarca', 'Órgão', 'Pessoa', 'Polo', 'Cliente'])
                    st.session_state.db_processos = pd.concat([st.session_state.db_processos, new_pr], ignore_index=True)
                    st.session_state.f_proc = False
                    st.rerun()
            if cb2.form_submit_button("CANCELAR"):
                st.session_state.f_proc = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.dataframe(st.session_state.db_processos, use_container_width=True)

# --- MÓDULO PESSOAS ---
elif menu == "👥 Pessoas":
    st.header("Gestão de Pessoas")
    if st.button("+ Cadastrar Pessoa"): st.session_state.f_pess = True
    if st.session_state.get('f_pess'):
        with st.form("f_pess_ct"):
            n = st.text_input("Nome")
            d = st.text_input("CPF ou CNPJ")
            if st.form_submit_button("SALVAR"):
                st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, pd.DataFrame([[n, d, ""]], columns=['Nome', 'CPF_CNPJ', 'Email'])], ignore_index=True)
                st.session_state.f_pess = False
                st.rerun()
    st.dataframe(st.session_state.db_pessoas, use_container_width=True)
