import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerenciador de Loggers - DRS Group", layout="wide")

st.title("📦 Célula 03 (BMS) - Controle de Loggers")
st.subheader("Painel de Controle de Palete, ID Estoque e Delivery")

# Inicialização da base na memória
if "df_loggers" not in st.session_state:
    st.session_state.df_loggers = None

# Upload da planilha DADOS BMS.xlsx
file_upload = st.file_uploader("Carregue a planilha DADOS BMS.xlsx", type=["xlsx", "xls"])

if file_upload and st.session_state.df_loggers is None:
    df = pd.read_excel(file_upload, sheet_name="loggers")
    
    # Limpeza dos textos
    cols_str = ["Descricao", "Restricao", "Palete", "Identificacao Estoque", "Série"]
    for col in cols_str:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Garante a criação da coluna Delivery
    df["DELIVERY"] = ""
    st.session_state.df_loggers = df
    st.rerun()

if st.session_state.df_loggers is not None:
    df = st.session_state.df_loggers

    # Filtra apenas itens LIBERADOS
    df_liberados = df[df["Restricao"] == "LIBERADO"].copy()

    st.markdown("---")

    categorias = [
        "TAGALERT 2-8C - SENSITECH",
        "TAGALERT 15-25C - SENSITECH",
        "TEMPTALE ULTRA 15-25C - SENSITECH"
    ]
    
    tab1, tab2, tab3 = st.tabs(categorias)

    def render_categoria(cat_name):
        dados_cat = df_liberados[df_liberados["Descricao"] == cat_name].copy()
        
        st.write(f"**Total nesta categoria:** {len(dados_cat)}")
        st.info("💡 Você pode digitar/colar o **DELIVERY** diretamente na célula da tabela abaixo:")
        
        # Exibe a tabela editável sem a coluna Endereço e com a coluna DELIVERY editável
        colunas_exibir = ["Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque", "DELIVERY"]
        
        edited_df = st.data_editor(
            dados_cat[colunas_exibir],
            use_container_width=True,
            disabled=["Série", "Descricao", "Restricao", "Palete", "Identificacao Estoque"],
            key=f"editor_{cat_name}"
        )
        
        # Atualiza as alterações do DELIVERY no banco principal
        if not edited_df.equals(dados_cat[colunas_exibir]):
            for idx, row in edited_df.iterrows():
                st.session_state.df_loggers.loc[idx, "DELIVERY"] = row["DELIVERY"]

    with tab1:
        render_categoria("TAGALERT 2-8C - SENSITECH")
        
    with tab2:
        render_categoria("TAGALERT 15-25C - SENSITECH")

    with tab3:
        render_categoria("TEMPTALE ULTRA 15-25C - SENSITECH")
