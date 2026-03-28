# --- MÓDULO IA ESTRATÉGICA (AGENTE C&T) ---
elif menu == "🤖 IA Estratégica":
    st.header("Agente Estratégico Costa & Tavares")
    
    # Seleção do Processo para Contexto
    if st.session_state.db_processos.empty:
        st.warning("Cadastre um processo no módulo '📋 Processos' para iniciar a análise.")
    else:
        proc_selecionado = st.selectbox("Selecione o Processo para Análise:", st.session_state.db_processos['CNJ'].tolist())
        
        # Recupera dados do processo selecionado para o Contexto
        dados_proc = st.session_state.db_processos[st.session_state.db_processos['CNJ'] == proc_selecionado].iloc[0]
        
        st.info(f"📌 **Contexto Atual:** Cliente {dados_proc['Cliente']} | Assunto: {dados_proc['Assunto']} | Status: {dados_proc['Status']}")

        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt_user := st.chat_input("Como posso ajudar nesta estratégia?"):
            st.session_state.messages.append({"role": "user", "content": prompt_user})
            with st.chat_message("user"):
                st.markdown(prompt_user)

            with st.chat_message("assistant"):
                # MONTAGEM DO CONTEXTO PARA O SISTEMA
                contexto_completo = f"""
                Você é o Agente de IA Estratégica do escritório Costa & Tavares.
                DADOS DO PROCESSO ATUAL:
                - CNJ: {dados_proc['CNJ']}
                - CLIENTE: {dados_proc['Cliente']}
                - ASSUNTO: {dados_proc['Assunto']}
                - STATUS: {dados_proc['Status']}
                - RESPONSÁVEL: {dados_proc['Advogado']}
                
                HISTÓRICO E DIRETRIZES:
                Analise os fatos com rigor técnico jurídico. Sugira próximos passos, identifique riscos e ajude na redação de teses.
                O usuário perguntou: {prompt_user}
                """
                
                # Chamada do Motor do Sistema (Anthropic ou Gemini)
                try:
                    # Usando a conexão que já configuramos nos Secrets
                    client = Anthropic(api_key=st.secrets["CLAUDE_KEY"])
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=2000,
                        system="Você é um advogado sênior da Costa & Tavares. Seja direto, técnico e estratégico.",
                        messages=[{"role": "user", "content": contexto_completo}]
                    )
                    full_response = response.content[0].text
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Erro de Conexão com o Motor do Sistema: {e}")
