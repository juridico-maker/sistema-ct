import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="C&T - Sistema Jurídico", page_icon="⚖️", layout="wide")

# --- ESTILO C&T (PRETO E DOURADO) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #d4af37; color: black; font-weight: bold; border-radius: 5px; border: none; }
    .stTextInput>div>div>input { background-color: #262626; color: white; border: 1px solid #d4af37; }
    h1, h2, h3 { color: #d4af37 !important; }
    div[data-testid="stExpander"] { border: 1px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA (SEGURA) ---
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    # Busca o modelo disponível automaticamente (como fizemos no Colab)
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("Erro na Chave API. Configure os Secrets no Streamlit Cloud.")

# --- FUNÇÃO WORD ---
def gerar_docx(texto):
    doc = Document()
    doc.add_heading('COSTA & TAVARES ADVOGADOS ASSOCIADOS', 0)
    doc.add_paragraph(texto)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
st.title("⚖️ Sistema C&T - Inteligência Jurídica")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.header("Painel Costa & Tavares")
    st.info("Sistema Online Ativo")

col1, col2 = st.columns(2)
with col1:
    cliente = st.text_input("Nome do Cliente")
    assunto = st.text_input("Assunto (Ex: Indenizatória)")
with col2:
    tipo_peca = st.selectbox("Tipo de Peça", ["Petição Inicial", "Contestação", "Réplica", "Recurso"])
    cnj = st.text_input("Processo CNJ")

fatos = st.text_area("Descrição do Caso e Teses", height=150)

if st.button("ANALISAR E REDIGIR PEÇA"):
    with st.spinner("O Agente C&T está processando..."):
        prompt = f"Advogado C&T. Caso: {assunto}. Peça: {tipo_peca}. Fatos: {fatos}. Redija a minuta."
        response = model.generate_content(prompt)
        minuta = response.text
        
        st.subheader("📄 Minuta Sugerida")
        st.write(minuta)
        
        docx = gerar_docx(minuta)
        st.download_button(
            label="📥 BAIXAR EM WORD (.DOCX)",
            data=docx,
            file_name=f"C&T_{cliente}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
