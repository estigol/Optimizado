from flask import Flask, render_template, request
import sqlite3

from generar_pdf import generar_pdf
from automatizar_pin import automatizar_pin
from enviar_email import enviar_email  # Asegúrate que esta función reciba un argumento "referencia" (número de documento)

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

            # 2. Generar PDF
            ruta_pdf = generar_pdf(datos)

            # 3. Automatizar generación del PIN/referencia en Paynet
            automatizar_pin(datos)  # Aquí no necesitas obtener ningún link, solo ejecutar el bot con los datos

            # 4. Enviar el correo electrónico con PDF y referencia personalizada
            referencia = datos["numero_documento"]
            enviar_email(
                nombre=datos["nombres"],
                apellido=datos["apellidos"],
                email=datos["correo"],
                ruta_pdf=ruta_pdf,
                referencia=referencia
            )

            return "✅ Registro exitoso. Revisa tu correo electrónico para descargar tu hoja de ruta y realizar tu pago. Puedes cerrar esta ventana."

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

if __name__ == "__main__":
    app.run()

