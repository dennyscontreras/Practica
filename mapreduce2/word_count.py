from flask import Flask, render_template, request
from mrjob.job import MRJob
import re

app = Flask(__name__)

class MRContadorPalabras(MRJob):
    
    def mapper(self, _, linea):
        EXPRESION_PALABRA = re.compile(r"[\w']+")
        for palabra in EXPRESION_PALABRA.findall(linea):
            yield (palabra.lower(), 1)
    
    def reducer(self, palabra, conteos):
        yield (palabra, sum(conteos))

def contar_palabras(nombre_archivo):
    trabajo = MRContadorPalabras(args=[nombre_archivo])
    with trabajo.make_runner() as corredor:
        corredor.run()
        conteos_palabras_ordenados = sorted(trabajo.parse_output(corredor.cat_output()), key=lambda x: x[1], reverse=True)
        conteos_palabras_top = conteos_palabras_ordenados[:5]
        otros_conteos_palabras = conteos_palabras_ordenados[5:]
        return conteos_palabras_top, otros_conteos_palabras

@app.route('/', methods=['GET', 'POST'])
def index():
    conteo_palabras = None
    if request.method == 'POST':
        archivo_texto = request.files['archivo_texto']
        if archivo_texto:
            nombre_archivo = 'archivo_cargado.txt'
            archivo_texto.save(nombre_archivo)
            conteo_palabras = contar_palabras(nombre_archivo)
    return render_template('index.html', conteo_palabras=conteo_palabras)

if __name__ == '__main__':
    app.run(debug=True)
