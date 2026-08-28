import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerenciador de Loggers - DRS Group", layout="wide")

st.title("📦 Célula 03 (BMS) - Controle de Loggers")
st.subheader("Painel de Baixa de Palete e ID Estoque por Delivery")

# Inicialização da base na memória
if "df_loggers" not in st.session_state:
    st.session_state.df_loggers = None

# Upload da planilha DADOS BMS.xlsx
file_upload = st.file_uploader("Carregue a planilha DADOS BMS.xlsx", type=["xlsx", "xls"])

if file_upload and st.session_state.df_loggers is None:
    df = pd.read_excel(file_upload, sheet_name="loggers")
    
    # Tratamento simples dos dados
    cols_str = ["Descricao", "Restricao", "Palete", "Identificacao Estoque", "Série"]
    for col in cols_str:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    df["Status_Uso"] = "DISPONÍVEL"
    df["Delivery"] = ""
    st.session_state.df_loggers = df
    st.rerun()

if st.session_state.df_loggers is not None:
    df = st.session_state.df_loggers

    # Filtra apenas itens LIBERADOS e DISPONÍVEIS
    df_liberados = df[(df["Restricao"] == "LIBERADO") & (df["Status_Uso"] == "DISPONÍVEL")]

    st.markdown("---")

    categorias = [
        "TAGALERT 2-8C - SENSITECH",
        "TAGALERT 15-25C - SENSITECH",
        "TEMPTALE ULTRA 15-25C - SENSITECH"
    ]
    
    tab1, tab2, tab3, tab4 = st.tabs(categorias + ["📜 Histórico de Baixas"])

    def render_categoria(cat_name):
        dados_cat = df_liberados[df_liberados["Descricao"] == cat_name]
        st.write(f"**Loggers Liberados Disponíveis:** {len(dados_cat)}")
        
        if len(dados_cat) == 0:
            st.warning("Nenhum logger disponível nesta categoria.")
            return

        # Menu para selecionar o Logger desejado
        opcoes = dados_cat.apply(
            lambda x: f"Série: {x['Série']} | Palete: {x['Palete']} | ID Estoque: {x['Identificacao Estoque']}", axis=1
        ).tolist()
        
        selecionado = st.selectbox(f"Selecione o Logger ({cat_name}):", opcoes, key=cat_name)
        
        if selecionado:
            serie_sel = selecionado.split("|")[0].replace("Série:", "").strip()
            row = dados_cat[dados_cat["Série"] == serie_sel].iloc[0]
            
            # Campo do DELIVERY diretamente na hora de dar a baixa
            st.markdown("#### 📝 Informação de Saída")
            delivery_val = st.text_input(
                "Digite o número do DELIVERY para este registro:", 
                key=f"del_input_{serie_sel}",
                placeholder="Cole ou digite o Delivery da Packing List..."
            )
            
            # Exibição dos dados em destaque
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Série", row["Série"])
            c2.metric("Descrição", row["Descricao"])
            c3.metric("Restrição", row["Restricao"])
            c4.metric("Palete", row["Palete"])
            
            st.metric("Identificação Estoque", row["Identificacao Estoque"])

            # Botão de Baixa
            if st.button(f"🚀 Dar Baixa no Logger ({serie_sel})", type="primary", key=f"btn_{serie_sel}"):
                if not delivery_val.strip():
                    st.error("⚠️ Por favor, informe o **DELIVERY** antes de dar baixa!")
                else:
                    idx = df[df["Série"] == serie_sel].index[0]
                    st.session_state.df_loggers.at[idx, "Status_Uso"] = "BAIXADO / UTILIZADO"
                    st.session_state.df_loggers.at[idx, "Delivery"] = delivery_val.strip()
                    st.success(f"Baixa concluída! Logger **{serie_sel}** (Palete {row['Palete']}) vinculado ao Delivery **{delivery_val}**.")
                    st.rerun()

        st.markdown("#### Tabela Disponível")
        st.dataframe(
            dados_cat[["Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque", "Endereco"]],
            use_container_width=True
        )

    with tab1:
        render_categoria("TAGALERT 2-8C - SENSITECH")
        
    with tab2:
        render_categoria("TAGALERT 15-25C - SENSITECH")

    with tab3:
        render_categoria("TEMPTALE ULTRA 15-25C - SENSITECH")

    with tab4:
        st.markdown("### Loggers Utilizados com Delivery Registrado")
        df_baixas = df[df["Status_Uso"] == "BAIXADO / UTILIZADO"]
        
        st.dataframe(
            df_baixas[["Delivery", "Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque"]],
            use_container_width=True
        )
        
        st.download_button(
            label="📥 Exportar Relatório de Baixas (CSV)",
            data=df_baixas.to_csv(index=False).encode('utf-8'),
            file_name="LOGGERS_BAIXADOS_DELIVERY.csv",
            mime="text/csv"
        )
