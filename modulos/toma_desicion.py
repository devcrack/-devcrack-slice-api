import json
from .horario import seleccciona_horario, convertir_rango_horas_a_horas, convierte_horas_a_rango
from .tipo_pago import selecciona_tipo_pago
import datetime

def hay_elementos_cumple_todos_requerimientos(dict_list):
    for registro in dict_list:
        if registro['fulfillRequirements'] == 1:
            return True
    return False

def num_registros_cumple_todos_requerimientos(dict_list):
    count = 0

    for registro in dict_list:
        if registro['fulfillRequirements'] == 1:
            count += 1
    return count


def desicion(mysql, prov, data):
    # Respuesta de Salida (JSON_OUT)
    json_salida = {}
    json_salida['proveedores'] = []

    # # Datos para la Conexion a la Base de Datos
    # conecction = MySQLdb.connect(host="db4free.net",    # your host, usually localhost
    #                     user="ifisica",      # your username
    #                     passwd="mientras123",   # your password
    #                     db='daelabs')       # name of the data base


    # Toma de Desiciones
    # # Recibe una lista con los Id's Suppliers
    ids_proveedores = prov
    band_toma_desicion = False

    if data['idApp'] == 1: #Si la Aplicación es de LevelGas
        if data['idSupplier'] == 2: # Si el idSupplier es de LevelGas
            # Toma de Desiciones
            print('Hace la Toma de Desision')
            band_toma_desicion = True
            for id_proveedor in ids_proveedores:
                ID = id_proveedor
                # Regresa los datos como una tupla de "Diccionarios", por lo que podremos
                # acceder a cada uno de los resultados usando el nombre de la columna en
                # vez de un numero de indice
                cur = mysql.get_db().cursor()
                #Consulta de la base de datos
                query = "SELECT * FROM Driver WHERE idDriver = " + str(ID) + " AND idStatus=1 OR idStatus = 2"
                # Ejecutar la Consulta sobre la Base de Datos
                cur.execute(query)
                datos_driver = cur.fetchall() 
                if len(datos_driver) != 0:                     
                    idSup = str(datos_driver[0][1])
                    print(idSup)
                    query2 = "SELECT * FROM Supplier WHERE idSupplier = " + idSup + " AND idStatus = 1"
                    # print("Consulta")
                    # print(query2)
                    # Ejecutar la Consulta sobre la Base de Datos
                    cur.execute(query2)

                    datos_supplier = cur.fetchall()
                    if len(datos_supplier) != 0:
                        for row in datos_supplier:
                            CANTIDAD_PESOS = row[24]   # Precio mínimo de Venta
                            CANTIDAD_VOLUMEN = row[25]# Volumen Mínimo de Venta
                            PRECIO_LITRO = float(row[7])     #Precio por Litro del Gas
                            H_I = row[22]
                            H_F = row[23]
                            TIPO_PAGO = row[8] #Verificar si tiene mas de una Forma de Pago
                            RATE = row[26]
                            COMMISSION = row[27]
                            # Consulta para promedio X Driver
                        print('idDriver = ' +  str(ID))
                        query3 = 'SELECT * FROM Driver2User WHERE idDriver =' + str(ID) + ' ORDER BY ranking DESC'
                        #print("Promedio")
                        #print(query3)
                        # Ejecutar la Consulta sobre la Base de Datos
                        cur.execute(query3)
                        # print ("iddriver" + str(ID))
                        aux_p = cur.fetchall()
                        print("Choferes por Camion")
                        print(aux_p)
                        if len(aux_p) != 0:
                            best_diver = aux_p[0]                
                            # print("Mejor Chofer")
                            # print(best_diver)
                            # print("-------------------------------------------------------")
                            for row in aux_p:
                                # print(row)
                                if row[2] >= best_diver[2]:
                                    #Verificar fecha
                                    # date1 = datetime.datetime (row[3])
                                    date1 = row[3]
                                    # date2 = datetime.datetime (best_diver[3])
                                    date2 = best_diver[3]
                                    if date1 < date2:
                                        best_diver = row
                                        # RANKING = float(str(cur.fetchall()[0][1]))
                                        # print(RANKING)
                            print("------------------------------------------------------")
                            print ("Mejor Chofer = ")
                            print(best_diver)
                            print("------------------------------------------------------")
                            if CANTIDAD_PESOS != 0 and CANTIDAD_VOLUMEN != 0 and PRECIO_LITRO != 0 and H_I != 0 and H_F != 0 and TIPO_PAGO != 0 and RATE != None and COMMISSION != None:
                                respuesta = {}
                                # Convertir Rango de Hora en formato de Entero
                                # para poder manipularlo
                                Hi, Hf = convertir_rango_horas_a_horas(data['hourRange'])
                                #Verifica el Horario Selecionado del Cliente
                                seleccciona_horario(Hi, Hf, H_I, H_F, respuesta)
                                tipos_pago = TIPO_PAGO.split(',')
                                # print('Tipos de Pago')
                                # print(tipos_pago)

                                # Verifica el Tipo de Pago Seleccionado del Cliente
                                selecciona_tipo_pago(data, tipos_pago, TIPO_PAGO, CANTIDAD_PESOS, CANTIDAD_VOLUMEN, PRECIO_LITRO, respuesta)
                                respuesta['idSupplier'] = int(idSup)
                                respuesta['pricePerLiter'] = PRECIO_LITRO
                                # Convertir numero a Formato HH:MM:SS
                                respuesta['schedule'] = convierte_horas_a_rango (respuesta['Hi'], respuesta['Hf'])
                                # Verificar si cumple con todos los requerimientos
                                if(respuesta['C_ideal'] and respuesta['H_ideal'] and respuesta['T_ideal']):
                                    respuesta['fulfillRequirements'] = 1
                                else:
                                    respuesta['fulfillRequirements'] = 0
                                    # Qutar las claves que no se van a mostrar
                                respuesta.pop('C_ideal')
                                respuesta.pop('T_ideal')
                                respuesta.pop('H_ideal')
                                respuesta.pop('Hi')
                                respuesta.pop('Hf')
                                respuesta.pop('pricePerLiter')
                                if(data['cost'] == None): # Venta es por Efectivo
                                    respuesta.pop('volume')
                                else:
                                    respuesta.pop('cost')
                                respuesta['rate'] = RATE
                                respuesta['commission'] = COMMISSION
                                respuesta['idUser'] = best_diver[0]
                                respuesta['idDriver'] = best_diver[1]
                                json_salida['proveedores'].append(respuesta)
                            else:
                                print('Error: Campos Vacíos, se omite el proveedor')
                    else:
                        print("El Supplier esta INACTIVO")
                else:
                    print("El Driver NO EXISTE")
        else:
            # Generar Pedido con idSupplier
            if str(data['idSupplier']) in ids_proveedores:
                print('Generar Pedido con idSupplier')
                cur = mysql.get_db().cursor()
                #Consulta de la base de datos
                query = "SELECT * FROM Driver WHERE idDriver= " + str(data['idSupplier'])
                # Ejecutar la Consulta sobre la Base de Datos
                cur.execute(query)

                query2 = "SELECT * FROM Supplier WHERE idSupplier = " + str(cur.fetchall()[0][1])
                # print("Consulta Pedido idSupplier")
                # print(query2)
                # Ejecutar la Consulta sobre la Base de Datos
                cur.execute(query2)

                for row in cur.fetchall():
                    CANTIDAD_PESOS = row[24]   # Precio mínimo de Venta
                    CANTIDAD_VOLUMEN = row[25]# Volumen Mínimo de Venta
                    PRECIO_LITRO = float(row[7])     #Precio por Litro del Gas
                    H_I = row[22]
                    H_F = row[23]
                    TIPO_PAGO = row[8] #Verificar si tiene mas de una Forma de Pago

                    if CANTIDAD_PESOS != 0 and CANTIDAD_VOLUMEN != 0 and PRECIO_LITRO != 0 and H_I != 0 and H_F != 0 and TIPO_PAGO != 0:
                        respuesta = {}
                        # Convertir Rango de Hora en formato de Entero
                        # para poder manipularlo
                        Hi, Hf = convertir_rango_horas_a_horas(data['hourRange'])
                        #Verifica el Horario Selecionado del Cliente
                        seleccciona_horario(Hi, Hf, H_I, H_F, respuesta)
                        tipos_pago = TIPO_PAGO.split(',')
                        # print('Tipos de Pago')
                        # print(tipos_pago)

                        # Verifica el Tipo de Pago Seleccionado del Cliente
                        selecciona_tipo_pago(data, tipos_pago, TIPO_PAGO, CANTIDAD_PESOS, CANTIDAD_VOLUMEN, PRECIO_LITRO, respuesta)
                        respuesta['idSupplier'] = int(data['idSupplier'])
                        respuesta['pricePerLiter'] = PRECIO_LITRO
                        # Convertir numero a Formato HH:MM:SS
                        respuesta['schedule'] = convierte_horas_a_rango (respuesta['Hi'], respuesta['Hf'])
                        # Verificar si cumple con todos los requerimientos
                        if respuesta['C_ideal'] and respuesta['H_ideal'] and respuesta['T_ideal']:
                            respuesta['fulfillRequirements'] = 1
                        else:
                            respuesta['fulfillRequirements'] = 0
                            # Qutar las claves que no se van a mostrar
                        respuesta.pop('C_ideal')
                        respuesta.pop('T_ideal')
                        respuesta.pop('H_ideal')
                        respuesta.pop('Hi')
                        respuesta.pop('Hf')
                        respuesta.pop('pricePerLiter')
                        if data['cost'] == None: # Venta es por Efectivo
                            respuesta.pop('volume')
                        else:
                            respuesta.pop('cost')
                            json_salida['proveedores'].append(respuesta)
                    else:
                        print('Error: Campos Vacíos, se omite el proveedor')
    else:
        # Generar Pedido con Proveedor
        # print('Datoooooooooooooo')
        # print(ids_proveedores)
        if str(data['idApp']) in ids_proveedores:
            print('Generar Pedido con idApp')
            cur = mysql.get_db().cursor()
            #Consulta de la base de datos
            query = "SELECT * FROM Driver WHERE idDriver = " + str(data['idApp'])
            # Ejecutar la Consulta sobre la Base de Datos
            cur.execute(query)

            query2 = "SELECT * FROM Supplier WHERE idSupplier = " + str(cur.fetchall()[0][1])
            #print("Consulta Pedido por Proveedor")
            # print(query2)
            # Ejecutar la Consulta sobre la Base de Datos
            cur.execute(query2)

            for row in cur.fetchall():
                CANTIDAD_PESOS = row[24]   # Precio mínimo de Venta
                CANTIDAD_VOLUMEN = row[25]# Volumen Mínimo de Venta
                PRECIO_LITRO = float(row[7])     #Precio por Litro del Gas
                H_I = row[22]
                H_F = row[23]
                TIPO_PAGO = row[8] #Verificar si tiene mas de una Forma de Pago

                if CANTIDAD_PESOS != 0 and CANTIDAD_VOLUMEN != 0 and PRECIO_LITRO != 0 and H_I != 0 and H_F != 0 and TIPO_PAGO != 0:
                    # Convertir Rango de Hora en formato de Entero
                    # para poder manipularlo
                    Hi, Hf = convertir_rango_horas_a_horas(data['hourRange']) 
                    tipos_pago = TIPO_PAGO.split(',')
                    print('Caso donde la Aplicación NO es de LEVEL_GAS')
                    respuesta = {}
                    seleccciona_horario(Hi, Hf, H_I, H_F, respuesta)
                    selecciona_tipo_pago(data, tipos_pago, TIPO_PAGO, CANTIDAD_PESOS, CANTIDAD_VOLUMEN, PRECIO_LITRO, respuesta)
                    respuesta['idSupplier'] = int(data['idApp'])
                    respuesta['pricePerLiter'] = PRECIO_LITRO
                    # Convertir numero a Formato HH:MM:SS
                    respuesta['schedule'] = convierte_horas_a_rango (respuesta['Hi'], respuesta['Hf'])
                    # Verificar si cumple con todos los requerimientos
                    if respuesta['C_ideal'] and respuesta['H_ideal'] and respuesta['T_ideal']:
                        respuesta['fulfillRequirements'] = 1
                    else:
                        respuesta['fulfillRequirements'] = 0
                        # Quitar las claves que no se van a mostrar
                    respuesta.pop('C_ideal')
                    respuesta.pop('T_ideal')
                    respuesta.pop('H_ideal')
                    respuesta.pop('Hi')
                    respuesta.pop('Hf')
                    respuesta.pop('pricePerLiter')
                    if data['cost'] == None: # Venta es por Efectivo
                        respuesta.pop('volume')
                    else:
                        respuesta.pop('cost')
                        json_salida['proveedores'].append(respuesta)
                else:
                    print('No se puede hacer el Pedido, Campos Incompletos')
    print ('Registros Sin Filtrar')
    print(json_salida['proveedores'])
    if band_toma_desicion == True:
        # Verificar si hay proveedores que cumplen con todos los requerimentos
        if hay_elementos_cumple_todos_requerimientos(json_salida['proveedores']):
            # Verificar si hay mas de un proveedor que  cumpla con todos los requerimientos
            if num_registros_cumple_todos_requerimientos(json_salida['proveedores']) > 1:
                json_salida_nueva = []
                for registro in json_salida['proveedores']:
                    if registro['fulfillRequirements']:
                        json_salida_nueva.append(registro)
                        json_salida_ordenado = sorted(json_salida_nueva, reverse=True, key=lambda x:  (x['rate'], x['commission']))
            else:
                json_salida_ordenado = sorted(json_salida['proveedores'], reverse=True, key=lambda x:  x['fulfillRequirements'])
        else:
            json_salida_ordenado = sorted(json_salida['proveedores'], reverse=True, key=lambda x:  (x['rate'], x['commission']))
    else:
        json_salida_ordenado = json_salida['proveedores']

    print('Número de Elementos en la Listaaaa = ', len(json_salida_ordenado))
    if len(json_salida_ordenado) > 1:
        i = len(json_salida_ordenado) - 1
        while len(json_salida_ordenado) > 1:
            json_salida_ordenado.pop(i)
            i = i - 1
            print('N  mero de Elementos en la Listaaaa = ', len(json_salida_ordenado))

    if len(json_salida_ordenado) == 1 and band_toma_desicion == True:
        # Eliminar llaves que nos sirvieron para elegir solamente un proveedor
        json_salida_ordenado[0].pop('rate')
        json_salida_ordenado[0].pop('commission')

    return json_salida_ordenado
#
# # Guarda en un archivo las sugerencia de los Proveedores
# with open('datos_out.json', 'w') as file:
#     json.dump(json_salida_ordenado, file)
#     file.close()
#
# print ("Datos leídos desde el Archivo")
# with open('datos_out.json', 'r') as file:
#     data = json.load(file)
#     print('Datos del Archivo')
#     print(data)
#     file.close()
#
# # print(json_salida)
# conecction.close()
