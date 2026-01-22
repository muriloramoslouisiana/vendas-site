import streamlit as st
import pandas as pd

# Configuração simplificada de senha
def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("Acesso Restrito")
    password = st.text_input("Digite a senha para acessar os dados de vendas:", type="password")
    if st.button("Entrar"):
        if password == "123456": # Altere para a senha desejada
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    return False

if check_password():
    st.title("📊 Painel de Vendas - Louisiana")

    # Substitua pelo ID do seu arquivo no Google Drive
    file_id = 'https://docs.google.com/spreadsheets/d/1bXorW_-a224wNiTK8Mnc_I8yAXloecqn/edit?usp=sharing&ouid=101741796619167215012&rtpof=true&sd=true'
    Erro ao conectar com a planilha: HTTP Error 404: Not Found
    url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    @st.cache_data
    def load_data():
        df = pd.read_csv(url)
        # Converte coluna de data se necessário
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'])
        return df

    try:
        data = load_data()
        
        # Filtros na barra lateral
        st.sidebar.header("Filtros")
        vendedor = st.sidebar.multiselect("Selecionar Vendedor", options=data["Vendedor"].unique())
        
        df_filtered = data.copy()
        if vendedor:
            df_filtered = df_filtered[df_filtered["Vendedor"].isin(vendedor)]

        # Exibição de Métricas
        col1, col2 = st.columns(2)
        col1.metric("Total de Itens", len(df_filtered))
        col2.metric("Venda Total (R$)", f"{df_filtered['Venda'].sum():,.2f}")

        st.dataframe(df_filtered, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")

        st.info("Certifique-se de que a planilha está com o link compartilhado para 'Qualquer pessoa com o link'.")

