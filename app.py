import streamlit as st
import pandas as pd

# 1. Configuração para ocupar a tela inteira
st.set_page_config(page_title="Louisiana - Vendas", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("Acesso Restrito")
    password = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if password == "123456": # Ajuste sua senha
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    return False

if check_password():
    st.title("📊 Painel de Vendas - Louisiana")

    file_id = '1MR1jmDMEbI79c7j6cEsVvF2IFAYZPw8fXL5zg4iZyNU'
    url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    @st.cache_data
    def load_data():
        df = pd.read_csv(url)
        if 'Venda' in df.columns:
            df['Venda'] = pd.to_numeric(df['Venda'], errors='coerce').fillna(0)
        return df

    try:
        data = load_data()
        
        # Filtros
        st.sidebar.header("Filtros")
        vendedores = data["Vendedor"].dropna().unique()
        vendedor_sel = st.sidebar.multiselect("Selecionar Vendedor", options=vendedores)
        
        df_filtered = data.copy()
        if vendedor_sel:
            df_filtered = df_filtered[df_filtered["Vendedor"].isin(vendedor_sel)]

        # Métricas em colunas largas
        col1, col2, col3 = st.columns([1, 1, 2]) # A terceira coluna sobra para equilíbrio
        col1.metric("Total de Itens", len(df_filtered))
        total_vendas = float(df_filtered['Venda'].sum())
        col2.metric("Venda Total", f"R$ {total_vendas:,.2f}")

        # Tabela ocupando 100% da largura
        st.dataframe(df_filtered, use_container_width=True, height=600)
        
    except Exception as e:
        st.error(f"Erro: {e}")


