
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
import numpy as np
import yfinance as yf
import time as time
from data import diccionario_datos

def ti_fechas(archivos):
    # Estas fechas serviran como etiquetas en dataframe y para yfinance
    t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]
    # lista con fechas ordenadas
    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]
    archivos = ['NAFTRAC_' + i.strftime('%d%m%y') for i in sorted(pd.to_datetime(i_fechas))]
    # final data to return
    r_f_fechas = {'i_fechas': i_fechas, 't_fechas': t_fechas}
    return t_fechas,i_fechas,archivos,r_f_fechas


#Construir el vector de tickers utilizables en yahoo finance

def todos_tickers(archivos):
    ticker = []
    for i in archivos:
        l_ticker = list(diccionario_datos(archivos)[i]['Ticker'])
        for i in l_ticker:
            ticker.append(i + '.MX')
    todos_los_tickers = np.unique(ticker).tolist()

    # ajustar el nombre de algunos tickers
    todos_los_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in todos_los_tickers]
    todos_los_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in todos_los_tickers]
    todos_los_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in todos_los_tickers]
    # eliminar los que no sirvan
    [todos_los_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'BSMXB.MX', 'KOFUBL.MX']]
    return todos_los_tickers


def yfin_close(todos_los_tickers,i_fechas):
    # Descargar y acomodar todos los precios historicos de close
    inicio = time.time()
    # descarga de precios de yahoo.finance
    datos = yf.download(todos_los_tickers, start="2018-01-31", end="2020-08-21", actions=False,group_by="close", interval='1d', auto_adjust=False, prepost=False, threads=True)
    # convertir columna de fechas
    data_close = pd.DataFrame({i: datos[i]['Close'] for i in todos_los_tickers})
    # tomar solo las fechas de interes
    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(i_fechas)))
    # localizar todos los precios
    precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == i)[0]) for i in ic_fechas]]
    # ordenar columnas
    precios = precios.reindex(sorted(precios.columns), axis=1)
    return(data_close,ic_fechas,precios)

def yfin_open(todos_los_tickers,i_fechas):
    # Descargar y acomodar todos los precios historicos de open
    inicio = time.time()
    # descarga de precios de yahoo.finance
    data_open_d = yf.download(todos_los_tickers, start="2018-01-31", end="2020-08-21", actions=False,group_by="open", interval='1d', auto_adjust=False, prepost=False, threads=True)
    # convertir columna de fechas
    data_open = pd.DataFrame({i: data_open_d[i]['Open'] for i in todos_los_tickers})
    # tomar solo las fechas de interes
    ic_fechas_open = sorted(list(set(data_open.index.astype(str).tolist()) & set(i_fechas)))
    # localizar todos los precios
    precios_open = data_open.iloc[[int(np.where(data_open.index.astype(str) == i)[0]) for i in ic_fechas_open]]
    # ordenar columnas
    precios_open = precios_open.reindex(sorted(precios_open.columns), axis=1)
    return(data_open,ic_fechas_open,precios_open)

# posicion inicial
k = 1000000
# comision por transaccion
c = 0.00125
# vector de comisiones historicas
comisiones = []

def inversion_pasiva(data_archivos,archivos,precios,t_fechas,ic_fechas,k,c):
    # obtener posicion inicial
    # los % para c_activos asignarlos a cash
    c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
    # diccionario para resultado final
    df_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}

    datos_pasiva = data_archivos[archivos[0]].copy().sort_values('Ticker')[
        ['Ticker', 'Nombre', 'Peso (%)']]
    i_activos = list(datos_pasiva[list(datos_pasiva['Ticker'].isin(c_activos))].index)
    # eliminar activos del dataframe
    datos_pasiva.drop(i_activos, inplace=True)
    # resetear index
    datos_pasiva.reset_index(inplace=True, drop=True)
    # agregar .MX para no tener problema con los precios
    datos_pasiva['Ticker'] = datos_pasiva['Ticker'] + '.MX'
    # corregir tickers
    datos_pasiva['Ticker'] = datos_pasiva['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
    datos_pasiva['Ticker'] = datos_pasiva['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    datos_pasiva['Ticker'] = datos_pasiva['Ticker'].replace('GFREGIOO.MX', 'RA.MX')
    igualar_f = precios.index[precios.index == t_fechas[0]][0]

    # precios necesarios para la posicion
    n1 = np.array(precios.loc[igualar_f, [i in datos_pasiva['Ticker'].to_list()
                                          for i in precios.columns.to_list()]])
    datos_pasiva['Precios'] = n1
    datos_pasiva['Capital'] = datos_pasiva['Peso (%)'] * k - datos_pasiva['Peso (%)'] * k * c
    datos_pasiva['Titulos'] = datos_pasiva['Capital'] // datos_pasiva['Precios']
    datos_pasiva['Postura'] = datos_pasiva['Titulos'] * datos_pasiva['Precios']
    datos_pasiva['Comision'] = datos_pasiva['Postura'] * c
    pos_cash = k - datos_pasiva['Postura'].sum() - datos_pasiva['Comision'].sum()

        #Valor de la postura por accion
    for i in range(1, len(ic_fechas)):
        igualar_f = precios.index[precios.index == ic_fechas[i]][0]

        # precios necesarios para la posicion
        n1 = np.array(precios.loc[igualar_f, [i in datos_pasiva['Ticker'].to_list() for i in precios.columns.to_list()]])
        # cantidad de titulos por acción
        datos_pasiva['Precios'] = n1
        datos_pasiva['Postura'] = datos_pasiva['Titulos'] * datos_pasiva['Precios']

        #valor de la posicion
        pos_value = datos_pasiva['Postura'].sum()

        # actualizar lista de valores en el diccionario
        df_pasiva['timestamp'].append(t_fechas[i])
        df_pasiva['capital'].append(pos_value + pos_cash)
    capital = list(df_pasiva['capital'])
    rendimiento = [0] + [(capital[i] - capital[i-1])/capital[i] for i in range(1,len(capital))]
    df_pasiva['rendimiento'] = rendimiento
    rend_acum = [0]
    for i in rendimiento[1:]:
        rend_acum.append(rend_acum[-1] + i)

    df_pasiva['rend_acum'] = rend_acum
    df_pasiva = pd.DataFrame(df_pasiva)
    return df_pasiva

#ACTIVA

x_p = 0.01
kc = 0.1

def inversion_activa(data_archivos,archivos,data_close,data_open,c,x_p,kc,k):
    inversion_activa = {'timestamp': ['30-01-2018'], 'capital': [k]}
    operacion_inv_activa = {'timestamp': [], 'titulos_t': [], 'titulos_c': [], 'precio': [], 'comision': [], 'cash': []}
    c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD'] #se asignan a cash
    comisiones = [0] #lista de comisiones
    datos_activa = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Peso (%)']]
    i_activos = list(datos_activa[list(datos_activa['Ticker'].isin(c_activos))].index)
    datos_activa.drop(i_activos, inplace=True)
    datos_activa.reset_index(inplace=True, drop=True)
    datos_activa['Ticker'] = datos_activa['Ticker'] + '.MX'
    datos_activa['Ticker'] = datos_activa['Ticker'].replace('GFREGIOO.MX', 'RA.MX')
    datos_activa['Ticker'] = datos_activa['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    datos_activa['Ticker'] = datos_activa['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
    #activo de mayor ponderacion
    peso_max = datos_activa['Peso (%)'].idxmax()

    datos_activa['Precio'] = np.round(np.array([data_close.iloc[0, data_close.columns.to_list().index(i)] for i in datos_activa['Ticker']]), 2)
    datos_activa['Precio_open'] = np.round(np.array([data_close.iloc[0, data_close.columns.to_list().index(i)] for i in datos_activa['Ticker']]), 2)
    datos_activa['Precio_c'] = 0
    datos_activa['Capital'] = np.round(datos_activa['Peso (%)'] * k - datos_activa['Peso (%)'] * k * c, 2)
    # Ajustas a solo el 50%
    datos_activa.loc[peso_max, 'Capital'] = datos_activa.loc[peso_max, 'Capital'] / 2
    datos_activa['Titulos'] = datos_activa['Capital'] // datos_activa['Precio']
    datos_activa['Comision'] = np.round(datos_activa['Precio'] * datos_activa['Titulos'] * c, 2)
    datos_activa['Postura'] = datos_activa['Titulos'] * datos_activa['Precio']
    cash = np.round(k - datos_activa['Postura'].sum() - datos_activa['Comision'].sum(), 2)

    inversion_activa['capital'].append(k - datos_activa['Comision'].sum())
    comisiones.append(sum(datos_activa['Comision']))
    inversion_activa['timestamp'].append(str(data_close.index[0].strftime('%Y-%m-%d')))

    operacion_inv_activa['timestamp'].append(str(data_close.index[0].strftime('%Y-%m-%d')))
    operacion_inv_activa['titulos_t'].append(datos_activa.loc[peso_max, 'Titulos'])
    operacion_inv_activa['titulos_c'].append(datos_activa.loc[peso_max, 'Titulos'])
    operacion_inv_activa['precio'].append(datos_activa.loc[peso_max, 'Precio'])
    operacion_inv_activa['comision'].append(datos_activa.loc[peso_max, 'Comision'])
    operacion_inv_activa['cash'].append(cash)

    for a in range(1, len(data_close)):
        #precio nuevo
        datos_activa['Precio'] = np.round(np.array([data_close.iloc[a, data_close.columns.to_list().index(i)] for i in datos_activa['Ticker']]), 2)
        datos_activa['Comision'] = 0
        datos_activa.loc[peso_max, 'Precio_open'] = np.round(np.array(data_open.iloc[a, data_open.columns.to_list().index(datos_activa.loc[peso_max, 'Ticker'])]), 2)
        differencia = (datos_activa.loc[peso_max, 'Precio'] / datos_activa.loc[peso_max, 'Precio_open']) - 1
        comprados = datos_activa.loc[peso_max, 'Titulos']

        if differencia <= -x_p:
            if a < len(data_close)-1:
                datos_activa.loc[peso_max, 'Precio_c'] = np.round(np.array(data_open.iloc[a + 1, data_open.columns.to_list().index(datos_activa.loc[peso_max, 'Ticker'])]), 2)
            if (cash * kc - cash * kc * c) // datos_activa.loc[peso_max, 'Precio_c'] > 0:
                # suma del 10% y le qutas las comisiones
                # nuevo capital
                datos_activa.loc[peso_max, 'Capital'] = datos_activa.loc[peso_max, 'Capital'] + (cash * kc - cash * kc * c)
                #titulos que ya tenias
                titulos = datos_activa.loc[peso_max, 'Titulos']
                #titulos comprados con el cash disponible
                comprados = ((cash * kc) - (cash * kc * c)) // datos_activa.loc[peso_max, 'Precio_c']

                #el parametro nos dice que se gasta el 10%
                cash = cash - (cash * kc - cash * kc * c)
                n_titulos = comprados + titulos

                #actualizacion de los titulos
                datos_activa.loc[peso_max, 'Titulos'] = n_titulos

                #comision de los titulos comprados
                datos_activa.loc[peso_max, 'Comision'] = np.round(datos_activa.loc[peso_max, 'Precio_c'] * comprados * c, 2)

                operacion_inv_activa['timestamp'].append(str(data_close.index[a].strftime('%Y-%m-%d')))
                operacion_inv_activa['titulos_t'].append(n_titulos)
                operacion_inv_activa['titulos_c'].append(comprados)
                operacion_inv_activa['precio'].append(datos_activa.loc[peso_max, 'Precio_c'])
                operacion_inv_activa['comision'].append(datos_activa.loc[peso_max, 'Comision'])
                operacion_inv_activa['cash'].append(cash)

                postura = [a * b - c for a, b, c in zip(operacion_inv_activa['titulos_c'], operacion_inv_activa['precio'], operacion_inv_activa['comision'])]

                datos_activa.loc[peso_max, 'Postura'] = np.sum(postura)
            for i in range(len(datos_activa['Ticker'])):
                if i == peso_max:
                    pass
                else:
                    datos_activa['Postura'] = np.round(datos_activa['Titulos'] * datos_activa['Precio'], 2)
        datos_activa['Precio_ant'] = datos_activa['Precio']
        datos_activa['Postura'] = np.round(datos_activa['Titulos'] * datos_activa['Precio'], 2)
        inversion_activa['capital'].append(np.round(sum(datos_activa['Postura']) + cash, 2))
        comisiones.append(sum(datos_activa['Comision']))
        inversion_activa['timestamp'].append(str(data_close.index[a].strftime('%Y-%m-%d')))
    return operacion_inv_activa,inversion_activa

def movimientos_activa(operacion_inv_activa):
    mov_activa = pd.DataFrame()
    mov_activa['timestamp'] = operacion_inv_activa['timestamp']
    mov_activa['titulos_t'] = operacion_inv_activa['titulos_t']
    mov_activa['titulos_c'] = operacion_inv_activa['titulos_c']
    mov_activa['precio'] = operacion_inv_activa['precio']
    mov_activa['comision'] = operacion_inv_activa['comision']
    mov_activa['cash'] = operacion_inv_activa['cash']
    return mov_activa

def cap_activa(inversion_activa):
    df_activa = pd.DataFrame()
    df_activa['timestamp'] = inversion_activa['timestamp']
    df_activa['capital'] = np.round(inversion_activa['capital'], 2)
    df_activa['rend'] = 0
    df_activa['rend_acum'] = 0
    for i in range(1, len(df_activa)):
        df_activa.loc[i, 'rend'] = np.round((df_activa.loc[i, 'capital'] / df_activa.loc[i - 1, 'capital'])-1, 4)
        df_activa.loc[i, 'rend_acum'] = np.round(df_activa.loc[i - 1, 'rend_acum'] + df_activa.loc[i, 'rend'], 4)
    return df_activa

rf = 0.0429

def medidas_desempeño(rf,df_pasiva,df_activa):
    df_medidas = pd.DataFrame()
    df_medidas['medida'] = ['rend_mensual', 'rend_acumulado', 'sharpe']
    df_medidas['descripcion'] = ['Rendimiento Promedio Mensual', ' Rendimiento mensual Acumulado', 'Ratio de Sharpe']
    df_medidas.loc[0, 'inversion_pasiva'] = np.round(np.average(df_pasiva['rendimiento']),4)
    df_medidas.loc[1, 'inversion_pasiva'] = df_pasiva.loc[len(df_pasiva) - 1, 'rend_acum']
    df_medidas.loc[2, 'inversion_pasiva'] = np.round((np.average(df_pasiva['rendimiento']) - (rf / 12)) / np.std(df_pasiva['rendimiento']), 4)
    df_medidas.loc[0, 'inversion_activa'] = np.round(np.average(df_activa['rend']), 4)
    df_medidas.loc[1, 'inversion_activa'] = df_activa.loc[len(df_activa) - 1, 'rend_acum']
    df_medidas.loc[2, 'inversion_activa'] = np.round((np.average(df_activa['rend']) - (rf / 12)) / np.std(df_activa['rend']), 4)
    return df_medidas

def comp_inv(df_pasiva, df_activa):
    compa = pd.DataFrame()
    compa["timestamp pasiva"] = df_pasiva['timestamp']
    compa["Inversión Pasiva"] = df_pasiva['capital']
    compa["timestamp activa"] = df_activa['timestamp']
    compa["Inversión Activa"] = df_activa['capital']
    return compa



