let menu = document.querySelector('#menu')

let menu_bar = document.querySelector('#menu-bar')

menu_bar.addEventListener('click', () => {
    menu.classList.toggle('menu-toggle')
})
//se agrega seleccionador de cantidad de productos
const cantidad = document.getElementById("cantidad");
const buttonMas = document.getElementById("button+");
const buttonMenos = document.getElementById("button-");
let items = 0;
function aumentarItem() {
    items++;
    cantidad.textContent = items;
}
function restarItem() {
    if(items > 0) items--;
    cantidad.textContent = items;
}
buttonMas.addEventListener("click", aumentarItem);
buttonMenos.addEventListener("click", restarItem);

// vue.config.js
module.exports = {
    publicPath: '/',
  };

//const RUTA_DESTINO = 'http://localhost:8080/imagen_inventario/';
const fs = require('fs');

if (!fs.existsSync(RUTA_DESTINO)) {
    fs.mkdirSync(RUTA_DESTINO);
}

const RUTA_DESTINO = '/static/imagen_inventario/';

// Ejemplo de código para guardar una imagen usando Node.js y Express
const express = require('express');
const multer = require('multer');

const app = express();

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, RUTA_DESTINO);
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname);
    }
});

const upload = multer({ storage: storage });

app.post('/subir-imagen', upload.single('imagen'), (req, res) => {
    // Lógica adicional después de subir la imagen si es necesario
    res.json({ mensaje: 'Imagen subida con éxito' });
});

// Resto de tu código
app.listen(3000, () => {
    console.log('Servidor web iniciado');
});
// JavaScript en tu frontend

