from flask import Flask, render_template, session, redirect, url_for, request, make_response
from flask_material import Material  
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, number_range
from flaskext.mysql import MySQL
from flask import jsonify
import config
import json

# Imports local modules
from modulos.geo import find_geolo
from modulos.geolocal import match_user_wth_supplier, get_geodata_sup
from modulos.toma_desicion import desicion

app = Flask(__name__)
mysql = MySQL()

# Secret key configuration
app.secret_key = config.SECRET_KEY

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = config.MYSQL_DATABASE_USER
app.config['MYSQL_DATABASE_PASSWORD'] = config.MYSQL_DATABASE_PASSWORD
app.config['MYSQL_DATABASE_DB'] = config.MYSQL_DATABASE_DB
app.config['MYSQL_DATABASE_HOST'] = config.MYSQL_DATABASE_HOST
app.config['MYSQL_DATABASE_PORT'] = config.MYSQL_DATABASE_PORT

# Init configurations
mysql.init_app(app)
Material(app)

#This classes define a model form
class LoginForm(FlaskForm):
    idsupplier = IntegerField('KEY', validators=[InputRequired()])
    rfcsupplier = StringField('RFC', validators=[InputRequired(), Length(min=0, max=13)])


class DataForm(FlaskForm):
    c_minVol = IntegerField('Volumen minimo de venta(litros)', validators=[InputRequired()])
    c_minEfectivo = FloatField('Precio minimo de venta', validators=[InputRequired()])
    h_inicio = IntegerField('Hora de inicio de servicio (24h)', validators=[InputRequired(), number_range(min=0, max=23)])
    h_fin = IntegerField('Hora de cierre de servicio (24h)', validators=[InputRequired(), number_range(min=0, max=23)])


# Definicion del api final
@app.route('/api/v0' , methods=['POST'])
def api():
    data = None
    try:
        try:
            data = request.json
        except:
            raise ValueError

        if data is None:
            raise ValueError

        try:
            if data:
                print(data)
        except:
            raise KeyError

        # Estructura del json de entrada
        # {
        #    "idUsuario: id" Nuevo
        #    "idApp": 2,
        #    "idSupplier": 1,
        #    "volume": 45,
        #    "cost": null,
        #    "addressHash": "527abfc0692a00338782",
        #    "date": "2018-06-26",
        #    "hourRange": "10:00:00-14:00:00",
        #    "paymentType": 2
        # }

        #Sea realiza consulta para obtener coordenadas.
        lista_sup = []
        try:
            cursor = mysql.get_db().cursor()
            q_string = 'SELECT longitude, latitude FROM `Address` WHERE addressHash = \'{}\''
            q_string = q_string.format(data['addressHash'])
            cursor.execute(q_string)
            res = cursor.fetchone()
            if res:
                #longitu
                lat = float(res[0])
                # latitud
                lon = float(res[1])
                lista_sup = match_user_wth_supplier(lat, lon)
        except:
            raise ValueError
        print(lista_sup)
        #geolocalizacion
        #Realiza consulta para obtener latitud y longitud
        lista_final = desicion(mysql, lista_sup, data)


    except ValueError:
        print('Error 1: Error con los datos recibidos (bad request)')
        return make_response('bad request', 400)

    except KeyError:
        print('Error2: Error con lso datos del json')
        return make_response('data error', 409)

    return make_response(json.dumps(lista_final), 200)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if 'id' in session:
#         return redirect(url_for('index'))
#
#     form = LoginForm()
#     if form.validate_on_submit():
#         cursor = mysql.get_db().cursor()
#         q_string = 'SELECT * FROM `Supplier` WHERE idSupplier = {} AND rfc = \'{}\''
#         cursor.execute(q_string.format(form.idsupplier.data, form.rfcsupplier.data))
#         data = cursor.fetchone()
#         if data:
#             session['id'] = data[0]
#             session['name'] = data[3]
#             return redirect(url_for('index'))
#
#         return render_template('login.html', form=form, message='Datos incorrectos')
#     return render_template('login.html', form=form)


@app.route('/login', methods=['GET'])
def login():

    id_sup = request.args.get('id')
    id_driver = request.args.get('drv')

    if id_driver and id_sup:
        cursor = mysql.get_db().cursor()
        q_string = 'SELECT * FROM `Driver` WHERE idDriver = {}'
        cursor.execute(q_string.format(id_driver))
        data_0 = cursor.fetchone()
        if data_0:
            cursor = mysql.get_db().cursor()
            q_string = 'SELECT * FROM `Supplier` WHERE idSupplier = {}'
            cursor.execute(q_string.format(id_sup))
            data_1 = cursor.fetchone()
            if data_1:
                session['id'] = data_1[0]
                session['id_drv'] = data_0[0]
                session['name'] = data_1[3]
                session['name_drv'] = data_0[5]
                return redirect(url_for('index'))
        return redirect("https://www.levelgas.com/interface/login.php")
    return redirect("https://www.levelgas.com/interface/login.php")


@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('name', None)
    session.pop('id_dvr', None)
    session.pop('name_dvr', None)
    return redirect("https://www.levelgas.com/interface/login.php")


@app.route('/')
def index():
    if 'id' in session:
        return render_template('index.html')
    else:
        return redirect("https://www.levelgas.com/interface/login.php")


@app.route('/supdata' , methods=['GET', 'POST'])
def supdata():
    if 'id' in session:
        form = DataForm()
        if request.method == 'GET':
            # Mostrar datos del Proveedor de la Base de Datos si es que los tiene         
            cursor = mysql.get_db().cursor()
            q_string = 'SELECT minimumVolume, minimumPrice, initialHour, finalHour '
            q_string = q_string + 'FROM `Supplier`'
            q_string = q_string + 'WHERE idSupplier = {}'
            q_string = q_string.format(session['id'])
            cursor.execute(q_string)
            print('Consulta para visualizar los datos')
            data = cursor.fetchone()
            if data:           
                form.c_minVol.data = int(data[0])
                form.c_minEfectivo.data = data[1]
                form.h_inicio.data = data[2]
                form.h_fin.data = data[3]
                return render_template('supdata.html', form=form, data=data, name=session['name'], dvr_name=session['name_drv'])

        if form.validate_on_submit():
            cursor = mysql.get_db().cursor()
            q_string = 'UPDATE `Supplier`'
            q_string = q_string + ' SET initialHour={}, finalHour={}, minimumPrice={}, minimumVolume={}'
            q_string = q_string + ' WHERE idSupplier = {}'
            q_string = q_string.format(form.h_inicio.data, form.h_fin.data, form.c_minEfectivo.data, form.c_minVol.data,
                                       session['id'])
            cursor.execute(q_string)
            mysql.get_db().commit()
            print(q_string)
            return render_template('supdata.html', form=form, name=session['name'], message='Datos guardados.', dvr_name=session['name_drv'])
        return render_template('supdata.html', form=form, name=session['name'], message='', dvr_name=session['name_drv'])
    else:
        return redirect("https://www.levelgas.com/interface/login.php")

#busqueda del nombre en el mapa
@app.route('/geo_search', methods = ['GET'])
def geo_search():
    if 'id' in session:
        res_data = {}
        data = request.args.get('data')

        if data:
            res = find_geolo(data)
            if res:
                js = json.dumps(res, ensure_ascii=False)
                jsonRes = jsonify({'status':1, 'datos': js})
                return jsonRes
            else:
                print("nada")
                return jsonify({'status':-1, 'datos': None})
        return render_template('geodata.html', name=session['name'], dvr_name=session['name_drv'])
    else:
        return redirect("https://www.levelgas.com/interface/login.php")


'''
Guarda las coordenadas recibididas desde la herramienta fronted
'''
@app.route('/save_coordinates', methods=['POST'])
def save_points():
    if 'id' in session:
        data = request.json
        path = './static/geo_data/{}.geojson'.format(session['id_drv'])
        with open(path, 'w') as fp:
            json.dump(data, fp)
        res = {'response': 'sucess'}
    else:
        res = {'response': 'error'}
    return jsonify(res)


@app.route('/get_geodata', methods=['GET'])
def get_geodata():
    if 'id_drv' in session:
        id = int(session['id_drv'])
        geo_data = get_geodata_sup(id)

        return jsonify(geo_data)
    else:
        return jsonify({})


if __name__ == '__main__':
    app.debug = config.DEBUG_MODE
    app.run(host = config.IP_VALUE, port=config.PORT_VALUE)
