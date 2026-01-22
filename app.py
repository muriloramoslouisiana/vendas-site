import streamlit as st
import pandas as pd

# 1. Configuração da página para ser LARGA
st.set_page_config(page_title="Louisiana - Vendas", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.title("Acesso Restrito")
    password = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if password == "123456": # Altere para sua senha
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    return False

if check_password():
    st.title("📊 Painel de Vendas - Louisiana")

    # Link da sua planilha (ID já conferido)
    file_id = '1MR1jmDMEbI79c7j6cEsVvF2IFAYZPw8fXL5zg4iZyNU'
    url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    @st.cache_data(ttl=600)
    def load_data():
        # Lendo os dados diretamente
        df = pd.read_csv(url)
        
        # Tratamento seguro da coluna Venda para não perder negativos nem decimais
        if 'Venda' in df.columns:
            # Se for texto, remove R$ e espaços. Se for número, o pandas já leu certo.
            if df['Venda'].dtype == 'object':
                df['Venda'] = df['Venda'].str.replace('R$', '', regex=False).str.strip()
                # Só troca vírgula por ponto se a vírgula existir (formato brasileiro)
                df['Venda'] = df['Venda'].str.replace(',', '.', regex=False)
            
            # Converte para número e mantém os negativos
            df['Venda'] = pd.to_numeric(df['Venda'], errors='coerce')
            
        return df

    try:
        data = load_data()
        
        # Filtros na lateral
        st.sidebar.header("Filtros")
        vendedores = sorted(data["Vendedor"].dropna().unique())
        vendedor_sel = st.sidebar.multiselect("Selecionar Vendedor", options=vendedores)
        
        df_filtered = data.copy()
        if vendedor_sel:
            df_filtered = df_filtered[df_filtered["Vendedor"].isin(vendedor_sel)]

        # --- MÉTRICAS ---
        m1, m2, m3 = st.columns(3)
        
        # Total de linhas (vendas + trocas)
        m1.metric("Qtd Itens", len(df_filtered))
        
        # Soma de vendas (considerando negativos)
        total_venda = float(df_filtered['Venda'].sum())
        m2.metric("Venda Líquida", f"R$ {total_venda:,.2f}")
        
        # Ticket médio das operações
        ticket = total_venda / len(df_filtered) if len(df_filtered) > 0 else 0
        m3.metric("Ticket Médio", f"R$ {ticket:,.2f}")

        # --- TABELA LARGA ---
        st.write("### Detalhamento")
        # Formatando a coluna Venda para aparecer com 2 casas decimais na tabela
        st.dataframe(
            df_filtered.style.format({"Venda": "{:.2f}"}, na_rep="-"), 
            use_container_width=True, 
            height=600
        )
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
