import os
import subprocess

print("[DEBUG] Inicio de app.py en Render")

# Forzar que los navegadores Playwright se instalen y se busquen en el directorio local del proyecto
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
print("[DEBUG] PLAYWRIGHT_BROWSERS_PATH =", os.environ["PLAYWRIGHT_BROWSERS_PATH"])

try:
    print("[DEBUG] Intentando instalar navegadores Chromium de Playwright en runtime...")
    subprocess.run(["playwright", "install", "chromium"], check=True)
    print("[DEBUG] Navegadores instalados correctamente.")
except Exception as e:
    print("[DEBUG] Error instalando navegadores Playwright:", repr(e))

try:
    from playwright.sync_api import sync_playwright
    print("[DEBUG] playwright.sync_api importado correctamente.")
except Exception as e:
    print("[DEBUG] Error importando playwright:", repr(e))

from flask import Flask, render_template, request, send_file, redirect
import sqlite3

from generar_pdf import generar_docx
from automatizar_pin import automatizar_pin
from enviar_email import enviar_email

app = Flask(__name__)

@app.route("/")
def formulario():
    return render_template("formulario.html")

@app.route("/submit", methods=["POST", "GET"])
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
            print("[DEBUG] Iniciando registro de usuario en base de datos.")
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
            print("[DEBUG] Usuario guardado en base de datos.")

            # 2. Generar Word (.docx)
            print("[DEBUG] Generando hoja de ruta DOCX.")
            ruta_docx = generar_docx(datos)

            # 3. Automatizar generación del PIN/referencia en Paynet
            print("[DEBUG] Ejecutando automatización de PIN con Playwright.")
            automatizar_pin(datos)

            # 4. Enviar el correo electrónico con el Word (.docx) adjunto
            print("[DEBUG] Enviando correo electrónico al usuario.")
            referencia = datos["numero_documento"]
            enviar_email(
                nombre=datos["nombres"],
                apellido=datos["apellidos"],
                email=datos["correo"],
                ruta_docx=ruta_docx,
                referencia=referencia
            )

            print("[DEBUG] Flujo completado sin errores.")
            return "✅ Registro exitoso. Revisa tu correo electrónico para descargar tu hoja de ruta (archivo Word) y realizar tu pago. Puedes cerrar esta ventana."

        except Exception as e:
            print("[DEBUG] Error en el proceso principal:", repr(e))
            return "❌ Ocurrió un error durante el registro. Por favor intenta de nuevo o comunícate con Calermedic."
    else:
        return redirect("/")

@app.route("/ver_registros")
def ver_registros():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()
    return render_template("ver_registros.html", pacientes=pacientes)

@app.route("/descargar_hoja/<doc_id>")
def descargar_hoja(doc_id):
    archivo = os.path.abspath(f"PDFsGenerados/{doc_id}_hoja_ruta.docx")
    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
