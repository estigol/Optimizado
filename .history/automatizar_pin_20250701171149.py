from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime
import os

def automatizar_pin(datos):
    print("[DEBUG] Entrando a automatizar_pin...")

    env_user = os.getenv("PAYNET_USER", "joanse4@gmail.com")
    env_pass = os.getenv("PAYNET_PASS", "Oficina2016*")
    login_url = "https://clientes.paynet.com.co/Login.aspx?ReturnUrl=%2f"

    # --- Manejo de fecha ---
    fecha_bd = datos.get('fecha_nacimiento', '')
    fecha_paynet = ''
    try:
        if '-' in fecha_bd:
            fecha_paynet = datetime.strptime(fecha_bd, '%Y-%m-%d').strftime('%d/%m/%Y')
        elif len(fecha_bd) == 8:
            fecha_paynet = datetime.strptime(fecha_bd, '%Y%m%d').strftime('%d/%m/%Y')
        else:
            fecha_paynet = fecha_bd
    except Exception as e:
        print("[DEBUG] Error formateando la fecha:", repr(e))
        fecha_paynet = fecha_bd

    elementos = {
        'recaudador': 'PSE',
        'moto': datos.get('categoria_moto', ''),
        'carro': datos.get('categoria_carro', ''),
        'genero': datos.get('genero', ''),
        'fecha_nacimiento': fecha_paynet,
        'tipo_documento': datos.get('tipo_documento', ''),
        'numero_documento': datos.get('numero_documento', ''),
        'nombres': datos.get('nombres', ''),
        'apellidos': datos.get('apellidos', ''),
        'correo_electronico': datos.get('correo', ''),
        'telefono': datos.get('telefono', ''),
    }

    browser = None
    context = None

    try:
        with sync_playwright() as playwright:
            print("[DEBUG] Lanzando Chromium con Playwright (headless=True)...")
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            print("[DEBUG] Navegador Chromium lanzado correctamente.")

            # --- Aquí va tu lógica de automatización (login, etc.) ---
            print("[DEBUG] Intentando login en Paynet...")
            # ...tu código...

            print("[DEBUG] Automatización finalizada correctamente.")
            return True

    except TimeoutError as e:
        print('[DEBUG] TimeoutError en automatizar_pin:', repr(e))
        return None
    except Exception as e:
        print("[DEBUG] Error general en automatizar_pin:", repr(e))
        return None
    finally:
        try:
            if context:
                context.close()
            if browser:
                browser.close()
        except Exception as e:
            print("[DEBUG] Error cerrando navegador/context:", repr(e))
