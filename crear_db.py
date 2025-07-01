
import sqlite3

# Conectar o crear la base de datos local
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla 'pacientes' con todos los campos incluidos
cursor.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres TEXT,
    apellidos TEXT,
    tipo_documento TEXT,
    numero_documento TEXT,
    ciudad_expedicion_documento TEXT,
    nacionalidad TEXT,
    fecha_nacimiento TEXT,
    genero TEXT,
    grupo_sanguineo TEXT,
    estado_civil TEXT,
    direccion TEXT,
    ciudad TEXT,
    correo TEXT,
    telefono TEXT,
    ocupacion TEXT,
    escolaridad TEXT,
    eps TEXT,
    tipo_vinculacion TEXT,
    contacto_emergencia TEXT,
    telefono_emergencia TEXT,
    parentesco_emergencia TEXT,
    acompanante_menor TEXT,
    tramite_moto TEXT,
    categoria_moto TEXT,
    tramite_carro TEXT,
    categoria_carro TEXT,
    usa_lentes TEXT,
    usa_audifonos TEXT,
    tiene_protesis TEXT,
    tiene_marcapasos TEXT,
    consume_medicamentos TEXT,
    medicamentos TEXT,
    ha_tenido_cirugias TEXT,
    cirugias TEXT,
    consume_alcohol TEXT,
    tratamiento_psico TEXT
)
''')

# Confirmar y cerrar
conn.commit()
conn.close()

print("✅ Base de datos 'database.db' creada con columna 'nacionalidad'.")
