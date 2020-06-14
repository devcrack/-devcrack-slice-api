import datetime

H_BEGIN = 0 # Hora Mínimo Inferior
H_END = 24  # Hora Máximo Superior

# Funcion que determina el Rango de Horario de Cliente
# Hi: Horario Inicial que seleccionó el Cliente
# Hf: Horario Final que seleccionó el Cliente
# H_I: Horario Inicial del Proveedor
# H_F: Horario Final del Proveedor
# respuesta: Dicciojnario con las sugerencias del Proveedor(Hi, Hf), bandera
# H_ideal, para verificar si todos los datos ingresados por el cliente hacen MATCH
def seleccciona_horario(Hi, Hf, H_I, H_F, respuesta):
    if((Hi >= H_BEGIN and Hi <= H_I) and (Hf >= H_BEGIN and Hf <= H_I)):
        respuesta['Hi'] = H_I
        respuesta['Hf'] = H_F
        respuesta['H_ideal'] = False
    # Caso Ideal 
    if((Hi >= H_I and Hi <= H_F) and (Hf >= H_I and Hf <= H_F)):
        respuesta['Hi'] = Hi
        respuesta['Hf'] = Hf
        respuesta['H_ideal'] = True

    if((Hi >= H_F and Hi <= H_END) and (Hf >= H_F and Hf <= H_END)):
        respuesta['Hi'] = H_I
        respuesta['Hf'] = H_F
        respuesta['H_ideal'] = False

    if(Hi < H_I and Hf > H_I):
        respuesta['Hi'] = H_I
        respuesta['Hf'] = Hf
        respuesta['H_ideal'] = False

    if(Hi < H_F and Hf > H_F):
        respuesta['Hi'] = Hi
        respuesta['Hf'] = H_F
        respuesta['H_ideal'] = False

# Función que convierte el Rango de Hora Seleccionado por el Cliente
# retorna las Horas (Inicial y Final)
def convertir_rango_horas_a_horas(rango):
    Hi = int(rango[0:2])
    Hf = int(rango[9:11])
    return Hi, Hf

#Función que convierte las Horas (Inicial y Final) en un rango en formato(HH:MM:SS-HH-MM-SS)
def convierte_horas_a_rango(Hi, Hf):
    return str(datetime.timedelta(hours=Hi)) + '-' + str(datetime.timedelta(hours=Hf))