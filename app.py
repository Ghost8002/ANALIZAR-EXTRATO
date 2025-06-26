import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Analisador de Extrato', layout='wide')
st.title('Analisador de Extrato - Receita Bruta por Categoria')

uploaded_files = st.file_uploader('Selecione os arquivos PDF', type='pdf', accept_multiple_files=True)

# Padrões para identificar as seções
pattern_locacao = r'Locação de bens móveis[\w\W]+?Receita Bruta Informada: R\$ ([\d\.,]+)'
pattern_servicos = r'Prestação de Serviços, exceto para o exterior - Não sujeitos ao fator "r" e tributados pelo Anexo III, com retenção/substituição tributária de ISS[\w\W]+?Receita Bruta Informada: R\$ ([\d\.,]+)'

# Função para extrair valores por categoria

def extrair_receitas_por_categoria(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ''
    for page in reader.pages:
        texto += page.extract_text() + '\n'
    # Extrai valores de cada categoria
    locacao = re.findall(pattern_locacao, texto)
    servicos = re.findall(pattern_servicos, texto)
    valores_locacao = []
    valores_servicos = []
    for valor in locacao:
        valor_num = valor.replace('.', '').replace(',', '.')
        try:
            valores_locacao.append(float(valor_num))
        except ValueError:
            pass
    for valor in servicos:
        valor_num = valor.replace('.', '').replace(',', '.')
        try:
            valores_servicos.append(float(valor_num))
        except ValueError:
            pass
    return valores_locacao, valores_servicos

if uploaded_files:
    total_locacao = 0.0
    total_servicos = 0.0
    resultados = []
    for file in uploaded_files:
        valores_locacao, valores_servicos = extrair_receitas_por_categoria(file)
        soma_locacao = sum(valores_locacao)
        soma_servicos = sum(valores_servicos)
        resultados.append({
            'Arquivo': file.name,
            'Locação de bens móveis': soma_locacao,
            'Prestação de Serviços': soma_servicos
        })
        total_locacao += soma_locacao
        total_servicos += soma_servicos

    df = pd.DataFrame(resultados)
    df_totais = pd.DataFrame({
        'Categoria': ['Locação de bens móveis', 'Prestação de Serviços'],
        'Total': [total_locacao, total_servicos]
    })

    st.subheader('Tabela de valores por arquivo')
    st.dataframe(df.style.format({'Locação de bens móveis': 'R$ {:,.2f}', 'Prestação de Serviços': 'R$ {:,.2f}'}), use_container_width=True)

    st.subheader('Totais por categoria')
    st.dataframe(df_totais.style.format({'Total': 'R$ {:,.2f}'}), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Gráfico por arquivo')
        fig1 = px.bar(df, x='Arquivo', y=['Locação de bens móveis', 'Prestação de Serviços'],
                      barmode='group',
                      labels={'value': 'Valor (R$)', 'variable': 'Categoria'},
                      title='Receita Bruta por Categoria em cada Arquivo')
        fig1.update_layout(xaxis_title='Arquivo', yaxis_title='Valor (R$)')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.markdown('#### Gráfico dos totais gerais')
        fig2 = px.bar(df_totais, x='Categoria', y='Total',
                      labels={'Total': 'Valor (R$)', 'Categoria': 'Categoria'},
                      title='Totais Gerais por Categoria',
                      text_auto='.2s')
        fig2.update_layout(xaxis_title='Categoria', yaxis_title='Valor (R$)')
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info('Faça upload de um ou mais arquivos PDF para começar.')
