import os
import unicodedata
from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime

categoria_xpaths = {
    'A1': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_0"]',
    'A2': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_1"]',
    'B1': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_2"]',
    'B2': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_3"]',
    'B3': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_4"]',
    'C1': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_5"]',
    'C2': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_6"]',
    'C3': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_cblCategoriaLiquidacion_7"]',
}
genero_xpaths = {
    'femenino': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_rblGeneroLiquidacion_0"]',
    'masculino': '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_rblGeneroLiquidacion_1"]',
}
fecha_xpath = '//*[@id="cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_txtFechaNacimientoLiquidacion"]'
btns = {
    'calcular': '#cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_btnCalcular',
    'matricular': '#cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_btnMatricular',
    'tipo_doc': '#cph_tcNuevoCliente_tpCliente_wucNuevoCliente_ddlTipoDoc',
}

def automatizar_pin(datos):
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
        print("Error formateando la fecha:", e)
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

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Login y navegación hasta formulario de Liquidación
        page.goto(login_url, timeout=60000)
        page.fill('xpath=//*[@id="cph_PaynetLogin_UserName"]', env_user)
        page.fill('xpath=/html/body/div/div/form/div[3]/div[1]/input[2]', env_pass)
        page.click('xpath=/html/body/div/div/form/div[3]/div[1]/div[3]/input')
        page.wait_for_load_state('networkidle', timeout=60000)

        # Acceder a Liquidación
        page.click('xpath=/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[4]/div[2]/div[3]/input[1]')
        page.click('xpath=/html/body/form/div[3]/div/div[1]/div[3]/ul/li[1]/a')

        # Llenado de campos en Liquidación
        page.select_option('select#cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_tipoEstudianteId', value='29')
        page.wait_for_load_state('networkidle', timeout=60000)

        # Selección de recaudador
        rec_select = 'select#cph_tcNuevoCliente_tpLiquidacion_wucNuevaLiquidacion_ddlTipoRecaudadorCentro'
        page.wait_for_selector(rec_select, timeout=60000)
        options = page.eval_on_selector_all(
            rec_select + ' option',
            'els => els.map(e => ({ value: e.value, label: (e.textContent || "").toString().trim() }))'
        )
        for opt in options:
            if opt['label'].strip().lower() == elementos['recaudador'].strip().lower():
                page.select_option(rec_select, value=opt['value'])
                print(f"Recaudador seleccionado: {opt['label']}")
                break

        # Selección de Moto y Carro
        if elementos['moto'] in categoria_xpaths:
            page.click(f"xpath={categoria_xpaths[elementos['moto']]}")
        if elementos['carro'] in categoria_xpaths:
            page.click(f"xpath={categoria_xpaths[elementos['carro']]}")

        # Género
        gen = elementos['genero'].lower()
        if gen in genero_xpaths:
            page.click(f"xpath={genero_xpaths[gen]}")
        if elementos['fecha_nacimiento']:
            page.fill(f"xpath={fecha_xpath}", elementos['fecha_nacimiento'])
            page.click('xpath=//body')
            page.wait_for_timeout(1000)

        # Calcular y matricular
        sel_calc = btns['calcular']
        page.wait_for_selector(sel_calc, timeout=30000)
        page.eval_on_selector(sel_calc, 'el => el.scrollIntoView()')
        page.click(sel_calc)

        sel_mat = btns['matricular']
        page.wait_for_selector(sel_mat, timeout=30000)
        page.eval_on_selector(sel_mat, 'el => el.scrollIntoView()')
        page.click(sel_mat)

        # Selección tipo de documento
        sel_doc = btns['tipo_doc']
        page.wait_for_selector(sel_doc, timeout=30000)
        options = page.eval_on_selector_all(
            sel_doc + ' option',
            'els => els.map(e => ({ value: e.value, label: (e.textContent || "").toString().trim() }))'
        )
        tipo_json = elementos['tipo_documento'].strip().lower()
        for opt in options:
            if opt['label'].strip().lower() == tipo_json:
                page.select_option(sel_doc, value=opt['value'])
                break

        # Selectores campos personales
        num_selector_css = '#cph_tcNuevoCliente_tpCliente_wucNuevoCliente_txtDocumento'
        name_selector = 'xpath=//*[@id="cph_tcNuevoCliente_tpCliente_wucNuevoCliente_txtNombres"]'
        last_selector = 'xpath=//*[@id="cph_tcNuevoCliente_tpCliente_wucNuevoCliente_txtApellidos"]'
        email_selector = 'xpath=//*[@id="cph_tcNuevoCliente_tpCliente_wucNuevoCliente_TxtEmail"]'
        phone_selector = 'xpath=//*[@id="cph_tcNuevoCliente_tpCliente_wucNuevoCliente_txtCelular"]'
        btn_siguiente = 'xpath=//*[@id="cph_tcNuevoCliente_tpCliente_wucNuevoCliente_btnContinuar"]'

        # --- FLUJO ROBUSTO ---

        # 1. Poner número documento, blur y esperar validación
        print(">>> PRIMER INTENTO: Documento")
        page.fill(num_selector_css, '')
        page.type(num_selector_css, elementos['numero_documento'])
        page.click('xpath=//body')
        page.wait_for_timeout(1200)

        # Verificar si borró datos personales (doc NO existe en base)
        name_val = page.input_value(name_selector).strip()
        apellido_val = page.input_value(last_selector).strip()
        correo_val = page.input_value(email_selector).strip()
        tel_val = page.input_value(phone_selector).strip()

        if not (name_val and apellido_val and correo_val and tel_val):
            print(">>> SISTEMA LIMPIÓ DATOS. REPITIENDO FLUJO como humano.")

            # 2. Volver a poner número de documento y blur
            page.fill(num_selector_css, '')
            page.type(num_selector_css, elementos['numero_documento'])
            page.click('xpath=//body')
            page.wait_for_timeout(700)

            # 3. Volver a poner TODOS los datos personales
            def force_fill(selector, valor, campo):
                print(f"Llenando {campo}: '{valor}'")
                page.fill(selector, '')
                page.type(selector, valor)
                page.click('xpath=//body')
            force_fill(name_selector, elementos['nombres'], "Nombres")
            force_fill(last_selector, elementos['apellidos'], "Apellidos")
            force_fill(email_selector, elementos['correo_electronico'], "Correo electrónico")
            force_fill(phone_selector, elementos['telefono'], "Teléfono")
            page.wait_for_timeout(700)
        else:
            print(">>> DATOS YA PRESENTES DESDE BD.")

        # Medio de pago
        medio_pago_selector = 'select#cph_tcNuevoCliente_tpCliente_wucNuevoCliente_ddlMedioPago'
        page.wait_for_selector(medio_pago_selector, timeout=30000)
        opciones_pago = page.eval_on_selector_all(
            medio_pago_selector + ' option',
            'els => els.map(e => ({ value: e.value, label: (e.textContent || "").toString().trim() }))'
        )
        for opt in opciones_pago:
            if opt['label'].strip().lower() == 'efectivo':
                page.select_option(medio_pago_selector, value=opt['value'])
                print("Medio de pago seleccionado: Efectivo")
                break

        page.click('xpath=//body')
        page.wait_for_timeout(400)

        # Click en Siguiente
        page.wait_for_selector(btn_siguiente, timeout=30000)
        page.click(btn_siguiente)
        page.wait_for_timeout(2500)

        # Click en Registrar del resumen
        btn_continuar_css = '#cph_tcNuevoCliente_tpReferencia_wucNuevoClienteResumen_btnRegistrar'
        page.wait_for_timeout(1000)
        page.wait_for_selector(btn_continuar_css, timeout=30000, state='visible')

        def aceptar_dialogo(dialog):
            print(f"Se abrió un diálogo: {dialog.message}")
            dialog.accept()

        page.once("dialog", aceptar_dialogo)
        page.eval_on_selector(btn_continuar_css, 'el => el.scrollIntoView()')
        page.click(btn_continuar_css, force=True)
        print("Click en CONTINUAR (Resumen) realizado y alerta aceptada.")

        nombre_archivo = f"screenshot_registro_{elementos['numero_documento']}.png"
        page.screenshot(path=nombre_archivo)
        print(f"Screenshot guardada en {nombre_archivo}")

        page.wait_for_timeout(7000)

        return True

    except TimeoutError as e:
        print('TimeoutError:', e)
        return None
    finally:
        context.close()
        browser.close()
        playwright.stop()

if __name__ == '__main__':
    datos_test = {
        "recaudador": "Centro Prueba",
        "categoria_moto": "A1",
        "categoria_carro": "B1",
        "genero": "Femenino",
        "fecha_nacimiento": "2003-06-10",
        "tipo_documento": "Cédula",
        "numero_documento": "98394435",
        "nombres": "LAURA DANIELA",
        "apellidos": "YELA LOPEZ",
        "correo": "yela-lopez@hotmail.com",
        "telefono": "3103252072"
    }
    ok = automatizar_pin(datos_test)
    print("Automatización exitosa:", ok)



