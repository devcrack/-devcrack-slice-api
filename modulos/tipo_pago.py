# Selecciona el Tipo de Pago  y devuelve una respuesta de sugerenccia 
# data: Datos del Cliente
# tipos_pago: lista tipos de pago del Proveedor
# TIPO_PAGO: tipos de pago del Proveedor
# CANTIDAD_PESOS: Cantidad M  nima de Venta en Efectivo del Proveedor
# CANTIDAD_VOLUMEN: Cantidad M  nima de Venta en Volumen del Proveedor
# PRECIO_LITRO: Precio por litro de gas del Proveedor
# respuesta: Diccionario con las sugerencias del Proveedor(paymentType, cost, gasPrice, minimumPayment, minimumVolume), 
# bandeeras (T_ideal, C_ideal) para verificar si todos los datos ingresados por el cliente hacen MATCH
def selecciona_tipo_pago(data, tipos_pago, TIPO_PAGO, CANTIDAD_PESOS, CANTIDAD_VOLUMEN, PRECIO_LITRO, respuesta):
    aux_litros_all = 0
    # Verifica el Tipo de Pago Seleccionado del Cliente
    if((str(data['paymentType']) in tipos_pago)):
        # print('Si se puede ralizar la venta por esta forma de pago')
        respuesta['paymentType'] = data['paymentType']
        respuesta['T_ideal'] = True
    else:
        # print('No se puede ralizar la venta por esta forma de pago, Sugerimos las Formas de pago del Proveedor')
        respuesta['paymentType'] = TIPO_PAGO
        respuesta['T_ideal'] = False

    # Verificar el Tipo de Venta (Efectivo o Volumen)
    if(data['volume'] == None): # Venta es por Efectivo
        if(data['cost'] < CANTIDAD_PESOS):
            aux_litros_all = float(CANTIDAD_PESOS) / PRECIO_LITRO
            respuesta['cost'] = CANTIDAD_PESOS
            respuesta['C_ideal'] = False
            respuesta['gasPrice'] = float("{0:.2f}".format(aux_litros_all * PRECIO_LITRO))  #Tomar solamente el dato
        else:
            aux_litros_all = float(data['cost']) / PRECIO_LITRO
            respuesta['cost'] = data['cost']
            respuesta['C_ideal'] = True
            respuesta['gasPrice'] = float("{0:.2f}".format(aux_litros_all * PRECIO_LITRO))   #Tomar solamente el dato
        respuesta['minimumPayment'] = CANTIDAD_PESOS
        respuesta['minimumVolume'] = None
    else: # Compra es por Volumen
        if(data['volume'] < CANTIDAD_VOLUMEN):
            respuesta['volume'] = CANTIDAD_VOLUMEN
            respuesta['C_ideal'] = False
            respuesta['gasPrice'] = float("{0:.2f}".format(CANTIDAD_VOLUMEN * PRECIO_LITRO)) #Multiplicar
        else:
            respuesta['volume'] = data['volume']
            respuesta['C_ideal'] = True
            respuesta['gasPrice'] = float("{0:.2f}".format(data['volume'] * PRECIO_LITRO)) #Multiplicar
        respuesta['minimumPayment'] = None
        respuesta['minimumVolume'] = int(CANTIDAD_VOLUMEN)