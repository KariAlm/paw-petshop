from flask import Flask, request, jsonify, render_template, request, redirect, url_for
from flask import request

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

#--------------------------------------------
class Catalogo:
    
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
            codigo INT,
            nombre VARCHAR(255) NOT NULL,
            descripcion VARCHAR(1000) NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            tamanio VARCHAR(10),
            stock INT NOT NULL,
            imagen VARCHAR(255),
            proveedor VARCHAR(255))''')
        self.conn.commit()
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    #agregar prod
    def agregar_producto(self, codigo, nombre, descripcion, precio, tamanio, stock, imagen, proveedor):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo ={codigo}")
        producto_existe = self.cursor.fetchone()
        if producto_existe:
            return False
        
        sql = "INSERT INTO productos (codigo, nombre, descripcion, precio, tamanio, stock, imagen, proveedor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        valores = (codigo, nombre, descripcion ,precio, tamanio , stock,  imagen, proveedor)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        print("Producto agregado correctamente.")
        return True      
#-------Cosultar prod-------------------------------------------------------------------------------------
    def consultar_producto(self, codigo):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    #modificar prod por codigo

    def modificar_producto(self, codigo, nombre, descripcion, precio, nuevo_tamanio, stock, imagen, proveedor):
        producto = self.consultar_producto(codigo)

        if not producto:
            return False

    # Ruta a la imagen anterior
        ruta_imagen_anterior = os.path.join(RUTA_DESTINO, producto['imagen'])

    # Actualiza la información del producto
        sql = f"UPDATE productos SET \
            nombre = '{nombre}', \
            descripcion = '{descripcion}', \
            precio = '{precio}', \
            tamanio = '{nuevo_tamanio}', \
            stock = '{stock}', \
            imagen = '{imagen}', \
            proveedor = '{proveedor}' \
            WHERE codigo = {codigo}"

        self.cursor.execute(sql)
        self.conn.commit()

        # Elimina la imagen anterior solo si se actualizó la imagen
        if imagen != producto['imagen'] and os.path.exists(ruta_imagen_anterior):
            os.remove(ruta_imagen_anterior)

        return self.cursor.rowcount > 0
#--------------------------------------------------------------------------------------------
    #eliminar prod por codigo
    def eliminar_producto(self, codigo):
       
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0
#--------------------------------------------------------------------------------------------
    #listar prod
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        lista_productos = []

        for producto in productos:
            producto_info = {
                "codigo": producto['codigo'],
                "nombre": producto['nombre'],
                "descripcion": producto['descripcion'],
                "precio": producto['precio'],
                "tamanio": producto['tamanio'],
                "stock": producto['stock'],
                "imagen": f"/static/imagen_inventario/{producto['imagen']}",
                "proveedor": producto['proveedor']
            }
            lista_productos.append(producto_info)

        return lista_productos
#--------------------------------------------------------------------------------------------
    #mostrar prod
    def mostrar_producto(self, codigo):
        producto = self.consultar_producto(codigo)
        if producto:
            print('-'*20)
            print(f"Código: {producto['codigo']}")
            print(f"Nombre: {producto['nombre']}")
            print(f"Descripción: {producto['descripcion']}")
            print(f"Precio: {producto['precio']}")
            print(f"Tamanio: {producto['tamanio']}")
            print(f"Stock: {producto['stock']}")
            print(f"Imagen: {producto['imagen']}")
            print(f"Proveedor: {producto['proveedor']}")
            print("-" * 20)
            producto_info = {
                "codigo": producto['codigo'],
                "nombre": producto['nombre'],
                "descripcion": producto['descripcion'],
                "precio": producto['precio'],
                "tamanio": producto['tamanio'],
                "stock": producto['stock'],
                "imagen": f"/static/imagen_inventario/{producto['imagen']}",  
                "proveedor": producto['proveedor']
            }
            return jsonify(producto_info), 201
        else:
            print("Producto no encontrado.")
            return jsonify({"mensaje": "Producto no encontrado"}), 404

            


catalogo = Catalogo(host='localhost', user='root', password='', database='paw_petproductos')
# catalogo.agregar_producto(1, 'Pienso para perros', 'Pienso para perros adultos', 21000.99, '1kg', 10, 'eso.png', 'purina')
# catalogo.agregar_producto(2, 'Pienso para gatos', 'Pienso para gatos', 13000.00, '1kg', 10, 'comida.png', 'purina')
# catalogo.agregar_producto(5, 'Jueguete para gatos', 'jueguete', 16000.00, 'Pequeño', 10, 'jueguete.png', 'petgasper')
# catalogo.listar_productos()

#Carpeta para guardar las imagenes.
RUTA_DESTINO = '/static/imagen_inventario/' 
#--------------------------------------------------------------------
@app.route("/productos", methods=["POST"])
def agregar_producto():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    stock = request.form['stock']
    tamanio = request.form['tamanio']
    imagen = request.files['imagen']
    proveedor = request.form['proveedor']

    producto = catalogo.consultar_producto(codigo)
    if not producto:
        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

        if catalogo.agregar_producto(codigo, nombre, descripcion, precio, tamanio, stock, nombre_imagen, proveedor):
            imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
            return jsonify({"mensaje": "Producto agregado"}), 201
        else:
            return jsonify({"mensaje": "Producto ya existe"}), 400
    else:
        return jsonify({"mensaje": "Producto ya existe"}), 400


#--------------------------------------------------------------------
@app.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos), 200
#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto), 201
    else:
        return "Producto no encontrado", 404
    


#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    #Recojo los datos del form
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    stock = request.form['stock']
    tamanio = request.form['tamanio']
    imagen = request.files['imagen']
    proveedor = request.form['proveedor']

    # Procesamiento de la imagen
    imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(imagen)
    imagen = f"{nombre_base}_{int(time.time())}{extension}"
    imagen.save(os.path.join(RUTA_DESTINO, imagen))

    # Busco el producto guardado
    producto = producto = catalogo.consultar_producto(codigo)
    if producto: # Si existe el producto...
        imagen= producto["imagen"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
    
    if catalogo.modificar_producto(codigo, nombre, descripcion, precio, tamanio, stock, imagen, proveedor):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 403


#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    # Busco el producto guardado
    producto = producto = catalogo.consultar_producto(codigo)
    if producto: # Si existe el producto...
        imagen = producto["imagen"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen)
        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
    # Luego, elimina el producto del catálogo
    if catalogo.eliminar_producto(codigo):
        return jsonify({"mensaje": "Producto eliminado"}), 200
    else:
        return jsonify({"mensaje": "Error al eliminar el producto"}), 500
#--------------------------------------------------------------------  
@app.route("/productos/confirmar_eliminar/<int:codigo>", methods=["GET"])
def confirmar_eliminar_producto(codigo):
    return render_template("confirmar_eliminar.html", codigo=codigo)
#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)