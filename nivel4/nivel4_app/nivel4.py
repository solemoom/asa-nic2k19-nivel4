from flask import Flask, jsonify, request, Response
import json
import mysql.connector
#from flask_cors import CORS, cross_origin
import redis
import pickle
import hashlib
import requests

app = Flask(__name__)

R_SERVER = redis.Redis(host='redis',port=6379)

def Connection():
    return mysql.connector.connect(user='root', host='nivel4-db', port='3306', password='toor', database='nivel4-db-mysql')

@app.route('/')
def nivel4():
    return print("Bienvenido al nivel 4")

@app.route('/active', methods=['GET', 'POST', 'PUT'])
def active():
    if request.method == 'GET':
        country = request.args.get("country", default = "no country", type = str)
        city = request.args.get("city", default = "no city", type = str)
        key = country+city
        info = {}
        sql_select = "select city.active, city.city, country.country from city inner join country on country.id = city.id_country where country.country LIKE '%{}%' and city.city LIKE '%{}%'".format(country, city)

        if R_SERVER.get(key):
            info = json.loads(R_SERVER.get(key))
        else:
            try:
                db = Connection()
                cursor = db.cursor()
                cursor.execute(sql_select)
                records = cursor.fetchall()
                if records == None:
                    info = {"Respuesta":"No hay datos o no se pasaron argumentos"}
                else:
                    for row in records:
                        if row[0] == 0:
                            v_active = False
                        else:
                            v_active = True

                        info = {"active":"{}".format(v_active),"country":"{}".format(row[2]),"city":"{}".format(row[1]),"cache":"miss"}
                        info_cache = {"active":"{}".format(v_active),"country":"{}".format(row[2]),"city":"{}".format(row[1]),"cache":"hit"}

                    R_SERVER.set(key,json.dumps(info_cache))
            except Exception as e:
                print("Error en SQL:\n",e)
            finally:
                db.close()

        return jsonify(info)

    if request.method == 'POST':
        req_data = request.get_json()

        country = req_data['country']
        city = req_data['city']
        db = Connection();
        try:
            sql_insert = "INSERT INTO `country` (`country`) VALUES ('{}')".format(country)
            cursor = db.cursor()
            cursor.execute(sql_insert)
            db.commit()

            sql_select = "select id from country where country = '{}'".format(country)
            cursor.execute(sql_select)
            records = cursor.fetchall()
            for row in records:
                id_v = row[0]

            sql_insert_c = "INSERT INTO `city` (`city`, `id_country`, `active`) VALUES ('{}', '{}', '1')".format(city, id_v)
            cursor.execute(sql_insert_c)
            db.commit()

            info = {"Response": "Datos guardados correctamente"}
        except Exception as e:
            print("Error in SQL:\n", e)
        finally:
            db.close()
        return jsonify(info)


    if request.method == 'PUT':
        req_data = request.get_json()

        country = req_data['country']
        city = req_data['city']
        db = Connection();
        try:
            sql_select = "select city.id,city.active from city inner join country on country.id = city.id_country where country.country like '%{}%' and city.city like '%{}%'".format(country, city)

            cursor = db.cursor()
            cursor.execute(sql_select)
            records = cursor.fetchall()
            for row in records:
                city_id = row[0]
                active = row[1]

            if active == 0:
                active_n = 1
                info = {"Response": "Se activo la venta"}
            else:
                active_n = 0
                info = {"Response": "Se desactivo la venta"}

            sql_update = "update city set active = {} where city.id = {}".format(active_n, city_id)
            cursor.execute(sql_update)
            db.commit()
        except Exception as e:
            print("Error in SQL:\n", e)
        finally:
            db.close()
        return jsonify(info)

@app.route('/quote',methods=['POST'])
def quote():
    req_data = request.get_json()
    sku = req_data['sku']
    country = req_data['country']
    city = req_data['city']
    key = sku+country+city
    descripcion = ""
    base_price = 0
    variation = 0
    info = {}

    if R_SERVER.get(key):
        info = json.loads(R_SERVER.get(key))
        return jsonify(info)
    else:
        uri = ("http://api.openweathermap.org/data/2.5/weather?q={},{}&appid=3225ae99d4c4cb46be4a2be004226918".format(city,country))
        try:
            uResponse = requests.get(uri)
        except requests.ConnectionError:
            return "Error en la coneccion de la api openweather"

        Jresponse = uResponse.text
        data = json.loads(Jresponse) 
        id_weather = data['weather'][0]['id']
        
        try:
            sql_select = "select productos.descripcion, productos.precio from productos where sku = '{}'".format(sku)
            db = Connection()
            cursor = db.cursor()
            cursor.execute(sql_select)
            records = cursor.fetchall()
            for row in records:
                descripcion = row[0]
                base_price = row[1]
        except Exception as e:
            print("Error en SQL:\n",e)
        finally:
            db.close()
        
        try:
            sql_select_varia = "select max(variation) from reglas where ciudad = '{}' and pais = '{}' and min_condition <= {} and max_condition >= {} and sku = '{}'".format(city,country,id_weather,sku)
            db = Connection()
            cursor = db.cursor()
            cursor.execute(sql_select_varia)
            records = cursor.fetchall()
            for row in records:
                variation = row[0]
        except Exception as e:
            print("Error en SQL:\n",e)
        finally:
            db.close()

        if variation == 0:
            precio_final = base_price * 1
        else:
            precio_final = base_price * variation

        info = {
            "sku":"{}".format(sku),
            "description":"{}".format(descripcion),
            "country":"{}".format(country),
            "city":"{}".format(city),
            "base_price":"{}".format(base_price),
            "variation":"{}".format(variation),
            "final_price":"{}".format(precio_final),
            "cache":"miss"
        }
        info_cache = {
            "sku":"{}".format(sku),
            "description":"{}".format(descripcion),
            "country":"{}".format(country),
            "city":"{}".format(city),
            "base_price":"{}".format(base_price),
            "variation":"{}".format(variation),
            "final_price":"{}".format(precio_final),
            "cache":"hit"
        }

        R_SERVER.set(key,json.dumps(info_cache))
        return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8000')
