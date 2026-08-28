import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerenciador de Loggers & Delivery - DRS / BMS", layout="wide")

st.title("📦 Gerenciador de Loggers por Delivery")
st.subheader("BMS - Baixa Automática de Palete e Identificação de Estoque")

# Inicializa banco de dados na memória do site
if "df_loggers" not in st.session_state:
    st.session_state.df_loggers = None

# Upload inicial da base do Excel (feito apenas uma vez ou quando atualizar o estoque)
if st.session_state.df_loggers is None:
    file_upload = st.file_uploader("Carregue a planilha DADOS BMS.xlsx para iniciar o sistema", type=["xlsx", "xls"])
    if file_upload:
        df = pd.read_excel(file_upload, sheet_name="loggers")
        df["Descricao"] = df["Descricao"].astype(str).str.strip()
        df["Restricao"] = df["Restricao"].astype(str).str.strip()
        df["Palete"] = df["Palete"].astype(str).str.strip()
        df["Identificacao Estoque"] = df["Identificacao Estoque"].astype(str).str.strip()
        df["Série"] = df["Série"].astype(str).str.strip()
        df["Status_Uso"] = "DISPONÍVEL"
        df["Delivery_Atribuido"] = ""
        st.session_state.df_loggers = df
        st.rerun()

if st.session_state.df_loggers is not None:
    df = st.session_state.df_loggers

    # Botão para recarregar nova planilha se precisar
    with st.sidebar:
        st.header("⚙️ Configurações")
        if st.button("🔄 Reiniciar / Carregar Nova Planilha"):
            st.session_state.df_loggers = None
            st.rerun()

    # Campo obrigatorio do DELIVERY da Packing List
    st.markdown("### 1️⃣ Informe o DELIVERY da Packing List")
    delivery_input = st.text_input("Digite ou cole o número do DELIVERY aqui:", placeholder="Ex: DEL-99887766")

    st.markdown("---")
    st.markdown("### 2️⃣ Escolha a Categoria e Selecione o Logger")

    # Filtra apenas itens LIBERADOS e DISPONÍVEIS
    df_liberados = df[(df["Restricao"] == "LIBERADO") & (df["Status_Uso"] == "DISPONÍVEL")]

    categorias = [
        "TAGALERT 2-8C - SENSITECH",
        "TAGALERT 15-25C - SENSITECH",
        "TEMPTALE ULTRA 15-25C - SENSITECH"
    ]
    
    tab1, tab2, tab3, tab4 = st.tabs(categorias + ["📋 Histórico por Delivery"])

    def render_categoria(cat_name):
        dados_cat = df_liberados[df_liberados["Descricao"] == cat_name]
        st.write(f"**Disponíveis nesta categoria:** {len(dados_cat)} itens")
        
        if len(dados_cat) == 0:
            st.warning("Nenhum logger disponível nesta categoria.")
            return

        opcoes = dados_cat.apply(
            lambda x: f"Série: {x['Série']} | Palete: {x['Palete']} | ID: {x['Identificacao Estoque']}", axis=1
        ).tolist()
        
        selecionado = st.selectbox(f"Selecione o Logger ({cat_name}):", opcoes, key=cat_name)
        
        if selecionado:
            serie_sel = selecionado.split("|")[0].replace("Série:", "").strip()
            row = dados_cat[dados_cat["Série"] == serie_sel].iloc[0]
            
            # Exibição organizada dos dados mastigados
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Série", row["Série"])
            c2.metric("Descrição", row["Descricao"])
            c3.metric("Restrição", row["Restricao"])
            c4.metric("Palete", row["Palete"])
            c5.metric("ID Estoque", row["Identificacao Estoque"])
            
            # Validação do Delivery para liberar o botão
            if not delivery_input:
                st.info("⚠️ Digite o número do **DELIVERY** no campo acima para liberar o botão de baixa.")
            else:
                if st.button(f"✅ Vincular ao Delivery '{delivery_input}' e Dar Baixa", type="primary", key=f"btn_{serie_sel}"):
                    idx = df[df["Série"] == serie_sel].index[0]
                    st.session_state.df_loggers.at[idx, "Status_Uso"] = "UTILIZADO"
                    st.session_state.df_loggers.at[idx, "Delivery_Atribuido"] = delivery_input
                    st.success(f" Logger {serie_sel} (Palete {row['Palete']}) vinculado ao Delivery **{delivery_input}** com sucesso!")
                    st.rerun()

    with tab1:
        render_categoria("TAGALERT 2-8C - SENSITECH")
    with tab2:
        render_categoria("TAGALERT 15-25C - SENSITECH")
    with tab3:
        render_categoria("TEMPTALE ULTRA 15-25C - SENSITECH")

    with tab4:
        st.markdown("### Consultar Baixas efetuadas")
        df_utilizados = df[df["Status_Uso"] == "UTILIZADO"]
        st.dataframe(
            df_utilizados[["Delivery_Atribuido", "Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque"]],
            use_container_width=True
        )
        
        st.download_button(
            label="📥 Baixar Relatório de Deliveries (CSV)",
            data=df_utilizados.to_csv(index=False).encode('utf-8'),
            file_name="RELATORIO_DELIVERIES_LOGGERS.csv",
            mime="text/csv"
        )
