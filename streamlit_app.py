import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerenciador de Loggers - DRS / BMS", layout="wide")

st.title("📦 Gerenciador de Loggers - Célula BMS")
st.subheader("Controle e Retirada de Palete / Identificação de Estoque")

# Inicialização do banco de dados na sessão
if "df_loggers" not in st.session_state:
    st.session_state.df_loggers = None

# Carregamento do arquivo
file_upload = st.file_uploader("Carregue a planilha DADOS BMS.xlsx", type=["xlsx", "xls"])

if file_upload:
    if st.session_state.df_loggers is None:
        # Carrega a aba 'loggers'
        df = pd.read_excel(file_upload, sheet_name="loggers")
        # Garante que as colunas de texto estejam limpas
        df["Descricao"] = df["Descricao"].astype(str).str.strip()
        df["Restricao"] = df["Restricao"].astype(str).str.strip()
        df["Palete"] = df["Palete"].astype(str).str.strip()
        df["Identificacao Estoque"] = df["Identificacao Estoque"].astype(str).str.strip()
        df["Série"] = df["Série"].astype(str).str.strip()
        
        # Cria coluna de controle de saída
        if "Status_Uso" not in df.columns:
            df["Status_Uso"] = "DISPONÍVEL"
            
        st.session_state.df_loggers = df

if st.session_state.df_loggers is not None:
    df = st.session_state.df_loggers

    # Filtro apenas de itens LIBERADOS e DISPONÍVEIS
    df_liberados = df[(df["Restricao"] == "LIBERADO") & (df["Status_Uso"] == "DISPONÍVEL")]

    st.markdown("---")
    
    # Abas por Categoria de Logger
    categorias = [
        "TAGALERT 2-8C - SENSITECH",
        "TAGALERT 15-25C - SENSITECH",
        "TEMPTALE ULTRA 15-25C - SENSITECH"
    ]
    
    tab1, tab2, tab3, tab4 = st.tabs(categorias + ["📜 Histórico de Retirados"])

    def render_categoria(cat_name):
        dados_cat = df_liberados[df_liberados["Descricao"] == cat_name]
        st.write(f"**Disponíveis:** {len(dados_cat)} loggers")
        
        if len(dados_cat) == 0:
            st.warning("Nenhum logger disponível nesta categoria.")
            return

        # Seleção do Logger para pegar os dados
        opcoes = dados_cat.apply(
            lambda x: f"Série: {x['Série']} | Palete: {x['Palete']} | ID Estoque: {x['Identificacao Estoque']}", axis=1
        ).tolist()
        
        selecionado = st.selectbox(f"Selecione o Logger ({cat_name}):", opcoes, key=cat_name)
        
        if selecionado:
            # Extrai a série selecionada
            serie_sel = selecionado.split("|")[0].replace("Série:", "").strip()
            row = dados_cat[dados_cat["Série"] == serie_sel].iloc[0]
            
            # Exibição organizada dos dados
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Descrição", row["Descricao"])
            c2.metric("Restrição", row["Restricao"])
            c3.metric("Palete", row["Palete"])
            c4.metric("Identificação Estoque", row["Identificacao Estoque"])
            
            # Botão de Baixa / Retirada
            if st.button(f"🚀 Baixar / Usar este Logger ({serie_sel})", type="primary", key=f"btn_{serie_sel}"):
                idx = df[df["Série"] == serie_sel].index[0]
                st.session_state.df_loggers.at[idx, "Status_Uso"] = "UTILIZADO / SAÍDO"
                st.success(f"Logger Série {serie_sel} marcado como UTILIZADO! Ele não estará mais disponível para seleção.")
                st.rerun()

        st.markdown("#### Tabela Completa da Categoria")
        st.dataframe(
            dados_cat[["Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque", "Endereco", "Data validade"]],
            use_container_width=True
        )

    with tab1:
        render_categoria("TAGALERT 2-8C - SENSITECH")
        
    with tab2:
        render_categoria("TAGALERT 15-25C - SENSITECH")

    with tab3:
        render_categoria("TEMPTALE ULTRA 15-25C - SENSITECH")

    with tab4:
        st.markdown("### Loggers já Utilizados / Retirados")
        df_utilizados = df[df["Status_Uso"] == "UTILIZADO / SAÍDO"]
        st.dataframe(
            df_utilizados[["Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque", "Status_Uso"]],
            use_container_width=True
        )
        
        # Botão para exportar planilha atualizada
        st.download_button(
            label="📥 Baixar Planilha Atualizada com Baixas",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="DADOS_BMS_ATUALIZADO.csv",
            mime="text/csv"
        )
