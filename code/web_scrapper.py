#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import datetime

parametros = ['Valor. Régimen general y minería del carbón',
             'Valor. Autónomos',
             'Valor. Total',
              '% Variación interanual. Régimen general y minería del carbón',
              '% Variación interanual. Autónomos',
              '% Variación interanual. Total'
             ]

"Header columnas tabla"
header_valores='Año','Mes','Region','Regimen','Sector','Valor'
header_variacion='Año','Mes','Region','Regimen','Sector','% Variacion interanual'
df_valores = pd.DataFrame(columns = header_valores)
df_variacion = pd.DataFrame(columns = header_variacion)

for pag in range(len(parametros)):
    r = requests.get('https://www.idescat.cat/indicadors/?id=conj&n=10222&t=202102&lang=es&col='+str(pag+1))
    soup = BeautifulSoup(r.text, 'lxml')
    "Se obtienen las dos tablas"
    tablas = soup.find_all('table', attrs={'class': 'ApartNum xs Cols7'})

    output_filename = tablas[0].find_all('span', attrs={'class': 'grup'})[0].contents[0].split('.')[0]

    row_values=[]
    for i,tabla in enumerate(tablas):
        #Variables fijas por cada tabla
        region = tabla.find_all('span', attrs={'class': 'grup'})[1].contents[0]
        tipo = tabla.find_all('span', attrs={'class': 'grup'})[2].contents[0].split(". ")[0]
        regimen = tabla.find_all('span', attrs={'class': 'grup'})[2].contents[0].split(". ")[1]
        #Variables dinámicas
        for row in range(len(tablas[i].find_all('tr')[1:-7])):
            mes = tablas[i].find_all('tr')[1:-7][row].find_all('th', attrs={'scope': 'row'})[0].contents[0].split('/')[0]
            año = tablas[i].find_all('tr')[1:-7][row].find_all('th', attrs={'scope': 'row'})[0].contents[0].split('/')[1]
            for sect in range(len(tablas[i].find_all('tr')[1:-7][row].find_all('td'))):
                sector = tablas[i].find_all('tr')[1:-7][row].find_all('td')[sect]['data-title']
                val_num = tablas[i].find_all('tr')[1:-7][row].find_all('td', attrs={'data-title': sector})[0].contents[0]
                row_values.append(año)
                row_values.append(mes)
                row_values.append(region)
                row_values.append(regimen)
                row_values.append(sector)
                row_values.append(val_num)
                if tipo == 'Valor':
                    df_length = len(df_valores)
                    df_valores.loc[df_length] = row_values
                elif tipo == '% Variación interanual':
                    df_length = len(df_variacion)
                    df_variacion.loc[df_length] = row_values
                row_values.clear()
            

final_df = df_valores.set_index(['Año','Mes','Region','Regimen','Sector']).join(df_variacion.set_index(['Año','Mes','Region','Regimen','Sector']))
final_df.to_csv(output_filename+'.csv',encoding='utf-8-sig')
