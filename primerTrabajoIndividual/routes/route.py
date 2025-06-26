from bson import ObjectId
from flask import request, render_template, jsonify, redirect, session
import pymongo
import pymongo.errors
from app import app, usuarios, personas
from werkzeug.utils import secure_filename
import os
from enum import Enum
import json

#Petición RUTA RAIZ: Landing Pages.
@app.route("/")
def home():
    return render_template("index.html")

#creamos los roles para el inicio de sesión por rol.
class Rol(Enum):
    admin = "admin"
    instructor = "instructor"
    funcionarioBienestar = "funcionarioBienestar"

#Petición RUTA iniciarSesion: formulario para inicair sesión.
@app.route("/iniciarSesion/", methods=['GET', 'POST'])
def iniciarSesion():
    # Renderizar formulario de inicio de sesión
    if request.method == 'GET':
        return render_template("formIniciarSesion.html")

    # Procesar datos del formulario
    elif request.method == 'POST':
        correo = request.form.get("txtCorreo")
        contraseña = request.form.get("txtContraseña")
        rol = request.form.get("selectRol")

        # Buscar usuario con correo, contraseña y rol exactos
        usuario_encontrado = usuarios.find_one({
            "correo": correo,
            "contraseña": contraseña,
            "rol": rol
        })

        # Si el usuario existe
        if usuario_encontrado:
            session["correo"] = correo
            session["rol"] = rol

            # Si es admin, va directo al menú
            if rol == Rol.admin.value:
                return render_template("menuAdministrador.html")

            # Para los demás, verificar datos personales
            datos_personales = personas.find_one({"correo": correo})

            if not datos_personales:
                # No tiene datos personales, redirigir al formulario
                return render_template("formRegistrarPersona.html")

            # Ya tiene datos personales, verificar si tiene info del rol
            rol_info = usuario_encontrado.get("rolInfo")

            # Mostrar menú correspondiente según el rol
            if rol == Rol.instructor.value:
                if rol_info:
                    return render_template("menuInstructor.html")
                else:
                    return render_template("formRegistroPorRol.html", rol="instructor")
            elif rol == Rol.funcionarioBienestar.value:
                if rol_info:
                    return render_template("menuFuncionarioBienestar.html")
                else:
                    return render_template("formRegistroPorRol.html", rol="funcionarioBienestar")

        # Si no se encuentra el usuario
        else:
            return render_template("formIniciarSesion.html", mensaje="Credenciales no válidas")


#Petición RUTA registarUsuario: formulario para registrarse.
@app.route("/registrarUsuario/", methods=['GET', 'POST'])
def registrarUsuario():
    #si el metodo a usar es get renderiza el archivo HTML del formulario 
    #para que el usuario pueda rgistrarse.
    if request.method == 'GET':
        return render_template("formRegistrarUsuario.html")
    #si el metodo a usar es post envia datos mediante el formulario.
    elif request.method == 'POST':
        correo = request.form["txtCorreo"]
        contraseña = request.form["txtContraseña"]
        rol = request.form["selectRol"]
        # Validaciones básicas
        if not correo or not contraseña or rol not in [r.value for r in Rol]:
            return render_template("formRegistrarUsuario.html", 
                                    mensaje="Todos los campos son obligatorio.")
        # Verificar si el usuario ya existe
        if usuarios.find_one({"correo": correo}):
            return render_template("formRegistrarUsuario.html", mensaje="El usuario ya existe.")
        # Crear usuario
        nuevo_usuario = {
            "correo": correo,
            "contraseña": contraseña,
            "rol": rol
        }
        #insertamos en la base de datos el nuevo usuario
        usuarios.insert_one(nuevo_usuario)
        return render_template("formRegistrarUsuario.html", mensaje="Usuario registrado correctamente.")

#Petición RUTA completarDatosPersonales: formulario para agregar datos al usuario.
@app.route("/completarDatosPersonales", methods=["GET", "POST"])
def completarDatosPersonales():
    if request.method == "GET":
        return render_template("formCompletarDatosPersonales.html")

    elif request.method == "POST":
        correo_usuario = session.get("correo")
        if not correo_usuario:
            return redirect("/iniciarSesion")

        # Obtener datos del formulario
        nombre1 = request.form.get("txtnombre1")
        nombre2 = request.form.get("txtnombre2")
        apellido1 = request.form.get("txtapellido1")
        apellido2 = request.form.get("txtapellido2")
        tipo_doc = request.form.get("selectDocumento")
        num_doc = request.form.get("intDocumento")
        correo_academico = request.form.get("txtCorreoAcademico")
        celular = request.form.get("intCelular")
        genero = request.form.get("selectGenero")
        fecha_nacimiento = request.form.get("fechaNacimiento")

        # Validación básica
        if not all([nombre1, apellido1, tipo_doc, num_doc, correo_academico, celular, genero, fecha_nacimiento]):
            return render_template("formRegistrarPersona.html", mensaje="Faltan campos obligatorios")

        # Guardar en la colección 'personas'
        persona = {
            "correo": correo_usuario,
            "nombres": {"primero": nombre1, "segundo": nombre2},
            "apellidos": {"primero": apellido1, "segundo": apellido2},
            "tipoDocumento": tipo_doc,
            "numeroDocumento": num_doc,
            "correoAcademico": correo_academico,
            "celular": celular,
            "genero": genero,
            "fechaNacimiento": fecha_nacimiento,
            "estado": "activo"
        }
        personas.insert_one(persona)

        # Obtener el rol del usuario desde la colección usuarios
        usuario = usuarios.find_one({"correo": correo_usuario})
        rol = usuario.get("rol") if usuario else None

        if rol:
            return render_template("formRegistroPorRol.html", rol=rol)
        else:
            return redirect("/iniciarSesion")


#Ruta para guardar datos del instructor
@app.route("/registrarInstructor/", methods=["POST"])
def registrarInstructor():
    correo_usuario = session.get("correo")
    if not correo_usuario:
        return redirect("/iniciarSesion")

    especialidades_json = request.form.get("especialidades")
    try:
        especialidades = json.loads(especialidades_json)
    except Exception:
        especialidades = []

    usuarios.update_one(
        {"correo": correo_usuario},
        {"$set": {
            "rolInfo": {
                "tipo": "instructor",
                "especialidades": especialidades
            },
            "estado": "activo"
        }}
    )
    return render_template("/menuInstructor.html/")


# Ruta para guardar datos del funcionario de bienestar
@app.route("/registrarFuncionarioBienestar/", methods=["POST"])
def registrarFuncionarioBienestar():
    correo_usuario = session.get("correo")
    if not correo_usuario:
        return redirect("/iniciarSesion")

    componente = request.form.get("selectComponente")
    especialidades_json = request.form.get("especialidades")

    try:
        especialidades = json.loads(especialidades_json)
    except Exception:
        especialidades = []

    usuarios.update_one(
        {"correo": correo_usuario},
        {"$set": {
            "rolInfo": {
                "tipo": "funcionarioBienestar",
                "componente": componente,
                "especialidades": especialidades
            },
            "estado": "activo"
        }}
    )

    return render_template("/menuFuncionarioBienestar.html/")
