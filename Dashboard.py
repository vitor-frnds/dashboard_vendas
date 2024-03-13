##Import das Bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
#----------------------------------------------------------------

##Setar a forma de visualização da aplicação
st.set_page_config(layout = 'wide',
                   page_title = '1ª Aplicação com o Streamlit',
                   page_icon = '')

#----------------------------------------------------------------

##Funções
#Função para formatar números:
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

#----------------------------------------------------------------

# Adicionar Título ao Aplicativo
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}

#Requisição dos dados
response = requests.get(url, params = query_string)
#Transformar a requisição em um JSON e transformar o JSON em um dataframe
dados = pd.DataFrame.from_dict(response.json())
#Alterar o formato da coluna para o datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

#----------------------------------------------------------------

##Tabelas
#Tabelas para os gráficos de receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum() 
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

#----------------------------------------------------------------

#Tabelas para os gráficos de Quantidade de Vendas
#Agrupar por 'Local da compra' e contar o número de vendas e Mesclar com as coordenadas geográficas
vendas_estados = dados.groupby('Local da compra').size()
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados.rename('Vendas'), left_on = 'Local da compra', right_index = True).sort_values('Vendas', ascending = False)

#Agrupar por 'Data de Compra' e contar o número de vendas
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M')).size().reset_index(name = 'Vendas')
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto').size().rename('Vendas').sort_values(ascending = False)

#----------------------------------------------------------------

#Tabelas para os gráficos de Vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

#----------------------------------------------------------------

##Gráficos
#Gráficas da aba receita:
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')
#Alterar a label do eixo Y
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(), 
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Top Estados (receita)')
#Alterar a label do eixo Y
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por Categoria')
#Alterar a label do eixo Y
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

#Gráficos da aba Quantidade de Vendas:
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Vendas',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                 hover_data = {'lat': False, 'lon': False},
                                 title = 'Quantidade de Vendas por Estado')

fig_vendas_mensal = px.line(vendas_mensal,
                            x = 'Mes',
                            y = 'Vendas',
                            markers = True,
                            range_y = (0, vendas_mensal['Vendas'].max() + 100),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Vendas Mensais')
#ALterar a label do eixo Y
fig_vendas_mensal.update_layout(yaxis_title = 'Vendas')

fig_vendas_estados = px.bar(vendas_estados.head(), 
                            x = 'Local da compra',
                            y = 'Vendas',
                            text_auto = True,
                            title = 'Top Estados (Vendas)')
#Alterar a label do eixo Y
fig_vendas_estados.update_layout(yaxis_title = 'Vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto = True,
                                title = 'Vendas por Categoria')
#Alterar a label do eixo Y
fig_vendas_categorias.update_layout(yaxis_title = 'Vendas')

#----------------------------------------------------------------

## Visualizacao no Streamlit
#Construção das abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    #Exibir métricas em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)
with aba2:
    #Exibir métricas em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)
with aba3:
    #Mínimo de 2, máximo de 10, padrão igual a 5
    qtd_vendedores = st.number_input('Quantidad de Vendedores', 2, 10, 5)

    #Exibir métricas em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True, #Adiciona os valores das receitas nas barras
                                        title = f'Top {qtd_vendedores} vendedores (receita)'
                                        )
        st.plotly_chart(fig_receita_vendedores, use_container_width = True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores.sort_values('count', ascending = False).head(qtd_vendedores),
                               x = 'count',
                               y = vendedores.sort_values('count', ascending = False).head(qtd_vendedores).index,
                               text_auto = True, #Adiciona os valores das receitas nas barras
                               title = f'Top {qtd_vendedores} vendedores (vendas)'
                               )
        st.plotly_chart(fig_vendas_vendedores, use_container_width = True)

#Exibir o dataframe no app
#st.dataframe(dados, use_container_width = True)
#----------------------------------------------------------------