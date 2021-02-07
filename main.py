
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import data as D
import functions as F
from os import path
import visualizations as V



#Paso 0: Dar la ruta de los archivos
abspath = path.abspath('NAFTRAC_holdings/')

#Paso 1: lista de los archivos
lis_archivos = D.ruta_arch(abspath)

#Paso 2: Crear un diccionario de los archivos
diccionario = D.diccionario_datos(lis_archivos)

#Paso 3: Armado del vector de fechas usando el vector de nombres de los archivos
fechas_archivos = F.ti_fechas(lis_archivos)

#Paso 4: lista de activos que sean compatibles con Yfinance
tickers_compatibles = F.todos_tickers(lis_archivos)

#Paso 5: Conseguir los precios de cierre
p_cierre = F.yfin_close(tickers_compatibles, fechas_archivos[1])

#Paso 6: Conseguir los precios de apertura
p_apertura = F.yfin_open(tickers_compatibles, fechas_archivos[1])

#Paso 7: Comienza el proceso para la inversion pasiva
# posicion inicial
k = 1000000
# comision por transaccion
c = 0.00125
# vector de comisiones historicas
comisiones = []

df__pasiva = F.inversion_pasiva(diccionario, lis_archivos, p_cierre[2], fechas_archivos[0], p_cierre[1], k, c)

#Paso 8: Comienza el proceso para la inversion activa
x_p = 0.01
kc = 0.1
# Localiza el ticker de mayor precio y le aplica la serie de requisitos de la inversion activa
inv_act = F.inversion_activa(diccionario, lis_archivos, p_cierre[0], p_apertura[0], c, x_p, kc, k)
# Se muestra el rebalanceo que hizo la inversion activa
mov_inversion_activa = F.movimientos_activa(inv_act[0])
# Los rendimientos de la inversion activa
df__activa = F.cap_activa(inv_act[1])

#Paso 9: Medidas de desempeño
rf = 0.0429
desempeño = F.medidas_desempeño(rf, df__pasiva, df__activa)

#Paso 10:Comparativo de las inversiones
comparacion = F.comp_inv(df__pasiva, df__activa)

#Paso 11: Comparativo de las inversiones en una gráfica
#Gráfica de la inversion pasiva
p_graf = V.grafica(x=df__pasiva['timestamp'],y=df__pasiva['capital'],titulo="Capital pasivo",xtitulo='Fechas',ytitulo="Capital")
#Gráfica de la inversion activa
a_graf = V.grafica(x=df__activa['timestamp'],y=df__activa['capital'],titulo="Capital activa",xtitulo='Fechas',ytitulo="Capital")



