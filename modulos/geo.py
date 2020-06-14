from geopy.geocoders import Nominatim

KEY = '9oBA5sB4KHNxyyH7Usxz'

"""
tipos validos [administrative, city]
datos = [
    {
        'display_name': Nombre general de la ubicacion,
        'lat': latitud,
        'lon': longitud,
        'type': tipo de area,
        'geojson': geojson del area,
    }
]
"""
def find_geolo(name):

    geo = Nominatim(user_agent="DaeGas")
    geodata_result = []

    geodata_result = geo.geocode(
        query=name,
        exactly_one=False,
        addressdetails=True,
        geometry='geojson',
        timeout=1000
    )
    clear_list = []

    #print(geodata_result.raw)

    if geodata_result != None:
        for f in geodata_result:
            if f.raw['type'] == 'administrative' or f.raw['type'] == 'city':
                if f.raw['geojson']['type'] == "Polygon":
                    clear_list.append({
                        "display_name": f.raw['display_name'],
                        "lat": f.raw['lat'],
                        "lon": f.raw['lon'],
                        "type": f.raw['type'],
                        "geojson": f.raw['geojson']
                    })

    return clear_list


if __name__ == '__main__':
    find_geolo('San luis potosi')