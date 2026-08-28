import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerenciador de Loggers - Célula 03", layout="wide")

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
        font-size: 13px !important;
        font-weight: bold;
        color: #212529;
        word-break: break-all;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Célula 03 (BMS) - Consulta e Controle de Loggers")

# ==============================================================================
# COLE O LINK DA SUA PLANILHA DO GOOGLE SHEETS ENTRE AS ASPAS ABAIXO:
# Exemplo: https://docs.google.com/spreadsheets/d/1ABC123xyz/edit#gid=0
# ==============================================================================
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/SEU_LINK_AQUI/edit"

def converter_url_csv(url):
    if "/edit" in url:
        return url.split("/edit")[0] + "/gviz/tq?tqx=out:csv&sheet=loggers"
    return url

@st.cache_data(ttl=5)
def carregar_dados_nuvem(url):
    csv_url = converter_url_csv(url)
    df = pd.read_csv(csv_url)
    df.columns = [str(c).strip() for c in df.columns]
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            
    if "DELIVERY" not in df.columns:
        df["DELIVERY"] = ""
    if "Status_Uso" not in df.columns:
        df["Status_Uso"] = "DISPONÍVEL"
        
    return df

# Inicializa sessão se necessário
if "df_loggers" not in st.session_state:
    try:
        st.session_state.df_loggers = carregar_dados_nuvem(URL_GOOGLE_SHEETS)
    except Exception as e:
        st.session_state.df_loggers = None

# Upload alternativo como backup caso a planilha do Google não esteja pública
if st.session_state.df_loggers is None:
    st.warning("⚠️ Não foi possível ler a planilha online. Verifique se o link está 'Público (Qualquer pessoa com o link)' ou faça o upload manual da planilha abaixo:")
    file_upload = st.file_uploader("Carregue a planilha DADOS BMS.xlsx", type=["xlsx", "xls"])
    if file_upload:
        df = pd.read_excel(file_upload, sheet_name="loggers")
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
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
        
        sel = st.selectbox("Selecione o Logger:", lista_opcoes, key=f"select_{cat_name}")
        
        if sel:
            serie_extraida = sel.split("|")[0].replace("Série:", "").strip()
            filtro = dados_cat[dados_cat[col_serie].astype(str).str.strip() == serie_extraida]
            
            if not filtro.empty:
                row = filtro.iloc[0]
                
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

                deliv_input = st.text_input(f"Digite o DELIVERY para o Logger {serie_extraida}:", key=f"del_{cat_name}_{serie_extraida}")

                if st.button(f"🚀 Confirmar Saída / Baixar Logger", type="primary", key=f"btn_{cat_name}_{serie_extraida}"):
                    if not deliv_input.strip():
                        st.error("⚠️ Por favor, digite o número do **DELIVERY** antes de dar a baixa.")
                    else:
                        idx_match = df[df[col_serie].astype(str).str.strip() == serie_extraida].index
                        if len(idx_match) > 0:
                            idx = idx_match[0]
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
            st.markdown("#### 🔄 Estornar / Retornar Logger ao Estoque")
            
            lista_estorno = df_usados.apply(
                lambda x: f"Delivery: {x['DELIVERY']} | Série: {x[col_serie]} | Palete: {x[col_palete]}", axis=1
            ).tolist()
            
            sel_estorno = st.selectbox("Selecione o registro para estornar:", lista_estorno)
            
            if st.button("🔄 Estornar / Voltar ao Estoque", type="secondary"):
                serie_estorno = sel_estorno.split("|")[1].replace("Série:", "").strip()
                idx_est = df[df[col_serie].astype(str).str.strip() == serie_estorno].index[0]
                
                st.session_state.df_loggers.at[idx_est, "Status_Uso"] = "DISPONÍVEL"
                st.session_state.df_loggers.at[idx_est, "DELIVERY"] = ""
                st.success(f"Logger **{serie_estorno}** estornado e retornado ao estoque!")
                st.rerun()

            st.markdown("---")
            st.markdown("#### Tabela de Baixas Efetuadas")
            st.dataframe(
                df_usados[["DELIVERY", col_serie, col_desc, col_rest, col_palete, col_id]],
                use_container_width=True
            )
        else:
            st.info("Nenhuma baixa realizada ainda.")
