import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Louisiana - Vendas", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.title("Acesso Restrito")
    password = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if password == "123456": # Altere sua senha aqui
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    return False

if check_password():
    st.title("📊 Painel de Vendas - Louisiana")

    file_id = '1MR1jmDMEbI79c7j6cEsVvF2IFAYZPw8fXL5zg4iZyNU'
    url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    @st.cache_data(ttl=600) # Atualiza o cache a cada 10 minutos automaticamente
    def load_data():
        df = pd.read_csv(url)
        
        # Tratamento da coluna Venda (Robustez total)
        if 'Venda' in df.columns:
            # Transforma tudo em texto primeiro para limpar
            df['Venda'] = df['Venda'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
            # Converte para número. Se falhar, vira 0.
            df['Venda'] = pd.to_numeric(df['Venda'], errors='coerce').fillna(0)
            
        return df

    try:
        data = load_data()
        
        # Filtros
        st.sidebar.header("Filtros")
        vendedores = sorted(data["Vendedor"].dropna().unique())
        vendedor_sel = st.sidebar.multiselect("Selecionar Vendedor", options=vendedores)
        
        df_filtered = data.copy()
        if vendedor_sel:
            df_filtered = df_filtered[df_filtered["Vendedor"].isin(vendedor_sel)]

        # Métricas
        m1, m2, m3 = st.columns(3)
        m1.metric("Quantidade de Itens", len(df_filtered))
        
        total_venda = float(df_filtered['Venda'].sum())
        m2.metric("Venda Total", f"R$ {total_venda:,.2f}")
        
        ticket_medio = total_venda / len(df_filtered) if len(df_filtered) > 0 else 0
        m3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

        # Tabela Larga
        st.write("### Detalhamento das Vendas")
        st.dataframe(df_filtered, use_container_width=True, height=500)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

