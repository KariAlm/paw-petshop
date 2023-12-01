from flask import Flask, request, jsonify
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
        self.conn = mysql.connector.connect(
            host=host, 
            user=user, 
            password=password, 
            database=database 
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
            codigo INT,
            nombre VARCHAR(255) NOT NULL,
            descripcion VARCHAR(1000) NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            tamanio VARCHAR(10),
            stock INT NOT NULL,
            imagen_url VARCHAR(255),
            proveedor VARCHAR(255))''')
        self.conn.commit()

    #agregar prod
    def agregar_producto(self, codigo, nombre, desccripcion, precio, tamanio, stock, imagen, proveedor):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo ={codigo}")
        producto_existe = self.cursor.fetchone()
        if producto_existe:
            return False
        
        sql = f"INSERT INTO productos \
            (codigo, nombre, descripcion,precio, tamanio, stock,  imagen_url, proveedor) \
            VALUES \
            ({codigo}, '{nombre}', '{descripcion}', {precio}, '{tamanio}', {stock},  '{imagen}', '{proveedor}')"
        valores = (codigo, nombre, desccripcion ,precio, tamanio , stock,  imagen , proveedor)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True      

        # #crear diccionario si no existe algun prod con ese codigo
        # producto = {
        #     'codigo': codigo, #int
        #     'nombre': nomb, #str
        #     'descripcion': desc, #str
        #     'precio': precio, #float
        #     'tamanio': tam, #str
        #     'stock': stock, #int
        #     'imagen': img, #str
        #     'marca': marca #str
        # }
        # #se almacena el prod en el arreglo
        # self.productos.append(producto)
        # return True #devuelve true si se agregó

    #consultar prod por codigo
    def consultar_producto(self, codigo):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    #modificar prod por codigo

    def modificar_producto(self, codigo, nuevo_nombre, nueva_descripcion, nuevo_precio, nuevo_tamanio, nuevo_stock, nueva_imagen, nuevo_proveedor):
        # for producto in self.productos:
        #     if producto['codigo'] == codigo:
        #         producto['nombre'] = nuevo_nombre
        #         producto['descripcion'] = nueva_descripcion
        #         producto['precio'] = nuevo_precio
        #         producto['tamanio'] = nuevo_tamanio
        #         producto['stock'] = nuevo_stock
        #         producto['imagen'] = nueva_imagen
        #         producto['proveedor'] = nuevo_proveedor
        #         return True
        # return False
        sql = f"UPDATE productos SET \
            nombre = '{nuevo_nombre}', \
            descripcion = '{nueva_descripcion}', \
            precio = '{nuevo_precio}', \
            tamanio = '{nuevo_tamanio}', \
            stock = '{nuevo_stock}', \
            imagen_url = '{nueva_imagen}', \
            proveedor ='{nuevo_proveedor}', \
            WHERE codigo = {codigo}"
        self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.rowcount > 0
#--------------------------------------------------------------------------------------------
    #eliminar prod por codigo
    def eliminar_producto(self, codigo):
        # for producto in self.productos:
        #     if producto['codigo'] == codigo:
        #         self.productos.remove(producto)
        #         return True
        # return False
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0
#--------------------------------------------------------------------------------------------
    #listar prod
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        print('-'*20)
        for producto in productos:
            print(f"Código: {producto['codigo']}")
            print(f"Nombre: {producto['nombre']}")
            print(f"Descripción: {producto['descripcion']}")
            print(f"Precio: {producto['precio']}")
            print(f"Tamaño: {producto['tamanio']}")
            print(f"Stock: {producto['stock']}")
            print(f"Imagen: {producto['imagen']}")
            print(f"Proveedor: {producto['proveedor']}")
            print("-" * 20)
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
            print(f"Tamaño: {producto['tamanio']}")
            print(f"Stock: {producto['stock']}")
            print(f"Imagen: {producto['imagen']}")
            print(f"Proveedor: {producto['proveedor']}")
            print("-" * 20)
        else:
            print("Producto no encontrado.")


catalogo = Catalogo(host='localhost', user='root', password='', database='productospetshop')

#Carpeta para guardar las imagenes.
RUTA_DESTINO = './imagen_inventario/'

#--------------------------------------------------------------------
@app.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)


#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto), 201
    else:
        return "Producto no encontrado", 404


#--------------------------------------------------------------------
@app.route("/productos", methods=["POST"])
def agregar_producto():
    #Recojo los datos del form
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    stock = request.form['stock']
    tamanio = request.form['tamanio']
    precio = request.form['precio']
    proveedor = request.form['proveedor']  
    imagen = request.files['imagen']

    # Me aseguro que el producto exista
    producto = catalogo.consultar_producto(codigo)
    if not producto: # Si no existe el producto...
        # Genero el nombre de la imagen
        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

    if catalogo.agregar_producto(codigo, nombre, descripcion, precio, tamanio, stock, nombre_imagen, proveedor):
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        return jsonify({"mensaje": "Producto agregado"}), 201
    else:
        return jsonify({"mensaje": "Producto ya existe"}), 400

#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    #Recojo los datos del form
    nueva_descripcion = request.form.get("descripcion")
    nuevo_precio = request.form.get("precio")
    tamanio = request.form['tamanio']
    nuevo_stock = request.form.get("stock")
    nuevo_proveedor = request.form.get("proveedor")
    imagen = request.files['imagen']

    # Procesamiento de la imagen
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
    imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))

    # Busco el producto guardado
    producto = producto = catalogo.consultar_producto(codigo)
    if producto: # Si existe el producto...
        imagen_vieja = producto["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
    
    if catalogo.modificar_producto(codigo, nuevo_nombre, nueva_descripcion, nuevo_precio, nuevo_tamanio, nuevo_stock, nombre_imagen, nuevo_proveedor):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 403


#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    # Busco el producto guardado
    producto = producto = catalogo.consultar_producto(codigo)
    if producto: # Si existe el producto...
        imagen_vieja = producto["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Luego, elimina el producto del catálogo
    if catalogo.eliminar_producto(codigo):
        return jsonify({"mensaje": "Producto eliminado"}), 200
    else:
        return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)