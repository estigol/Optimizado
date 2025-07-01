import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

# --- Configuraciones de correo ---
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "remito.reporte@gmail.com"      # Correo desde donde se envía
password = "weej osel uccp wqos"               # App password, NO tu clave de gmail
bcc_email = "joanse4@gmail.com"   # CCO de auditoría (puedes poner el mismo sender si lo deseas)


def enviar_email(nombre, apellido, email, ruta_docx, referencia=None):
    """
    Envía el DOCX generado al correo del usuario y en copia oculta a calermedic.recepcion@gmail.com.
    referencia: número de referencia para el trámite, se incluirá en el asunto y cuerpo del correo si se proporciona.
    """
    # Asunto del correo, incluyendo referencia si se proporciona
    if referencia:
        asunto = f"Hoja de Ruta Inscripción - Calermedic (Ref: {referencia})"
    else:
        asunto = "Hoja de Ruta Inscripción - Calermedic"

    # Cuerpo del correo
    if referencia:
        cuerpo = f"Referencia de trámite: {referencia}\n\n"
    else:
        cuerpo = ""
    cuerpo += f"""Estimado(a) {nombre} {apellido},

Gracias por confiar en Calermedic. Adjunto encontrarás tu hoja de ruta (archivo Word), la cual deberás presentar en nuestras oficinas para agilizar tu proceso.

Si tienes alguna duda, puedes responder a este correo o comunicarte con nosotros al teléfono 3202184633 (Fabián Administrador).

De la misma forma, si lo prefieres, puedes iniciar tu pago en el siguiente enlace:
https://www.banco.scotiabankcolpatria.com/PagosElectronicos/Referencias.aspx?IdConvenio=10206

Solo ingresa tu número de documento de identidad en cada una de las casillas y realiza el pago por PSE.

¡Te esperamos!
"""

    # Construcción del mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = sender_email
    mensaje["To"] = email
    mensaje["Subject"] = asunto
    mensaje["Bcc"] = bcc_email

    mensaje.attach(MIMEText(cuerpo, "plain"))

    # Adjuntar DOCX (Word)
    with open(ruta_docx, "rb") as f:
        adjunto = MIMEApplication(
            f.read(),
            _subtype="vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        adjunto.add_header("Content-Disposition", "attachment", filename=os.path.basename(ruta_docx))
        mensaje.attach(adjunto)

    try:
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(sender_email, password)
        servidor.send_message(mensaje)
        servidor.quit()
        print(f"Correo enviado correctamente a {email}")
    except Exception as e:
        print("Error al enviar el correo:", e)
        raise
