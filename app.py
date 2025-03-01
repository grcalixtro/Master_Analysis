import streamlit as st
import pandas as pd
import numpy as np
from json import loads
from pandas import read_csv
import io
#import openpyxl
from json import loads
import datetime as dt
from datetime import date, time, datetime, timedelta
#import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import fitz  # PyMuPDF - Lê o PDF (Texto)
import base64 # Mostra PDF (Foto)
from PIL import Image
from io import BytesIO

Horario_Inicio = dt.datetime.now()

# Icone da página
st.set_page_config(
    page_title="SPL_System Production Lear",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)
#--------------------------------------------- Carregar dados do Arquivo -----------------------------------------------------

Master = pd.read_csv(r"C:\Users\Family\Documents\Cursos Python\Projeto_Master\df_Master.csv")
maqs_corte = pd.read_csv(r"C:\Users\Family\Documents\Cursos Python\Projeto_Master\df_maqs_corte.csv")
lista_cfa = pd.read_csv(r'C:\Users\Family\Documents\Cursos Python\Projeto_Master\df_cfa.csv')

# Converte 'total week' para numérico, forçando erros como NaN
Master['total week'] = pd.to_numeric(Master['total week'], errors='coerce')

# Filtra as linhas onde 'total week' > 0 e 'Cut.Mch' não está em ['0', '-', '""']
Master = Master[(Master['total week'] > 0) & (~Master['Cut.Mch'].isin(['0', '-', '""']))]

#------------------------------------------------------ TITULOS --------------------------------------------------------------
# Primeiro comando no Streamlit
st.sidebar.image('Logo_Lear_Preto_L_Branco.png', caption="gcalixtro")
# Agora os outros comandos do Streamlit podem vir
st.title('Master Analysis WE09')
col1, col2 = st.columns([1, 5])

#with col2:
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');
        h1 {
            font-family: 'Orbitron', sans-serif;
        }
    </style>
   
    <h1 style='text-align: center;'>Assignação de Máquinas</h1>    

""", unsafe_allow_html=True)

print('\n------------------------D A D O S --- F I L T R A D O S --- M A S T E R ------------------------\n')
print(Master)
Master.to_csv("Master_Geral.csv", index=False)

print('\nO dataset ( Master ) possui {:,.0f}'.format(Master.shape[0]).replace(',', '.'), 'linhas e {} colunas.'.format(Master.shape[1]))

print('\n== R E S U M O = T O T A L ==\n')
# Supondo que df_total já foi calculado
df_total = Master.groupby('Projeto')['total week'].sum().reset_index()

# Calcular o total geral da soma da coluna 'total week'
total_geral = df_total['total week'].sum()

# Formatar a coluna 'total week' com separador de milhar
df_total['total week'] = df_total['total week'].apply(lambda x: "{:,.0f}".format(x).replace(',', '.'))

# Adicionar uma linha com o total geral ao dataframe
df_total.loc[len(df_total)] = ['TOTAL GERAL', "{:,.0f}".format(total_geral).replace(',', '.')]

# Exibir o resultado
print(df_total)
print('\n---df_total.dtypes---')
print(df_total.dtypes)
#-------------------------Carga Maq Qtde ------------------------------------
# Garantir que a coluna 'Cut.Mch' seja tratada como texto
Master['Cut.Mch'] = Master['Cut.Mch'].astype(str)

# Agrupar por 'Cut.Mch' e somar os valores de 'total week'
Carga_Maq = Master.groupby('Máq_Tipo')['total week'].sum().reset_index()

# Formatar a coluna 'total week' com separador de milhar
Carga_Maq['total week'] = Carga_Maq['total week'].apply(lambda x: "{:,.0f}".format(x).replace(',', '.'))

print('\n---- Carga_Máq_Qtde ----\n')
# Exibir o DataFrame resultante
print(Carga_Maq)

# Calcular o total geral de 'total week' para todos os projetos
total_geral_todos = Master['total week'].sum()

print('\nO dataset ( Master ) possui {:,.0f}'.format(Master.shape[0]).replace(',', '.'), 'linhas e {} colunas.'.format(Master.shape[1]))
print('\nArquivo Importado como Sucesso!!!\n')

#-------------------------Carga Maq Tipos ------------------------------------
print('\n== R E S U M O = T I P O S ==\n')

# Verificar se "VS30" está presente antes da agregação
print("\---- Projetos antes da agregação ----")
print(Master['Projeto'].unique())  # Ver quais projetos estão presentes

# Contar os tipos únicos de 'Personalizar' por 'Máq_Tipo' e 'Projeto'
Tipos_Maq = Master.groupby(['Máq_Tipo', 'Projeto'])[['Personalizar', 'total week']].agg({
    'Personalizar': 'nunique',
    'total week': 'sum'
}).reset_index()

# Renomear colunas
Tipos_Maq.columns = ['Máq_Tipo', 'Projeto', 'Quantidade_Tipos', 'Total_Week']

# Verificar se "VS30" está presente após a agregação
print("\n---- Dados agregados ----\n")
print(Tipos_Maq[Tipos_Maq['Projeto'] == 'SPIN'])  # Ver se VS30 aparece aqui

#========================================== SIDEBAR ====================================================
# Sidebar
st.sidebar.markdown("## Painel de Filtros")
st.sidebar.caption("Gráfico Dados Gerais")

# Opções de Gráficos
coluna1, coluna2 = st.sidebar.columns(2)

# Agrupar por 'Projeto' e somar os valores de 'total week'
df_total = Master.groupby('Projeto')['total week'].sum().reset_index()


#---------------------------------- GRÁFICOS DE LINHAS E COLUNAS ----------------------------------------

# Botão para o Gráfico de Barras na primeira coluna
if coluna1.button("Gráfico de Barras"):
#     st.bar_chart(df_total.set_index('Projeto'), use_container_width=True) Sem a cor
    fig = px.bar(
        df_total,
        x='Projeto',
        y=df_total.columns[1:],  # Supondo que a 1ª coluna seja 'Projeto' e o restante sejam valores numéricos
        title="Carga_Projetos",
        text_auto=True
    )
    # Personalizando a cor para cinza claro (#F2F2F2)
    fig.update_traces(marker_color=['#F2274C','#4d4f6e','#F2F2F2'])

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Botão para o Gráfico de Linhas na segunda coluna
if coluna2.button("Gráfico de Linhas"):
   
    fig = px.line(
        df_total,
        x='Projeto',
        y=df_total.columns[1:],  # Supondo que a 1ª coluna seja 'Projeto' e o restante sejam valores numéricos
        title="Craga_Projetos"
    )

    # Personalizando a cor das linhas
    fig.update_traces(line=dict(color='#F2F2F2'))  # Define cor cinza claro

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Botão Check
check = st.sidebar.checkbox("Exibir Dataframe Master")
if check:
    st.write('Master_Filtrada')
    st.dataframe(Master)

check1 = st.sidebar.checkbox("Exibir Dataframe CFA")
if check1:
    st.write('Lista CFA')
    st.dataframe(lista_cfa)
# ------------------------------------O P Ç Õ E S - -  P R O J E T O S - - R Á D I O ---------------------------------------
# Radio Select
opcao = st.sidebar.radio(
    "Selecione um Projeto",
    ("Geral","GEM","VS30","SPIN","BMW")
)

if opcao == "Geral": #--------------Fica somente o Geral
    st.header("Todos Projetos")
    st.image('Todos_Modelos.PNG', caption='Projetos')

elif opcao == "GEM": #--------------- Além do Geral, abaixo mostra por projeto----------------------------------------------------
    st.header("Projeto: GEM")
    st.image('GM ONIX.png', caption='Onix')

    # Ordenar o dataframe por 'Máq_Tipo' em ordem crescente
    Master = Master.sort_values(by='Máq_Tipo', ascending=True)

    # Filtra para Projeto GEM
    df_gem = Master[Master['Projeto'] == 'GEM']

    # Agrupa por 'Máq_Tipo' e soma 'total week'
    Master_total = df_gem.groupby(['Máq_Tipo'], as_index=False)['total week'].sum()
   
    # Calcula o total geral de 'total week' para o projeto GEM
    total_geral_gem = Master_total['total week'].sum()
 
    # Calcular a porcentagem de GEM em relação ao total geral
    percentual_gem = (total_geral_gem / total_geral_todos) * 100 if total_geral_todos > 0 else 0

    # Formatar os valores
    total_formatado = f"{total_geral_gem:,.0f}".replace(",", ".")
    percentual_formatado = f"{percentual_gem:,.2f}%"  # duas casas decimais
    # Criar o título formatado
    titulo = f"Carga_Máq/GEM: <span style='color:#F55D7A'> {total_formatado} ({percentual_formatado})</span>"
   
   # Criar o gráfico
    fig_date = px.bar(
        Master_total,
        x='Máq_Tipo',
        y='total week',
        title= titulo,
        text='total week'
    )

    # Definir as barras na cor branca
    fig_date.update_traces(marker_color='white', marker_line_color='black', marker_line_width=1.5)

   # Se o Plotly não interpretar HTML no título, podemos atualizar o layout para aplicar a formatação:
    fig_date.update_layout(
    title_font_color='white',
    title_font=dict(size=24)  # Aumenta o tamanho da fonte para 24, ajuste conforme necessário
    )
    st.plotly_chart(fig_date, use_container_width=True)

# Gráfico por Tipo_Projeto_GEM ---------------------------------------------------------------------------------------------
 
    #Filtrar apenas os registros do projeto GEM
    Tipos_Maq_GEM = Tipos_Maq[Tipos_Maq['Projeto'] == 'GEM']

    #Garantir que 'Máq_Tipo' seja uma categoria ordenada
    Tipos_Maq_GEM['Máq_Tipo'] = pd.Categorical(
        Tipos_Maq_GEM['Máq_Tipo'],
        categories=[
            'B01-TT', 'B02-TT', 'M03-TT', 'M15-SS', 'M16-TT', 'M17-TT', 'M18-SS', 'M19-SS',
            'M20-SS', 'M21-SS', 'M22-SS', 'M23-SS', 'M24-TT', 'M25-TT', 'M26-TT', 'M27-TS',
            'M28-TT', 'M29-TS', 'M30-TT', 'M31-TT', 'M32-S', 'M33-TT', 'M34-TT', 'M35-TT',
            'M36-TT', 'M37-SS', 'M38-TS', 'M39-SS', 'M40-TS', 'M41-TT', 'M42-TS', 'M43-TS',
            'M44-TT', 'M45-SS', 'M46-SS'
        ],
        ordered=True
    )

    #Criar uma coluna de texto para os rótulos usando Quantidade_Tipos formatado
    Tipos_Maq_GEM['texto_barra'] = Tipos_Maq_GEM['Quantidade_Tipos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
   
    #Calcular total geral do projeto GEM
    total_tipos_maq = Tipos_Maq_GEM['Quantidade_Tipos'].sum()

    #Calcular total geral de todos os projetos
    total_geral_tipos = Tipos_Maq['Quantidade_Tipos'].sum()

    #Calcular a porcentagem do GEM sobre o total
    percentual_gem = (total_tipos_maq / total_geral_tipos) * 100 if total_geral_tipos > 0 else 0

    #Formatar os valores
    total_tipos_formatado = f"{total_tipos_maq:,.0f}".replace(",", ".")
    percentual_formatado = f"{percentual_gem:,.2f}%"  # Arredondado para 2 casas decimais

    #Criar título com o total e a porcentagem em vermelho
    titulo_Tipo_GEM = f"Carga_Máq/Tipo_GEM: <span style='color:#F55D7A; font-size:24px;'> {total_tipos_formatado} ({percentual_formatado})</span>"
 
    #Criar o gráfico de barras
    fig = px.bar(
        Tipos_Maq_GEM,
        x='Máq_Tipo',
        y='Quantidade_Tipos',
        title=titulo_Tipo_GEM,
        text='texto_barra',  # Rótulo com a contagem de Quantidade_Tipos
        labels={'Máq_Tipo': 'Máquina Tipo', 'Quantidade_Tipos': 'Quantidade de Tipos'},
        barmode='stack',        
    )
    #Ajustar a cor da borda das barras para melhor visualização
    fig.update_traces(marker_line_color='black', marker_line_width=1.5)


    #Atualizar layout para a ordem correta e rotação do eixo X
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=Tipos_Maq_GEM['Máq_Tipo'].cat.categories),
        xaxis_tickangle=-45
    )

    #Definir as barras na cor vermelha
    fig.update_traces(marker_color='#F2274C', marker_line_color='black', marker_line_width=1.5)

    #Ajustar a formatação do título caso o HTML não seja interpretado
    fig.update_layout(
        title_font_color='white',
        title_font=dict(size=24)  # Aumentar o tamanho da fonte para 24
    )
    #Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)


elif opcao == "VS30":#------------------------- Dados do Projeto VS30 ----------------------------------------------------
    st.header("Dados VS30")
    st.image('MERCEDES VS30.png', caption='Sprinter')

# Ordenar o dataframe por 'Máq_Tipo' em ordem crescente
    Master = Master.sort_values(by='Máq_Tipo', ascending=True)

    # Filtra para Projeto VS30
    df_VS30 = Master[Master['Projeto'] == 'VS30']

    # Agrupa por 'Máq_Tipo' e soma 'total week'
    Master_total = df_VS30.groupby(['Máq_Tipo'], as_index=False)['total week'].sum()
   
    # Calcula o total geral de 'total week' para o projeto VS30
    total_geral_VS30 = Master_total['total week'].sum()
 
    # Calcular a porcentagem de GEM em relação ao total geral
    percentual_VS30 = (total_geral_VS30 / total_geral_todos) * 100 if total_geral_todos > 0 else 0

    # Formatar os valores
    total_formatado = f"{total_geral_VS30:,.0f}".replace(",", ".")
    percentual_formatado = f"{percentual_VS30:,.2f}%"  # duas casas decimais
    # Criar o título formatado
    titulo = f"Carga_Máq/VS30: <span style='color:#F55D7A'> {total_formatado} ({percentual_formatado})</span>"
   
   # Criar o gráfico
    fig_date = px.bar(
        Master_total,
        x='Máq_Tipo',
        y='total week',
        title= titulo,
        text='total week'
    )
    # Definir as barras na cor branca
    fig_date.update_traces(marker_color='white', marker_line_color='black', marker_line_width=1.5)

   # Se o Plotly não interpretar HTML no título, podemos atualizar o layout para aplicar a formatação:
    fig_date.update_layout(
    title_font_color='white',
    title_font=dict(size=24)  # Aumenta o tamanho da fonte para 24, ajuste conforme necessário
    )
    st.plotly_chart(fig_date, use_container_width=True)

# Gráfico por Tipo_Projeto_VS30 ---------------------------------------------------------------------------------------------

 # Filtrar apenas os registros do projeto VS30
    Tipos_Maq_VS30 = Tipos_Maq[Tipos_Maq['Projeto'] == 'VS30']

    # Garantir que 'Máq_Tipo' seja uma categoria ordenada
    Tipos_Maq_VS30['Máq_Tipo'] = pd.Categorical(
        Tipos_Maq_VS30['Máq_Tipo'],
        categories=[
            'B01-TT', 'B02-TT', 'M03-TT', 'M15-SS', 'M16-TT', 'M17-TT', 'M18-SS', 'M19-SS',
            'M20-SS', 'M21-SS', 'M22-SS', 'M23-SS', 'M24-TT', 'M25-TT', 'M26-TT', 'M27-TS',
            'M28-TT', 'M29-TS', 'M30-TT', 'M31-TT', 'M32-S', 'M33-TT', 'M34-TT', 'M35-TT',
            'M36-TT', 'M37-SS', 'M38-TS', 'M39-SS', 'M40-TS', 'M41-TT', 'M42-TS', 'M43-TS',
            'M44-TT', 'M45-SS', 'M46-SS'
        ],
        ordered=True
    )

    # Criar uma coluna de texto para os rótulos usando Quantidade_Tipos formatado
    Tipos_Maq_VS30['texto_barra'] = Tipos_Maq_VS30['Quantidade_Tipos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    # Calcular total geral do projeto GEM
    total_tipos_maq = Tipos_Maq_VS30['Quantidade_Tipos'].sum()

    # Calcular total geral de todos os projetos
    total_geral_tipos = Tipos_Maq['Quantidade_Tipos'].sum()

    # Calcular a porcentagem do GEM sobre o total
    percentual_VS30 = (total_tipos_maq / total_geral_tipos) * 100 if total_geral_tipos > 0 else 0

    # Formatar os valores
    total_tipos_formatado = f"{total_tipos_maq:,.0f}".replace(",", ".")
    percentual_formatado = f"{percentual_VS30:,.2f}%"  # Arredondado para 2 casas decimais

    # Criar título com o total e a porcentagem em vermelho
    titulo_Tipo_VS30 = f"Carga_Máq/Tipo_VS30:<span style='color:#F55D7A; font-size:24px;'> {total_tipos_formatado} ({percentual_formatado})</span>"

    # Criar o gráfico de barras
    fig = px.bar(
        Tipos_Maq_VS30,
        x='Máq_Tipo',
        y='Quantidade_Tipos',
        title=titulo_Tipo_VS30,
        text='texto_barra',  # Rótulo com a contagem de Quantidade_Tipos
        labels={'Máq_Tipo': 'Máquina Tipo', 'Quantidade_Tipos': 'Quantidade de Tipos'},
        barmode='stack',        
    )

    # Ajustar a cor da borda das barras para melhor visualização
    fig.update_traces(marker_line_color='black', marker_line_width=1.5)

    # Atualizar layout para a ordem correta e rotação do eixo X
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=Tipos_Maq_VS30['Máq_Tipo'].cat.categories),
        xaxis_tickangle=-45
    )

    # Definir as barras na cor vermelha
    fig.update_traces(marker_color='#F2274C', marker_line_color='black', marker_line_width=1.5)

    # Ajustar a formatação do título caso o HTML não seja interpretado
    fig.update_layout(
        title_font_color='white',
        title_font=dict(size=24)  # Aumentar o tamanho da fonte para 24
    )
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

elif opcao == "SPIN":#------------------------- Dados do Projeto SPIN ----------------------------------------------------
    st.header("Dados SPIN")
    st.image('GM SPIN Cinza.png', caption='Chevrolet')

    # Ordenar o dataframe por 'Máq_Tipo' em ordem crescente
    Master = Master.sort_values(by='Máq_Tipo', ascending=True)

    # Filtra para Projeto SPIN
    df_SPIN = Master[Master['Projeto'] == 'SPIN']

    # Agrupa por 'Máq_Tipo' e soma 'total week'
    Master_total = df_SPIN.groupby(['Máq_Tipo'], as_index=False)['total week'].sum()
   
    # Calcula o total geral de 'total week' para o projeto VS30
    total_geral_SPIN = Master_total['total week'].sum()
 
    # Calcular a porcentagem de GEM em relação ao total geral
    percentual_SPIN = (total_geral_SPIN / total_geral_todos) * 100 if total_geral_todos > 0 else 0

    # Formatar os valores
    total_formatado = f"{total_geral_SPIN:,.0f}".replace(",", ".")
    percentual_formatado = f"{percentual_SPIN:,.2f}%"  # duas casas decimais

    # Criar o título formatado
    titulo = f"Carga_Máq/SPIN: <span style='color:#F55D7A'> {total_formatado} ({percentual_formatado})</span>"
   
   # Criar o gráfico
    fig_date = px.bar(
        Master_total,
        x='Máq_Tipo',
        y='total week',
        title= titulo,
        text='total week'
    )

    # Definir as barras na cor branca
    fig_date.update_traces(marker_color='white', marker_line_color='black', marker_line_width=1.5)

   # Se o Plotly não interpretar HTML no título, podemos atualizar o layout para aplicar a formatação:
    fig_date.update_layout(
    title_font_color='white',
    title_font=dict(size=24)  # Aumenta o tamanho da fonte para 24, ajuste conforme necessário
    )
    st.plotly_chart(fig_date, use_container_width=True)


# Gráfico por Tipo_Projeto_SPIN ---------------------------------------------------------------------------------------------
 # Filtrar apenas os registros do projeto SPIN
    Tipos_Maq_SPIN = Tipos_Maq[Tipos_Maq['Projeto'] == 'SPIN']

    # Garantir que 'Máq_Tipo' seja uma categoria ordenada
    Tipos_Maq_SPIN['Máq_Tipo'] = pd.Categorical(
        Tipos_Maq_SPIN['Máq_Tipo'],
        categories=[
            'B01-TT', 'B02-TT', 'M03-TT', 'M15-SS', 'M16-TT', 'M17-TT', 'M18-SS', 'M19-SS',
            'M20-SS', 'M21-SS', 'M22-SS', 'M23-SS', 'M24-TT', 'M25-TT', 'M26-TT', 'M27-TS',
            'M28-TT', 'M29-TS', 'M30-TT', 'M31-TT', 'M32-S', 'M33-TT', 'M34-TT', 'M35-TT',
            'M36-TT', 'M37-SS', 'M38-TS', 'M39-SS', 'M40-TS', 'M41-TT', 'M42-TS', 'M43-TS',
            'M44-TT', 'M45-SS', 'M46-SS'
        ],
        ordered=True
    )

    # Criar uma coluna de texto para os rótulos usando Quantidade_Tipos formatado
    Tipos_Maq_SPIN['texto_barra'] = Tipos_Maq_SPIN['Quantidade_Tipos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    # Calcular total geral do projeto GEM
    total_tipos_maq = Tipos_Maq_SPIN['Quantidade_Tipos'].sum()

    # Calcular total geral de todos os projetos
    total_geral_tipos = Tipos_Maq['Quantidade_Tipos'].sum()

    # Calcular a porcentagem do GEM sobre o total
    percentual_SPIN = (total_tipos_maq / total_geral_tipos) * 100 if total_geral_tipos > 0 else 0

    # Formatar os valores
    total_tipos_formatado = f"{total_tipos_maq:,.0f}".replace(",", ".")
    percentual_formatado = f"{percentual_SPIN:,.2f}%"  # Arredondado para 2 casas decimais

    # Criar título com o total e a porcentagem em vermelho
    titulo_Tipo_SPIN = f"Carga_Máq/Tipo_SPIN: <span style='color:#F55D7A; font-size:24px;'> {total_tipos_formatado} ({percentual_formatado})</span>"

    # Criar o gráfico de barras
    fig = px.bar(
        Tipos_Maq_SPIN,
        x='Máq_Tipo',
        y='Quantidade_Tipos',
        title=titulo_Tipo_SPIN,
        text='texto_barra',  # Rótulo com a contagem de Quantidade_Tipos
        labels={'Máq_Tipo': 'Máquina Tipo', 'Quantidade_Tipos': 'Quantidade de Tipos'},
        barmode='stack',        
    )

    # Ajustar a cor da borda das barras para melhor visualização
    fig.update_traces(marker_line_color='black', marker_line_width=1.5)

    # Atualizar layout para a ordem correta e rotação do eixo X
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=Tipos_Maq_SPIN['Máq_Tipo'].cat.categories),
        xaxis_tickangle=-45
    )

    # Definir as barras na cor vermelha
    fig.update_traces(marker_color='#F2274C', marker_line_color='black', marker_line_width=1.5)

    # Ajustar a formatação do título caso o HTML não seja interpretado
    fig.update_layout(
        title_font_color='white',
        title_font=dict(size=24)  # Aumentar o tamanho da fonte para 24
    )
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

elif opcao == "BMW": #------------------------- Dados do Projeto BMW ----------------------------------------------------
    st.header("Dados BMW")
    st.image('BMW X-1.png', caption='X-1')

# =============================================== S E L E C T -- B O X ===================================================
opcao = st.sidebar.selectbox(
    "Selecione dados do Gráfico",
    ("Carga_Máq","Tipos","Meta")
)
fig_date = None  # Inicializa a variável para evitar erro caso a opção não seja encontrada

if opcao == "Carga_Máq":
   
    # Ordenar o dataframe por 'Máq_Tipo' em ordem crescente
    Master = Master.sort_values(by='Máq_Tipo', ascending=True)

    # Agrupar por 'Máq_Tipo'
    Master_total_Geral = Master.groupby('Máq_Tipo', as_index=False)['total week'].sum()

    # Calcular o total geral e formatar
    total_geral = Master_total_Geral['total week'].sum()
    total_formatado = f"{total_geral:,.0f}".replace(",", ".")
    titulo_total_geral = f"Carga_Máq/Geral: <span style='color:#F55D7A'> {total_formatado}</span>"

    # Formatar os valores da coluna 'total week' para incluir separador de milhares
    Master_total_Geral['total week'] = Master_total_Geral['total week'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    # Usar o DataFrame Master_total_Geral no gráfico
    fig_date = px.bar(
        Master_total_Geral,  # Aqui era total_geral, mas deve ser o DataFrame
        x='Máq_Tipo',
        y='total week',
        title=titulo_total_geral,
        text='total week'
    )
    # Definir as barras na cor branca
    fig_date.update_traces(marker_color='white', marker_line_color='black', marker_line_width=1.5)

    # Atualizar layout do título
    fig_date.update_layout(
        title_font_color='white',
        title_font=dict(size=24)
    )
    st.plotly_chart(fig_date, use_container_width=True)

if opcao == "Meta":
    df = pd.DataFrame(
       np.random.rand(10,1),
      columns=['Meta']
    )
    st.line_chart(df)
#============================================== M-U-L-T-I---S-E-L-E-C-T ========================================================

opcao = st.sidebar.multiselect(
    "Selecione Multi dados do Gráfico",
    ("Projeto","Tipos","Pizza"), # Para vir selecionado, e o nome
    ("Projeto")
)
if "Projeto" in opcao:
   
    # Garantir que a coluna 'Projeto' seja tratada como string
    Master['Projeto'] = Master['Projeto'].astype(str)

    # Corrigir a soma groupby das colunas e resetar o índice
    df_Projeto = Master.groupby(['Projeto', 'Máq_Tipo'], as_index=False)['total week'].sum()
   
    # Criar um dataframe com o total por projeto
    total_por_projeto = df_Projeto.groupby('Projeto', as_index=False)['total week'].sum()

    # Formatar os totais para exibição no título
    totais_formatados = " - ".join([
        f"{projeto}: {total:,.0f}".replace(",", ".")
        for projeto, total in zip(total_por_projeto['Projeto'], total_por_projeto['total week'])
    ])

    # Criar título com os totais por projeto
    titulo_Projeto = f"Carga_Máq/Projeto_Geral: <span style='color:#F55D7A; font-size:24px;'> {totais_formatados}</span>"

    # Ordenar o dataframe por 'Máq_Tipo' em ordem crescente
    df_Projeto = df_Projeto.sort_values(by='Máq_Tipo', ascending=True)

    # Definir a ordem das categorias explicitamente
    ordem_maq = sorted(df_Projeto['Máq_Tipo'].unique())

    # Formatar os valores de 'total week' para exibir com pontos como separadores de milhares
    df_Projeto['total week formatado'] = df_Projeto['total week'].apply(lambda x: f'{x:,.0f}'.replace(',', '.'))

    # Criar o gráfico de barras com rótulos
    fig_date = px.bar(
        df_Projeto,
        x='Máq_Tipo',
        y='total week',
        color='Projeto',
        title=titulo_Projeto,
        text='total week formatado',  # Adiciona os rótulos nas barras
        category_orders={'Máq_Tipo': ordem_maq},  # Define a ordem do eixo x
        color_discrete_sequence=['#F2274C','#F2F2F2','#4d4f6e','#CAC60C']
    )
   
    # Rotacionar os rótulos do eixo X em 30 graus
    fig_date.update_xaxes(tickangle=30)

    # Atualizar layout do título
    fig_date.update_layout(
        title_font_color='white',
        title_font=dict(size=24)
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig_date, use_container_width=True, key=f"chart_{opcao}")

if "Tipos" in opcao:
     
    # Garantir que 'Máq_Tipo' seja uma categoria ordenada
    Tipos_Maq['Máq_Tipo'] = pd.Categorical(
        Tipos_Maq['Máq_Tipo'],
        categories=[
            'B01-TT', 'B02-TT', 'M03-TT', 'M15-SS', 'M16-TT', 'M17-TT', 'M18-SS', 'M19-SS',
            'M20-SS', 'M21-SS', 'M22-SS', 'M23-SS', 'M24-TT', 'M25-TT', 'M26-TT', 'M27-TS',
            'M28-TT', 'M29-TS', 'M30-TT', 'M31-TT', 'M32-S', 'M33-TT', 'M34-TT', 'M35-TT',
            'M36-TT', 'M37-SS', 'M38-TS', 'M39-SS', 'M40-TS', 'M41-TT', 'M42-TS', 'M43-TS',
            'M44-TT', 'M45-SS', 'M46-SS'
        ],
        ordered=True
    )  
    # Criar uma coluna de texto para os rótulos usando Quantidade_Tipos
    Tipos_Maq['texto_barra'] = Tipos_Maq['Quantidade_Tipos'].astype(str)

    # Calcular total geral de todos os projetos
    total_geral_tipos = Tipos_Maq['Quantidade_Tipos'].sum()


    # Formatar os valores
    total_tipos_formatado = f"{total_geral_tipos:,.0f}".replace(",", ".")# Arredondado para 2 casas decimais

    # Criar título com o total
    titulo_Total_Tipos = f"Carga_Máq/Tipo_Geral: <span style='color:#F55D7A; font-size:24px;'> {total_tipos_formatado}"

    # Criar o gráfico de barras
    fig = px.bar(
        Tipos_Maq,
        x='Máq_Tipo',
        y='Quantidade_Tipos',
        color='Projeto',
        title=titulo_Total_Tipos,
        text='texto_barra',  # Rótulo com a contagem de Quantidade_Tipos
        labels={'Máq_Tipo': 'Máquina Tipo', 'Quantidade_Tipos': 'Quantidade de Tipos'},
        barmode='stack',
        color_discrete_sequence=['#F2274C', '#4d4f6e', '#F2F2F2']
    )  
    # Atualizar layout para a ordem correta
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=Tipos_Maq['Máq_Tipo'].cat.categories),
        xaxis_tickangle=-45,
        title_font=dict(size=24)  # Definir tamanho da fonte do título
    )
    st.plotly_chart(fig, use_container_width=True)


if "Pizza" in opcao:
    # Agrupar os dados somando 'total week' por 'Projeto'
    df_pizza = Master.groupby('Projeto', as_index=False)['total week'].sum()

    # Definir cores personalizadas
    custom_colors = ['#F2274C', '#4d4f6e', '#F2F2F2']

    # Criar o gráfico de pizza aprimorado
    fig_pizza = px.pie(
        df_pizza,
        names='Projeto',
        values='total week',
        title="%_Carga_Projeto",
        hole=0.2,  # Deixa um espaço no centro para efeito "rosca"
        color_discrete_sequence=custom_colors  # Aplicando cores personalizadas
    )

    # Melhorar o layout
    fig_pizza.update_traces(
        textinfo='percent+label',  # Exibe porcentagem e nome do projeto
        marker=dict(line=dict(color='#000000', width=1.5)),  # Adiciona borda preta nas fatias
        pull=[0.1 if i == df_pizza['total week'].idxmax() else 0 for i in range(len(df_pizza))]  # Destaca maior fatia
    )

    # Ajustar o design do gráfico
    fig_pizza.update_layout(
        showlegend=True,
        legend_title="Projetos",
        template="plotly_dark",  # Estilo visual escuro
    )
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig_pizza, use_container_width=True, key="chart_pizza")

opcao= st.sidebar.slider(
    "Definir Intervalo de Dados",
    0.0,100.0, (25.0, 75.0))
#=============================================== UPLOAD ============================================================
import pdfplumber

# Componente para upload de arquivos
if 'arquivo' not in st.session_state:
    st.session_state['arquivo'] = None

arquivo = st.sidebar.file_uploader("Carregar arquivo", type=["json", "csv", "xlsx", "py", "mp3", "mp4", "pdf", "jpeg", "png", "bmp"])
         
if arquivo:
    st.sidebar.write(f"Tipo do arquivo: {arquivo.type}")

    match arquivo.type.split('/'):
        case ['application', 'json']:
            dados_json = loads(arquivo.read().decode('utf-8'))
            st.json(dados_json)

        case ['image', _]:
            st.image(arquivo)

        case ['text', 'csv']:
            df = pd.read_csv(arquivo)  # Lê o CSV
            st.dataframe(df)
            #st.line_chart(df)  # Exibe um gráfico de linhas

        case ['application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet']:  # Para XLSX
            df = pd.read_excel(arquivo)#, sheet_name='Base')  # Lê o Excel
            st.dataframe(df)
            #st.line_chart(df) # Exibe um gráfico de linhas

        case ['text', 'x-python']:
            st.code(arquivo.read().decode())

        case ['audio', _]:
            st.audio(arquivo)
 
        case ['application', 'pdf']:
            # Carregar o arquivo PDF
            doc = fitz.open(stream=arquivo.read(), filetype='pdf')
            num_pages = doc.page_count
            for i in range(num_pages):
                page = doc.load_page(i)
                pix = page.get_pixmap()
                img = Image.open(BytesIO(pix.tobytes()))
                st.image(img, caption=f'Página {i+1}')

    # Se for um arquivo de vídeo, Streamlit pode renderizá-lo
    if 'video' in arquivo.type:
        st.video(arquivo)
else:
    st.sidebar.error('Carregue qualquer tipo de arquivo...')

#===================================== NOVO BROWSE == EXTRAIR TEXTO =================================================


def display_pdf(file):
    """Exibe o texto extraído de um arquivo PDF."""
    with pdfplumber.open(file) as pdf:
        text = "\n\n".join(
            page.extract_text() or "[Formato de arquivo não suportado. Ex: Scanner/Foto.]" 
            for page in pdf.pages
        )
        if text.strip():
            st.markdown("<h3>📄 Texto extraído do PDF:</h3>", unsafe_allow_html=True)
            st.text_area("", text, height=400)
        else:
            st.markdown("<h3 style='color: red;'>🛑 [Formato de arquivo não suportado. Ex: Scanner/Foto.]</h3>", unsafe_allow_html=True)

# Upload do arquivo
arquivo = st.sidebar.file_uploader("Extrair Texto de PDF", type=["pdf"])

if arquivo:
    st.sidebar.write(f"Tipo do arquivo: {arquivo.type}")

    if arquivo.type == "application/pdf":
        display_pdf(arquivo)
    else:
        st.sidebar.error("Formato de arquivo não suportado.")
else:
    st.sidebar.warning("Carregue um arquivo PDF...")


#===================================== Finalizando - o - Código  ===================================================
print("\n=== Finalizando o Código ===\n")

Horario_Fim = dt.datetime.now()
Tempo_Execucao = Horario_Fim - Horario_Inicio

# Mensagem final
now = dt.datetime.now() # Obtém a data e hora atual
formatted_date = now.strftime('%d-%m-%Y') # Formata a data conforme desejado (dia-mês-ano)
formatted_time = now.strftime('%H:%M:%S') # Formata apenas a parte do horário (hora:minuto:segundo)

print(formatted_date, formatted_time) # Retorna a data e hora

Hora_Inicio_formatada= Horario_Inicio.strftime('%H:%M:%S') # Formatar apenas a parte do horário (hora:minuto:segundo)
Hora_Fim_formatada= Horario_Fim.strftime('%H:%M:%S') # Formata a data conforme desejado (dia-mês-ano)

print(f'Horario_Inicio   : {Hora_Inicio_formatada}')
print(f'Horario_Fim      : {Hora_Fim_formatada}')
print(f'Tempo de execução: {Tempo_Execucao}\n')