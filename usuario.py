from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

class Usuarios:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

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

        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
        existing_user = cursor.fetchone()

        if existing_user:
            return False, "El usuario ya existe."
        else:
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
usuarios_db = Usuarios(host='localhost', user='root', password='', database='usuarios_db')

# Resto del código Flask (rutas y manejo de peticiones HTTP)

@app.route("/usuarios/login", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data['usuario']
    contrasena = data['contrasena']

    if usuarios_db.login(usuario, contrasena):
        return jsonify({"mensaje": "Inicio de sesión exitoso"}), 200
    else:
        return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

@app.route("/usuarios/register", methods=["POST"])
def register():
    data = request.get_json()
    usuario = data['nombre-registro']
    contrasena = data['contrasena-registro']
    email = data['email-registro']

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
    data = request.get_json()
    new_contrasena = data['new_contrasena']
    usuarios_db.update_user(user_id, new_contrasena)
    return jsonify({"mensaje": "Contraseña actualizada"}), 200

@app.route("/usuarios/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    usuarios_db.delete_user(user_id)
    return jsonify({"mensaje": "Usuario eliminado"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

