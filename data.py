
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
from os import listdir
from os.path import isfile, join
from datetime import datetime

#Ruta de los archivos

def ruta_arch(ruta):
    """
    :param ruta:
    :return:
    """
    archivos = [f[:-4] for f in listdir(ruta) if isfile(join(ruta, f))]
    #ordena los archivos dependiendo de sus fechas
    archivos = sorted(archivos, key=lambda day: datetime.strptime(day[8:], '%d%m%y'))
    return archivos
# crear un diccionario para almacenar todos los datos
def diccionario_datos(archivos):
    data_archivos = {}
    for i in archivos:
        #omitir los primero dos renglones (no contienen información) de cada archivo
        datos = pd.read_csv('NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None)
        #renombrar correctamente las columnas
        datos.columns = list(datos.iloc[0, :])
        datos = datos.loc[:, pd.notnull(datos.columns)]
        datos = datos.iloc[1:-1].reset_index(drop=True, inplace=False)
        # correcciones para el mejor manejo de los archivos
        # quitar comas de los precios
        datos['Precio'] = [i.replace(',', '') for i in datos['Precio']]
        # eliminar los asteriscos
        datos['Ticker'] = [i.replace('*', '') for i in datos['Ticker']]
        #hacer numerica la columna precio
        convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
        datos = datos.astype(convert_dict)
        # convertir la columna de peso a decimal
        datos['Peso (%)'] = datos['Peso (%)'] / 100
        # guardar el diccionario
        data_archivos[i] = datos
    return data_archivos
