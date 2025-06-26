import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd

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
    for file in uploaded_files:
        valores_locacao, valores_servicos = extrair_receitas_por_categoria(file)
        total_locacao += sum(valores_locacao)
        total_servicos += sum(valores_servicos)
    total_geral = total_locacao + total_servicos

    def format_brl(valor):
        return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    df_totais = pd.DataFrame({
        'Categoria': ['Locação de bens móveis', 'Prestação de Serviços', 'Total Geral'],
        'Valor': [total_locacao, total_servicos, total_geral]
    })
    df_totais['Valor'] = df_totais['Valor'].apply(format_brl)
    st.dataframe(df_totais, use_container_width=True)
else:
    st.info('Faça upload de um ou mais arquivos PDF para começar.')
