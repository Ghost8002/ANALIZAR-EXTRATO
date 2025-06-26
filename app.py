import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Analisador de Extrato', layout='wide')
st.title('Analisador de Extrato - Receita Bruta por Categoria')

uploaded_files = st.file_uploader('Selecione os arquivos PDF', type='pdf', accept_multiple_files=True)

# Regex para encontrar todos os blocos que contenham Receita Bruta Informada
pattern_bloco = r'((Locação de bens móveis|Prestação de Serviços[\w\W]{0,200}?)?[\w\W]{0,300}?Receita Bruta Informada: R\$ ([\d\.,]+))'

# Função para extrair valores por categoria de forma flexível
def extrair_receitas_por_categoria(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ''
    for page in reader.pages:
        texto += page.extract_text() + '\n'
    matches = re.findall(pattern_bloco, texto, re.IGNORECASE)
    valores_locacao = []
    valores_servicos = []
    for bloco, categoria, valor in matches:
        valor_num = valor.replace('.', '').replace(',', '.')
        try:
            valor_float = float(valor_num)
        except ValueError:
            continue
        if 'locação de bens móveis' in bloco.lower():
            valores_locacao.append(valor_float)
        elif 'prestação de serviços' in bloco.lower():
            valores_servicos.append(valor_float)
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
