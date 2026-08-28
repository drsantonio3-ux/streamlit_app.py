import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerenciador de Loggers - Célula 03", layout="wide")

# CSS personalizado para diminuir o tamanho das fontes dos cartões
st.markdown("""
    <style>
    .card-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
    }
    .card-title {
        font-size: 11px !important;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .card-value {
        font-size: 14px !important;
        font-weight: bold;
        color: #212529;
        word-break: break-all;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Célula 03 (BMS) - Consulta e Controle de Loggers")

# Inicialização do banco
if "df_loggers" not in st.session_state:
    st.session_state.df_loggers = None

file_upload = st.file_uploader("Carregue a planilha DADOS BMS.xlsx", type=["xlsx", "xls"])

if file_upload and st.session_state.df_loggers is None:
    df = pd.read_excel(file_upload, sheet_name="loggers")
    
    # Padronização de nomes de colunas
    df.columns = [str(c).strip() for c in df.columns]
    
    if "DELIVERY" not in df.columns:
        df["DELIVERY"] = ""
    if "Status_Uso" not in df.columns:
        df["Status_Uso"] = "DISPONÍVEL"
        
    st.session_state.df_loggers = df
    st.rerun()

if st.session_state.df_loggers is not None:
    df = st.session_state.df_loggers

    col_serie = "Série" if "Série" in df.columns else "Serie"
    col_desc = "Descricao" if "Descricao" in df.columns else "Descrição"
    col_rest = "Restricao" if "Restricao" in df.columns else "Restrição"
    col_palete = "Palete"
    col_id = "Identificacao Estoque" if "Identificacao Estoque" in df.columns else "Identificação Estoque"

    # Filtro apenas LIBERADOS e DISPONÍVEIS
    df_disponiveis = df[(df[col_rest] == "LIBERADO") & (df["Status_Uso"] == "DISPONÍVEL")]

    st.markdown("---")

    categorias = [
        "TAGALERT 2-8C - SENSITECH",
        "TAGALERT 15-25C - SENSITECH",
        "TEMPTALE ULTRA 15-25C - SENSITECH"
    ]
    
    tab1, tab2, tab3, tab4 = st.tabs(categorias + ["📜 Histórico por Delivery"])

    def render_categoria(cat_name):
        dados_cat = df_disponiveis[df_disponiveis[col_desc] == cat_name]
        st.write(f"**Disponíveis:** {len(dados_cat)}")
        
        if len(dados_cat) == 0:
            st.info("Nenhum logger disponível nesta categoria.")
            return

        lista_opcoes = dados_cat.apply(
            lambda x: f"Série: {x[col_serie]} | Palete: {x[col_palete]} | ID: {x[col_id]}", axis=1
        ).tolist()
        
        sel = st.selectbox("Selecione o Logger:", lista_opcoes, key=cat_name)
        
        if sel:
            serie_extraida = sel.split("|")[0].replace("Série:", "").strip()
            row = dados_cat[dados_cat[col_serie] == serie_extraida].iloc[0]
            
            # Exibição compacta e responsiva
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="card-box"><div class="card-title">Série</div><div class="card-value">{row[col_serie]}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="card-box"><div class="card-title">Descrição</div><div class="card-value">{row[col_desc]}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="card-box"><div class="card-title">Restrição</div><div class="card-value">{row[col_rest]}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="card-box"><div class="card-title">Palete</div><div class="card-value">{row[col_palete]}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="card-box"><div class="card-title">Identificação Estoque</div><div class="card-value">{row[col_id]}</div></div>', unsafe_allow_html=True)

            deliv_input = st.text_input(f"Digite o DELIVERY para o Logger {serie_extraida}:", key=f"del_{serie_extraida}")

            if st.button(f"🚀 Confirmar Saída / Baixar Logger", type="primary", key=f"btn_{serie_extraida}"):
                if not deliv_input.strip():
                    st.error("⚠️ Por favor, digite o número do **DELIVERY** antes de dar a baixa.")
                else:
                    idx = df[df[col_serie] == serie_extraida].index[0]
                    st.session_state.df_loggers.at[idx, "Status_Uso"] = "UTILIZADO"
                    st.session_state.df_loggers.at[idx, "DELIVERY"] = deliv_input.strip()
                    st.success(f"Baixa concluída! Logger **{serie_extraida}** vinculado ao Delivery **{deliv_input}**.")
                    st.rerun()

    with tab1:
        render_categoria("TAGALERT 2-8C - SENSITECH")
    with tab2:
        render_categoria("TAGALERT 15-25C - SENSITECH")
    with tab3:
        render_categoria("TEMPTALE ULTRA 15-25C - SENSITECH")

    with tab4:
        st.markdown("### Loggers Utilizados por Delivery")
        df_usados = df[df["Status_Uso"] == "UTILIZADO"]
        
        if len(df_usados) > 0:
            # Opção de Estorno
            st.markdown("#### 🔄 Estornar / Retornar Logger ao Estoque")
            
            lista_estorno = df_usados.apply(
                lambda x: f"Delivery: {x['DELIVERY']} | Série: {x[col_serie]} | Palete: {x[col_palete]}", axis=1
            ).tolist()
            
            sel_estorno = st.selectbox("Selecione o registro para estornar:", lista_estorno)
            
            if st.button("🔄 Estornar / Voltar ao Estoque", type="secondary"):
                serie_estorno = sel_estorno.split("|")[1].replace("Série:", "").strip()
                idx_est = df[df[col_serie] == serie_estorno].index[0]
                
                # Devolve para o estoque
                st.session_state.df_loggers.at[idx_est, "Status_Uso"] = "DISPONÍVEL"
                st.session_state.df_loggers.at[idx_est, "DELIVERY"] = ""
                st.success(f"Logger **{serie_estorno}** estornado e retornado ao estoque com sucesso!")
                st.rerun()

            st.markdown("---")
            st.markdown("#### Tabela de Baixas Efetuadas")
            st.dataframe(
                df_usados[["DELIVERY", col_serie, col_desc, col_rest, col_palete, col_id]],
                use_container_width=True
            )
        else:
            st.info("Nenhuma baixa realizada ainda.")
