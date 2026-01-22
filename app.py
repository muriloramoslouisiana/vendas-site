import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
# Configuração de senha
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("Acesso Restrito")
    password = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if password == "123456": # Ajuste sua senha aqui
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    return False

if check_password():
    st.title("📊 Painel de Vendas - Louisiana")

    # ID correto que você extraiu
    file_id = '1MR1jmDMEbI79c7j6cEsVvF2IFAYZPw8fXL5zg4iZyNU'
    url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    @st.cache_data
    def load_data():
        df = pd.read_csv(url)
        
        # Converte a coluna Venda para número (remove R$ ou vírgulas se houver)
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

        # Métricas
        col1, col2 = st.columns(2)
        col1.metric("Total de Itens", len(df_filtered))
        
        # Aqui estava o erro: formatamos apenas se for número
        total_vendas = float(df_filtered['Venda'].sum())
        col2.metric("Venda Total", f"R$ {total_vendas:,.2f}")

        st.dataframe(df_filtered, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")




