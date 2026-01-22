import streamlit as st
import pandas as pd
import numpy as np

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
        if password == "SUA_SENHA_AQUI": # Altere aqui
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    return False

if check_password():
    st.title("📊 Painel de Vendas - Louisiana")

    file_id = '1MR1jmDMEbI79c7j6cEsVvF2IFAYZPw8fXL5zg4iZyNU'
    url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    @st.cache_data(ttl=60) # Atualiza mais rápido (1 min) para teste
    def load_data():
        df = pd.read_csv(url)
        
        # 1. Tenta encontrar a coluna 'Venda' mesmo se houver erro de maiúscula/minúscula
        df.columns = [c.strip() for c in df.columns] # Remove espaços nos nomes das colunas
        col_venda = next((c for c in df.columns if c.lower() == 'venda'), None)

        if col_venda:
            # Converte para string para limpar caracteres de moeda/formatação
            df[col_venda] = df[col_venda].astype(str)
            
            # Limpeza: remove R$, remove pontos (separador de milhar), troca vírgula por ponto
            df[col_venda] = (
                df[col_venda]
                .str.replace('R$', '', regex=False)
                .str.replace(' ', '', regex=False)
                .str.replace('.', '', regex=False) # Remove ponto de milhar: 1.000 -> 1000
                .str.replace(',', '.', regex=False) # Troca vírgula decimal: 1000,50 -> 1000.50
            )
            
            # Converte para número (o sinal de menos '-' é preservado automaticamente)
            df[col_venda] = pd.to_numeric(df[col_venda], errors='coerce').fillna(0)
        
        return df, col_venda

    try:
        data, nome_coluna = load_data()
        
        if not nome_coluna:
            st.error(f"Coluna 'Venda' não encontrada. Colunas disponíveis: {list(data.columns)}")
        else:
            # Filtros
            st.sidebar.header("Filtros")
            vendedores = sorted(data["Vendedor"].dropna().unique()) if "Vendedor" in data.columns else []
            vendedor_sel = st.sidebar.multiselect("Selecionar Vendedor", options=vendedores)
            
            df_filtered = data.copy()
            if vendedor_sel:
                df_filtered = df_filtered[df_filtered["Vendedor"].isin(vendedor_sel)]

            # Métricas
            m1, m2 = st.columns(2)
            m1.metric("Qtd Itens", len(df_filtered))
            
            total_venda = float(df_filtered[nome_coluna].sum())
            m2.metric("Venda Líquida", f"R$ {total_venda:,.2f}")

            # Tabela
            st.write("### Detalhamento")
            # Exibe a tabela formatando a coluna de venda corretamente
            st.dataframe(
                df_filtered.style.format({nome_coluna: "{:.2f}"}), 
                use_container_width=True, 
                height=600
            )
            
    except Exception as e:
        st.error(f"Erro crítico: {e}")
