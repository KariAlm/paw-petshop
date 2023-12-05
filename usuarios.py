from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
CORS(app)

class Usuarios:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

        # Crear la tabla de usuarios si no existe
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(255) NOT NULL,
                contrasena VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
            )
        ''')
        self.conn.commit()

def login(self, usuario, contrasena):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s", (usuario, contrasena))
            user = cursor.fetchone()
            if user:
                return True
            else:
                return False
        except Exception as e:
            return False

def register(self, usuario, contrasena, email):
        cursor = self.conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
        existing_user = cursor.fetchone()

        if existing_user:
            return False, "El usuario ya existe."
        else:
            # Insertar el nuevo usuario solo si no existe
            cursor.execute("INSERT INTO usuarios (usuario, contrasena, email) VALUES (%s, %s, %s)", (usuario, contrasena, email))
            self.conn.commit()
            return True, "Registro exitoso."

def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        return users

def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        return user

def update_user(self, user_id, new_contrasena):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE usuarios SET contrasena=%s WHERE id=%s", (new_contrasena, user_id))
        self.conn.commit()

def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
        self.conn.commit()

# Configuración de la base de datos
usuarios_db = Usuarios(host='localhost', user='un_usuario_mysql', password='laa_contrasena_mysql', database='la_base_de_datos_mysql')

@app.route("/usuarios/login", methods=["POST"])
def login():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']

    if usuarios_db.login(usuario, contrasena):
        return jsonify({"mensaje": "Inicio de sesión exitoso"}), 200
    else:
        return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

@app.route("/usuarios/register", methods=["POST"])
def register():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    email = request.form['email']

    success, message = usuarios_db.register(usuario, contrasena, email)

    if success:
        return jsonify({"mensaje": message}), 201
    else:
        return jsonify({"mensaje": message}), 400

@app.route("/usuarios", methods=["GET"])
def get_all_users():
    users = usuarios_db.get_all_users()
    return jsonify(users)

@app.route("/usuarios/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = usuarios_db.get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

@app.route("/usuarios/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    new_contrasena = request.form['new_contrasena']
    usuarios_db.update_user(user_id, new_contrasena)
    return jsonify({"mensaje": "Contraseña actualizada"}), 200

@app.route("/usuarios/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    usuarios_db.delete_user(user_id)
    return jsonify({"mensaje": "Usuario eliminado"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)


