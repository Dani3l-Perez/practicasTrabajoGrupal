from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

app.secret_key = '0123456789'

miConexion = MongoClient("mongodb://localhost:27017/")

app.config["UPLOAD_FOLDER"] = "./static/image/"

baseDatos = miConexion["P-SENA"]
usuarios = baseDatos["usuarios"]
personas = baseDatos["personas"]

if __name__ == "__main__":
    from routes.route import *
    app.run(port=5000, debug=True)

