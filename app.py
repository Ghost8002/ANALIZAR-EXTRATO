import streamlit as st
import re
from PyPDF2 import PdfReader

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
        resultados.append((file.name, valores_locacao, soma_locacao, valores_servicos, soma_servicos))
        total_locacao += soma_locacao
        total_servicos += soma_servicos
    st.write('Valores extraídos por categoria:')
    for nome, valores_locacao, soma_locacao, valores_servicos, soma_servicos in resultados:
        st.write(f'**{nome}**')
        st.write('Locação de bens móveis: ' + (', '.join([f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') for v in valores_locacao]) if valores_locacao else 'Nenhum valor encontrado.') + f' (Total: R$ {soma_locacao:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ')')
        st.write('Prestação de Serviços: ' + (', '.join([f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') for v in valores_servicos]) if valores_servicos else 'Nenhum valor encontrado.') + f' (Total: R$ {soma_servicos:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ')')
        st.write('---')
    st.markdown(f'## Soma total - Locação de bens móveis: R$ {total_locacao:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
    st.markdown(f'## Soma total - Prestação de Serviços: R$ {total_servicos:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
else:
    st.info('Faça upload de um ou mais arquivos PDF para começar.')
