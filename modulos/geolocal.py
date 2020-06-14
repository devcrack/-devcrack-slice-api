from geopandas.geoseries import *
import geopandas as gp
from shapely.geometry import Polygon
import pathlib
import json
import os



def test_2():
    '''
    Generamos coordenadas para un par de usuarios.
    '''
    p0 = Point(1900.892177224159,22.15679872606256) #
    p1 = Point(-1901.011219024658,22.15012616280903)

    '''
    Cargamos el GeoDataFrame desde un archivo el cual contiene varias areas
    Ref: http://geopandas.readthedocs.io/en/latest/reference/geopandas.read_file.html
    '''
    gas_chingon = gp.read_file('map.geojson')

    '''
    Importante notar que cualquier atributo y metodo de GeoSeries funcionara efectimante para GeoDataFrame
    '''
    print(gas_chingon.intersects(p0))
    print(gas_chingon.intersects(p1))

    '''
    Graficando GeoDataFrame
    '''
    # gas_chingon.plot()
    # plt.show()

    
def match_user_wth_supplier(lat, lon):
    coordenate_point_user = Point(lat, lon)

    cwd = os.getcwd()
    cwd += '/static/geo_data'              # Ruta donde se encuentran los gejson
    current_directory = pathlib.Path(cwd)  # Iniciamos lectura de archivos *.gejson
    proveedores_validos = []

    for files_in_directory in current_directory.iterdir():
        with open(str(files_in_directory)) as f:                            # Cargamos geodatos de proveedor
            nom , ext = os.path.splitext(files_in_directory.name)           # Obtenemos id de proveedor
            data = json.load(f)
            for feature in data['features']:                                # Inicia lectura de poligonos de proveedor
                polygon = Polygon(feature['geometry']['coordinates'][0]) 
                if coordenate_point_user.within(polygon) == True :         #  Determimos si el usuario esta dentro del area de servicio(dentro del poligo, que delimita dicha area)
                   proveedores_validos.append(nom)                        #   Cargamos ID
                   break
    return proveedores_validos


def get_geodata_sup(id):
    cwd = os.getcwd()
    cwd += '/static/geo_data'
    current_directory = pathlib.Path(cwd)

    data = ""
    cwd = cwd + "/" + str(id) + ".geojson"
    with open(cwd) as f:                            # Cargamos geodatos de proveedor
        data = json.load(f)

    return data

# if __name__ == "__main__":
#     p0 = Point(1900.892177224159,22.15679872606256) #
#     p1 = Point(-1901.011219024658,22.15012616280903)
#
#     user_2 = Point(-100.95130920410156,22.16014234128522)
#     user_3 = Point(-100.95047771930695,22.119245913972147)  # Valido solo para edison effect Gas
#     user_4 = Point( -100.89757919311523,22.149569687545846) # Este punto NO hace match con ningun proveedor
#     user_5 = Point( -100.89875936508179,22.149383367211627) # Este punto hace match con el proveedor #1
#     user_6 = Point( -100.94444274902344,22.211563385273656) # Este punto hace match con el proveedor #1
#     user_7 = Point(-101.02980136871338,22.188080529287323)  # Match proveedor #1
#     user_8 = Point(-101.03978723287582,22.126647951738402)  # Este punto no hace match
#
#     match = match_user_wth_supplier(user_8)
#     if match:
#         print(match)
#     else :
#         print('No hay match para este usuario')


if __name__ == "__main__":
    get_geodata_sup(1)