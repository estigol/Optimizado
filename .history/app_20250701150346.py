from flask import Flask, render_template, request
import sqlite3
import os

from generar_pdf import generar_docx           # Usa el nuevo nombre de la función
from automatizar_pin import automatizar_pin
from enviar_email import enviar_email          # Asegúrate que recibe ruta_docx y lo adjunta

app = Flask(__name__)

@app.route("/")
def formulario():
    return render_template("formulario.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        datos = {campo: request.form.get(campo) for campo in [
            "nombres", "apellidos", "tipo_documento", "numero_documento",
            "ciudad_expedicion_documento", "nacionalidad", "fecha_nacimiento", "genero",
            "grupo_sanguineo", "estado_civil", "direccion", "ciudad", "correo",
            "telefono", "ocupacion", "escolaridad", "eps", "tipo_vinculacion",
            "contacto_emergencia", "telefono_emergencia", "parentesco_emergencia",
            "acompanante_menor", "tramite_moto", "categoria_moto", "tramite_carro",
            "categoria_carro", "usa_lentes", "usa_audifonos", "tiene_protesis",
            "tiene_marcapasos", "consume_medicamentos", "medicamentos",
            "ha_tenido_cirugias", "cirugias", "consume_alcohol", "tratamiento_psico"
        ]}

        try:
            # 1. Guardar en la base de datos
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pacientes (
                    nombres, apellidos, tipo_documento, numero_documento,
                    ciudad_expedicion_documento, nacionalidad, fecha_nacimiento, genero,
                    grupo_sanguineo, estado_civil, direccion, ciudad, correo,
                    telefono, ocupacion, escolaridad, eps, tipo_vinculacion,
                    contacto_emergencia, telefono_emergencia, parentesco_emergencia,
                    acompanante_menor, tramite_moto, categoria_moto, tramite_carro,
                    categoria_carro, usa_lentes, usa_audifonos, tiene_protesis,
                    tiene_marcapasos, consume_medicamentos, medicamentos,
                    ha_tenido_cirugias, cirugias, consume_alcohol, tratamiento_psico
                ) VALUES (
                    :nombres, :apellidos, :tipo_documento, :numero_documento,
                    :ciudad_expedicion_documento, :nacionalidad, :fecha_nacimiento, :genero,
                    :grupo_sanguineo, :estado_civil, :direccion, :ciudad, :correo,
                    :telefono, :ocupacion, :escolaridad, :eps, :tipo_vinculacion,
                    :contacto_emergencia, :telefono_emergencia, :parentesco_emergencia,
                    :acompanante_menor, :tramite_moto, :categoria_moto, :tramite_carro,
                    :categoria_carro, :usa_lentes, :usa_audifonos, :tiene_protesis,
                    :tiene_marcapasos, :consume_medicamentos, :medicamentos,
                    :ha_tenido_cirugias, :cirugias, :consume_alcohol, :tratamiento_psico
                )
            ''', datos)
            conn.commit()
            conn.close()

            # 2. Generar Word (.docx)
            ruta_docx = generar_docx(datos)

            # 3. Automatizar generación del PIN/referencia en Paynet
            automatizar_pin(datos)

            # 4. Enviar el correo electrónico con el Word (.docx) adjunto
            referencia = datos["numero_documento"]
            enviar_email(
                nombre=datos["nombres"],
                apellido=datos["apellidos"],
                email=datos["correo"],
                ruta_docx=ruta_docx,
                referencia=referencia
            )

            return "✅ Registro exitoso. Revisa tu correo electrónico para descargar tu hoja de ruta (archivo Word) y realizar tu pago. Puedes cerrar esta ventana."

        except Exception as e:
            print("Error en el proceso:", e)
            return "❌ Ocurrió un error durante el registro. Por favor intenta de nuevo o comunícate con Calermedic."

@app.route("/ver_registros")
def ver_registros():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()
    return render_template("ver_registros.html", pacientes=pacientes)

# (Opcional) Endpoint para descargar DOCX manualmente
from flask import send_file
@app.route("/descargar_hoja/<doc_id>")
def descargar_hoja(doc_id):
    archivo = os.path.abspath(f"PDFsGenerados/{doc_id}_hoja_ruta.docx")
    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
