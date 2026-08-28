import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Simulador de Agendamento - DRS Group", layout="wide")

st.title("🚚 DRS Group - Célula 03 (BMS)")
st.subheader("Simulador de Atualização Automática via IA")

# Inicializa a base de dados na memória para o teste
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame([
        {"Chamado": "25807", "Protocolo": "CA266-0002", "Cliente": "BMS", "Centro": "LIGA NORTE RIOGRANDENSE", "Status": "Agendamento", "Sub Status": "Aguardando Agendamento via IA", "Comprovante Salvo": "Não"}
    ])

# Exibe o status atual do gerenciamento
st.markdown("### 📋 Painel de Gerenciamento (Visão Atual)")
st.dataframe(st.session_state.dados, use_container_width=True)

st.divider()

# Área de simulação da resposta do centro
st.markdown("### ✉️ Simular Resposta do Centro de Pesquisa")
col1, col2 = st.columns(2)

with col1:
    chamado_sel = st.selectbox("Selecione o Chamado:", st.session_state.dados["Chamado"])
    data_confirmada = st.date_input("Data Confirmada pelo Centro:")

with col2:
    horario_confirmado = st.selectbox("Horário Confirmado:", ["08h às 12h", "13h às 17h", "08h às 17h"])
    btn_simular = st.button("🚀 Simular Resposta da IA", type="primary")

# Ação da automação
if btn_simular:
    with st.spinner("IA processando resposta do e-mail e atualizando sistema..."):
        time.sleep(2) # Simula o tempo de processamento da IA
        
        # Atualiza o status e sub status automaticamente
        idx = st.session_state.dados.index[st.session_state.dados["Chamado"] == chamado_sel][0]
        st.session_state.dados.at[idx, "Status"] = "Documentação"
        st.session_state.dados.at[idx, "Sub Status"] = "Aguardando documentação"
        st.session_state.dados.at[idx, "Comprovante Salvo"] = "Sim (PDF/E-mail em Nuvem)"
        
    st.success("✅ Processo concluído com sucesso!")
    st.rerun()
