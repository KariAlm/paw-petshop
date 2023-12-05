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
            imagen= '{nueva_imagen}', \
            proveedor ='{nuevo_proveedor}' \
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
        lista_productos = []

        for producto in productos:
            producto_info = {
                "codigo": producto['codigo'],
                "nombre": producto['nombre'],
                "descripcion": producto['descripcion'],
                "precio": producto['precio'],
                "tamanio": producto['tamanio'],
                "stock": producto['stock'],
                "imagen": producto['imagen'],
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
        else:
            print("Producto no encontrado.")


catalogo = Catalogo(host='localhost', user='root', password='', database='paw_petproductos')
# catalogo.agregar_producto(1, 'Pienso para perros', 'Pienso para perros adultos', 21000.99, '1kg', 10, 'eso.png', 'purina')
# catalogo.agregar_producto(2, 'Pienso para gatos', 'Pienso para gatos', 13000.00, '1kg', 10, 'comida.png', 'purina')
# catalogo.agregar_producto(5, 'Jueguete para gatos', 'jueguete', 16000.00, 'Pequeño', 10, 'jueguete.png', 'petgasper')
#catalogo.listar_productos()

#Carpeta para guardar las imagenes.
RUTA_DESTINO = '../pages/imagen_inventario' 
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
@app.route("/productos/<int:codigo>", methods=["GET", "POST"])
def modificar_producto(codigo):
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre")
        nueva_descripcion = request.form.get("descripcion")
        nuevo_precio = request.form.get("precio")
        nuevo_tamanio = request.form.get("tamanio")
        nuevo_stock = request.form.get("stock")
        nuevo_proveedor = request.form.get("proveedor")

        # Procesar la imagen
        if 'nuevaImagen' in request.files:
            imagen = request.files['nuevaImagen']
            if imagen and allowed_file(imagen.filename):
                nombre_imagen = secure_filename(imagen.filename)
                nombre_base, extension = os.path.splitext(nombre_imagen)
                nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
                imagen.save(ruta_imagen)
            else:
                # Manejar el caso donde el archivo no es válido
                pass

        # Luego, llamar a tu función modificar_producto con los datos procesados
        catalogo.modificar_producto(codigo, nuevo_nombre, nueva_descripcion, nuevo_precio, nuevo_tamanio, nuevo_stock, nombre_imagen, nuevo_proveedor)

        # Redirigir a alguna página después de la modificación
        return redirect(url_for('producto_modificado', codigo=codigo))

    # Lógica para manejar el método GET y mostrar la página con el formulario.
    return render_template("tuplantilla.html", codigo=codigo)

@app.route("/producto_modificado/<int:codigo>")
def producto_modificado(codigo):
    # Puedes renderizar una plantilla especial para indicar que el producto ha sido modificado.
    # O simplemente redirigir a otra página.
    return render_template("producto_modificado.html", codigo=codigo)

# Función para verificar si una extensión de archivo es válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    # Busco el producto guardado
    producto = producto = catalogo.consultar_producto(codigo)
    if producto: # Si existe el producto...
        imagen_vieja = producto["imagen"]
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
    
@app.route("/productos/confirmar_eliminar/<int:codigo>", methods=["POST"])
def confirmar_eliminar_producto(codigo):
    # Aquí puedes realizar cualquier lógica de confirmación necesaria
    # Puedes verificar si el producto puede eliminarse y devolver una respuesta adecuada

    # En este ejemplo, simplemente devolveremos un mensaje de confirmación
    return jsonify({"mensaje": f"¿Estás seguro de que quieres eliminar el producto {codigo}?"}), 200
#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)