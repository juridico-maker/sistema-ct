import streamlit as st
import pandas as pd
from anthropic import Anthropic
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="C&T Enterprise - Gestão Jurídica", layout="wide", page_icon="⚖️")

# --- ESTILO CUSTOMIZADO (NAVY & GOLD) ---
st.markdown("""
    <style>
    /* Fundo e Texto Geral */
    .main { background-color: #001f3f; color: #fdfdfd; }
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #00152b; border-right: 3px solid #d4af37; }
    /* Títulos e Métricas */
    h1, h2, h3, .stMetric { color: #d4af37 !important; font-family: 'serif'; }
    /* Botões */
    .stButton>button { 
        background-color: #d4af37; color: #001f3f; 
        font-weight: bold; border-radius: 5px; 
        border: 1px solid #d4af37; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #b8962e; color: white; }
    /* Inputs */
    input { background-color: #002b55 !important; color: white !important; border: 1px solid #d4af37 !important; }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #002b55; border: 1px solid #d4af37; 
        border-radius: 5px 5px 0 0; color: white; padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS (PERSISTÊNCIA EM SESSÃO) ---
if 'db_pessoas' not in st.session_state:
    st.session_state.db_pessoas = pd.DataFrame(columns=['ID', 'Nome', 'CPF_CNPJ', 'Papel'])
if 'db_processos' not in st.session_state:
    st.session_state.db_processos = pd.DataFrame(columns=['CNJ', 'Cliente', 'Assunto', 'Status', 'Data_Cad'])
if 'db_movimentacoes' not in st.session_state:
    st.session_state.db_movimentacoes = pd.DataFrame(columns=['CNJ', 'Data', 'Titulo', 'Descricao', 'IA_Analise'])
if 'user_logged' not in st.session_state:
    st.session_state.user_logged = None

# --- LOGIN ---
if not st.session_state.user_logged:
    st.title("⚖️ Costa & Tavares - Acesso Restrito")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        # Tentativa de carregar logo local, se não houver, usa ícone
        st.write("### Identificação de Usuário")
        user = st.selectbox("Usuário", ["Alexandre (Admin)", "Vinícius", "Bruna", "Naira"])
        senha = st.text_input("Senha", type="password")
        if st.button("ACESSAR SISTEMA"):
            st.session_state.user_logged = user
            st.rerun()
    st.stop()

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4140/4140037.png", width=100) # Logo temporária elegante
    st.title("Painel C&T")
    st.write(f"Conectado: **{st.session_state.user_logged}**")
    menu = st.radio("Módulos:", ["🏠 Dashboard", "👥 Pessoas", "📋 Processos", "🤖 IA Estratégica", "⚙️ Configurações"])
    if st.button("Sair"):
        st.session_state.user_logged = None
        st.rerun()

# --- 1. DASHBOARD ---
if menu == "🏠 Dashboard":
    st.header("Resumo Operacional")
    c1, c2, c3 = st.columns(3)
    c1.metric("Processos Ativos", len(st.session_state.db_processos))
    c2.metric("Pessoas Cadastradas", len(st.session_state.db_pessoas))
    c3.metric("Análises de IA", len(st.session_state.db_movimentacoes[st.session_state.db_movimentacoes['IA_Analise'] != ""]))

# --- 2. MÓDULO PESSOAS (COM DEDUPLICAÇÃO) ---
elif menu == "👥 Pessoas":
    st.header("Cadastro Centralizado de Pessoas")
    with st.expander("➕ Nova Pessoa (Cliente ou Parte)"):
        with st.form("form_pessoa"):
            p_nome = st.text_input("Nome Completo")
            p_doc = st.text_input("CPF ou CNPJ (Obrigatório)")
            p_papel = st.selectbox("Papel Principal", ["Cliente", "Parte Contrária", "Terceiro"])
            if st.form_submit_button("Cadastrar"):
                if p_doc in st.session_state.db_pessoas['CPF_CNPJ'].values:
                    st.error("Erro: Este CPF/CNPJ já consta no sistema.")
                elif p_nome and p_doc:
                    nova_p = pd.DataFrame([[len(st.session_state.db_pessoas)+1, p_nome, p_doc, p_papel]], 
                                         columns=st.session_state.db_pessoas.columns)
                    st.session_state.db_pessoas = pd.concat([st.session_state.db_pessoas, nova_p], ignore_index=True)
                    st.success("Pessoa cadastrada com sucesso!")
                else:
                    st.warning("Preencha Nome e Documento.")
    st.table(st.session_state.db_pessoas)

# --- 3. MÓDULO PROCESSOS (AUTOCOMPLETE E MOVIMENTAÇÕES) ---
elif menu == "📋 Processos":
    st.header("Gestão de Processos")
    
    aba_cad, aba_mov = st.tabs(["📂 Cadastro/Lista", "⚡ Movimentações e IA"])
    
    with aba_cad:
        with st.expander("🆕 Vincular Novo Processo"):
            if st.session_state.db_pessoas.empty:
                st.info("Cadastre uma Pessoa antes de criar um processo.")
            else:
                with st.form("form_proc"):
                    cnj = st.text_input("Número CNJ (Deduplicação automática)")
                    # AUTOCOMPLETE: Puxa nomes da base de pessoas
                    cliente_opt = st.selectbox("Vincular Cliente (Autocomplete)", st.session_state.db_pessoas['Nome'].tolist())
                    assunto = st.text_input("Assunto/Tese")
                    if st.form_submit_button("Vincular Processo"):
                        if cnj in st.session_state.db_processos['CNJ'].values:
                            st.error("Este CNJ já está cadastrado.")
                        else:
                            novo_p = pd.DataFrame([[cnj, cliente_opt, assunto, "Ativo", datetime.date.today()]], 
                                                 columns=st.session_state.db_processos.columns)
                            st.session_state.db_processos = pd.concat([st.session_state.db_processos, novo_p], ignore_index=True)
                            st.success("Processo vinculado!")
        st.dataframe(st.session_state.db_processos, use_container_width=True)

    with aba_mov:
        if st.session_state.db_processos.empty:
            st.warning("Nenhum processo disponível.")
        else:
            proc_sel = st.selectbox("Selecione o Processo para atualizar:", st.session_state.db_processos['CNJ'].tolist())
            with st.form("form_mov"):
                titulo_mov = st.text_input("Título da Movimentação (ex: Despacho Proferido)")
                desc_mov = st.text_area("Descrição do Ato")
                usar_ia = st.checkbox("🔮 Acionar IA Estratégica para sugerir próximo passo")
                
                if st.form_submit_button("Registrar Movimentação"):
                    analise_ia = ""
                    if usar_ia:
                        try:
                            client = Anthropic(api_key=st.secrets["CLAUDE_KEY"])
                            prompt = f"Movimentação: {titulo_mov}. Conteúdo: {desc_mov}. Sugira o próximo passo jurídico estratégico para o escritório Costa & Tavares."
                            resp = client.messages.create(
                                model="claude-3-5-sonnet-20240620", max_tokens=500,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            analise_ia = resp.content[0].text
                        except: analise_ia = "Erro ao conectar com a IA."
                    
                    nova_m = pd.DataFrame([[proc_sel, datetime.date.today(), titulo_mov, desc_mov, analise_ia]], 
                                         columns=st.session_state.db_movimentacoes.columns)
                    st.session_state.db_movimentacoes = pd.concat([st.session_state.db_movimentacoes, nova_m], ignore_index=True)
                    st.success("Movimentação registrada!")
            
            # Exibe histórico do processo
            st.write("### Histórico de Movimentações")
            hist = st.session_state.db_movimentacoes[st.session_state.db_movimentacoes['CNJ'] == proc_sel]
            for i, row in hist.iterrows():
                with st.expander(f"{row['Data']} - {row['Titulo']}"):
                    st.write(row['Descricao'])
                    if row['IA_Analise']:
                        st.warning(f"💡 **Sugestão IA:** {row['IA_Analise']}")

# --- 4. IA ESTRATÉGICA E CONFIGS (ADMIN) ---
elif menu == "🤖 IA Estratégica":
    st.header("Consultoria Jurídica de Inteligência")
    st.info("Este chat tem memória do processo selecionado.")
    # Lógica de Chat contínuo aqui...

elif menu == "⚙️ Configurações":
    if "Admin" in st.session_state.user_logged:
        st.header("Configurações do Sistema C&T")
        st.text_input("Identidade do Escritório", "Costa & Tavares Advogados Associados")
        st.color_picker("Cor Primária", "#001f3f")
        st.color_picker("Cor Secundária", "#d4af37")
        st.write("---")
        st.write("Configurações de IA e Prompt de Sistema editáveis em breve.")
    else:
        st.error("Acesso permitido apenas para Alexandre (Admin).")
