import streamlit as st
import re
from PyPDF2 import PdfReader

st.title('Analisador de Extrato - Receita Bruta Informada')

uploaded_files = st.file_uploader('Selecione os arquivos PDF', type='pdf', accept_multiple_files=True)

pattern = r'Receita Bruta Informada: R\$ ([\d\.,]+)'

def extrair_receita(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ''
    for page in reader.pages:
        texto += page.extract_text() + '\n'
    match = re.search(pattern, texto)
    if match:
        valor = match.group(1).replace('.', '').replace(',', '.')
        return float(valor)
    return 0.0

if uploaded_files:
    total = 0.0
    resultados = []
    for file in uploaded_files:
        valor = extrair_receita(file)
        resultados.append((file.name, valor))
        total += valor
    st.write('Valores extraídos:')
    for nome, valor in resultados:
        st.write(f'{nome}: R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
    st.markdown(f'## Soma total: R$ {total:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
else:
    st.info('Faça upload de um ou mais arquivos PDF para começar.')
