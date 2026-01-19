import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN GOOGLE SHEETS
# ==========================================
st.set_page_config(page_title="Tutor EXANI-I | Telesecundaria", page_icon="📚", layout="wide")

# Nombre exacto de tu hoja en Google Drive
SHEET_NAME = "BD_Tutor_Exani"

def conectar_google_sheets():
    """Conecta con Google Sheets usando los secretos de Streamlit."""
    try:
        # Definir el alcance
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Crear credenciales desde los secretos
        # Nota: Streamlit convierte automáticamente la sección [gcp_service_account] de secrets.toml en un diccionario
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja
        sheet = client.open(SHEET_NAME)
        return sheet
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

def registrar_usuario(nombre, escuela, grupo, password):
    """Registra un nuevo usuario con contraseña."""
    sh = conectar_google_sheets()
    if not sh: return None, "Error de conexión"
    
    worksheet = sh.worksheet("Usuarios")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    nombre = nombre.strip().upper()
    password = password.strip()
    
    # Verificar si ya existe
    if not df.empty and nombre in df['nombre_completo'].values:
        return None, "El usuario ya existe. Por favor ve a la pestaña 'Ingresar'."
    
    # Crear nuevo
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_id = 1 if df.empty else df['id'].max() + 1
    # Nota: Guardamos password en texto plano por simplicidad educativa. 
    # En apps comerciales se debe encriptar.
    nuevo_usuario = [int(nuevo_id), nombre, escuela, grupo, fecha_hoy, password]
    worksheet.append_row(nuevo_usuario)
    return nuevo_id, "Registro exitoso"

def autenticar_usuario(nombre, password):
    """Verifica credenciales y devuelve el ID del usuario."""
    sh = conectar_google_sheets()
    if not sh: return None
    
    worksheet = sh.worksheet("Usuarios")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    nombre = nombre.strip().upper()
    password = password.strip()
    
    if df.empty: return None
    
    # Buscar coincidencia exacta de Nombre y Contraseña
    usuario = df[(df['nombre_completo'] == nombre) & (df['password'].astype(str) == password)]
    
    if not usuario.empty:
        return int(usuario.iloc[0]['id'])
    return None

def obtener_sesiones_completadas(usuario_id):
    """Recupera qué sesiones ya terminó el alumno."""
    sh = conectar_google_sheets()
    if not sh: return []
    
    worksheet = sh.worksheet("Progreso")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    if df.empty: return []
    
    # Filtrar por usuario y criterio de aprobado (ej. > 60% aciertos si quisieras filtrar)
    # Por ahora devolvemos todas las que haya intentado
    mis_sesiones = df[df['usuario_id'] == usuario_id]['sesion_id'].unique().tolist()
    return mis_sesiones

def guardar_progreso_sesion(usuario_id, sesion_id, puntaje, total):
    """Guarda el intento en la hoja 'Progreso'."""
    sh = conectar_google_sheets()
    if not sh: return
    
    worksheet = sh.worksheet("Progreso")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Estrategia "Append Only": Siempre agregamos una fila nueva (historial completo)
    # Esto es más seguro y rápido que buscar y actualizar celdas específicas en la nube.
    nueva_fila = [int(usuario_id), sesion_id, puntaje, total, fecha_hoy]
    worksheet.append_row(nueva_fila)

def obtener_historial_progreso():
    """Descarga todo el historial para análisis."""
    sh = conectar_google_sheets()
    if not sh: return pd.DataFrame()
    
    ws_progreso = sh.worksheet("Progreso")
    ws_usuarios = sh.worksheet("Usuarios")
    
    df_p = pd.DataFrame(ws_progreso.get_all_records())
    df_u = pd.DataFrame(ws_usuarios.get_all_records())
    
    if df_p.empty: return pd.DataFrame()
    
    # Unir tablas (Join)
    df_completo = pd.merge(df_p, df_u, left_on='usuario_id', right_on='id', how='left')
    return df_completo

# ==========================================
# 2. CONTENIDO DEL CURSO (VERSIÓN LIMPIA)
# ==========================================
# Reemplaza todo el diccionario CONTENIDO_CURSO con esto:

CONTENIDO_CURSO = {
    # =================================================================
    # SESIÓN 1: CONCEPTOS BÁSICOS
    # =================================================================
    "sesion_1_mat": {
        "titulo": "Pensamiento Matemático - Sesión 1: Conceptos básicos de aritmética",
        "teoria": """
        ### 1. Números Primos y Compuestos
        * **Números Primos:** Son aquellos divisibles únicamente entre dos números: ellos mismos y la unidad (1).
          * *Ejemplos:* 2, 3, 5, 7, 11, 13, 17, 19, 23, 29...
        * **Números Compuestos:** Son aquellos que tienen más de dos divisores. Se pueden expresar como la multiplicación de 2 o más primos.
          * *Ejemplos:* 4, 6, 8, 9, 10, 12... (El 9 es divisible entre 1, 3 y 9).

        ### 2. Criterios de Divisibilidad
        Reglas para saber si un número es divisible por otro sin hacer la división:
        * **Divisible por 2:** Si termina en cero o cifra par 0, 2, 4, 6, 8 (Ej: 24, 108, 550, 7312).
        * **Divisible por 3:** Si la suma de sus dígitos es múltiplo de 3 (Ej: 102 -> 1+0+2=3).
        * **Divisible por 4:** Si sus dos últimas cifras son ceros o múltiplo de 4.
        * **Divisible por 5:** Si termina en cero o cinco.
        * **Divisible por 6:** Si es divisible por 2 y por 3 a la vez.
        * **Divisible por 10:** Si su último dígito es cero.
        """,
        "ejercicios": [
            # --- EJERCICIOS DE PRÁCTICA ---
            {
                "pregunta": "Clasifica el número 71:",
                "opciones": ["Primo", "Compuesto", "Par"],
                "correcta": "Primo",
                "explicacion": "El 71 solo puede dividirse entre 1 y 71. No termina en par, sus dígitos suman 8 (no es múltiplo de 3) y no termina en 0 o 5."
            },
            {
                "pregunta": "¿El número 456 es divisible por 6?",
                "opciones": ["Sí", "No", "Solo por 2"],
                "correcta": "Sí",
                "explicacion": "Para ser divisible por 6, debe serlo por 2 y 3. Termina en par (6), así que es divisible por 2. La suma de sus dígitos (4+5+6=15) es múltiplo de 3. Por lo tanto, sí es divisible por 6."
            },
            {
                "pregunta": "Simplifica la fracción 70/84 a su mínima expresión:",
                "opciones": ["35/42", "5/6", "10/12"],
                "correcta": "5/6",
                "explicacion": "Dividimos ambos entre 2 -> 35/42. Luego dividimos entre 7 -> 35/7=5 y 42/7=6. Resultado: 5/6."
            },
            {
                "pregunta": "Problema: Un celular costó $9,309. ¿A cuánto hay que venderlo para ganar $1,315?",
                "opciones": ["$10,500", "$10,624", "$8,000"],
                "correcta": "$10,624",
                "explicacion": "Debes sumar el costo original más la ganancia deseada: 9,309 + 1,315 = 10,624."
            },
            {
                "pregunta": "Problema: Pagué con un billete de $200 una cuenta de $187.72 (suma de manzana, pera y pollo). ¿Cuánto cambio recibo?",
                "opciones": ["$12.28", "$13.50", "$22.28"],
                "correcta": "$12.28",
                "explicacion": "Es una resta simple: 200.00 - 187.72 = 12.28."
            },
            # --- TAREA DE LA SESIÓN ---
            {
                "pregunta": "1. El número 123 se clasifica como...",
                "opciones": ["Par y primo", "Impar y compuesto", "Impar y primo"],
                "correcta": "Impar y compuesto",
                "explicacion": "Es impar (termina en 3). Es compuesto porque la suma de sus dígitos es 1+2+3=6 (múltiplo de 3), por lo que es divisible entre 3."
            },
            {
                "pregunta": "2. ¿Cuáles de las siguientes parejas de números son compuestos?",
                "opciones": ["45 y 93", "19 y 45", "43 y 60"],
                "correcta": "45 y 93",
                "explicacion": "45 es divisible por 5. 93 es divisible por 3 (9+3=12). Las otras opciones tienen primos (19 y 43)."
            },
            {
                "pregunta": "3. Simplifica la fracción 125/35:",
                "opciones": ["25/7", "25/5", "20/7"],
                "correcta": "25/7",
                "explicacion": "Ambos terminan en 5, así que dividimos entre 5. 125/5 = 25 y 35/5 = 7."
            },
            {
                "pregunta": "4. El número 315 es divisible por:",
                "opciones": ["2 y 3", "3 y 5", "2, 3 y 5"],
                "correcta": "3 y 5",
                "explicacion": "No es divisible por 2 (es impar). Es divisible por 5 (termina en 5). Es divisible por 3 (3+1+5=9)."
            },
            {
                "pregunta": "5. Voy a repartir equitativamente 540 dulces entre 36 niños. ¿Cuántos tocan a cada uno?",
                "opciones": ["15", "16", "17"],
                "correcta": "15",
                "explicacion": "Realizamos la división: 540 ÷ 36 = 15."
            }
        ]
    },

    # =================================================================
    # SESIÓN 2: JERARQUÍA Y MCM/MCD
    # =================================================================
    "sesion_2_mat": {
        "titulo": "Pensamiento Matemático - Sesión 2: Jerarquía de Operaciones y MCM/MCD",
        "teoria": """
        ### 1. Jerarquía de Operaciones
        Orden estricto para resolver operaciones combinadas:
        1. **Signos de agrupación:** ( ), [ ], { }.
        2. **Raíces y potencias.**
        3. **Multiplicaciones y divisiones** (de izquierda a derecha).
        4. **Sumas y restas.**

        ### 2. Mínimo Común Múltiplo (mcm)
        Es la cifra más pequeña que es múltiplo común de todos los números del conjunto.
        * *Palabras clave:* "Coincidir", "Repetir", "Mínimo tiempo", "Encontrarse".

        ### 3. Máximo Común Divisor (mcd)
        Es el mayor número que divide a dos o más números de manera exacta.
        * *Palabras clave:* "Repartir", "Dividir", "Mayor tamaño posible", "Agrupar".
        """,
        "ejercicios": [
            # --- EJERCICIOS DE PRÁCTICA ---
            {
                "pregunta": "Resuelve: 4 - 6 ÷ 2 - 8 + 10",
                "opciones": ["7", "3", "1"],
                "correcta": "3",
                "explicacion": "1° División: 6÷2=3. Queda: 4 - 3 - 8 + 10. 2° Sumas y restas de izq a der: 1 - 8 + 10 = -7 + 10 = 3."
            },
            {
                "pregunta": "Resuelve: (88 ÷ 8) x 5 - 5^2",
                "opciones": ["30", "55", "300"],
                "correcta": "30",
                "explicacion": "1° Paréntesis: 88÷8=11. 2° Potencia: 5^2=25. Queda: 11 x 5 - 25. 3° Mult: 55 - 25 = 30."
            },
            {
                "pregunta": "Calcula el MCM de 12 y 30",
                "opciones": ["30", "60", "360"],
                "correcta": "60",
                "explicacion": "Múltiplos de 12: 12, 24, 36, 48, 60... Múltiplos de 30: 30, 60... El primero en coincidir es 60."
            },
            {
                "pregunta": "Problema: Una persona viaja cada 12 días, otra cada 20 y otra cada 6. Hoy coincidieron. ¿En cuántos días volverán a coincidir?",
                "opciones": ["60 días", "24 días", "120 días"],
                "correcta": "60 días",
                "explicacion": "Es un problema de coincidencia futura (MCM). MCM de 6, 12 y 20 es 60."
            },
            {
                "pregunta": "Problema: Se quieren cortar cuadrados lo más grandes posible de una madera de 256cm x 96cm.",
                "opciones": ["MCM", "MCD"],
                "correcta": "MCD",
                "explicacion": "Buscas dividir una cantidad en partes iguales y lo más grandes posible. Esto es Máximo Común Divisor."
            },
            # --- TAREA DE LA SESIÓN ---
            {
                "pregunta": "1. Resultado de (32-15) x 4 - 8^2",
                "opciones": ["8", "4", "2"],
                "correcta": "4",
                "explicacion": "(17) x 4 - 64 -> 68 - 64 = 4."
            },
            {
                "pregunta": "2. Si el MCD de los números es 20, los números podrían ser:",
                "opciones": ["2, 4 y 5", "20, 30 y 40", "20, 40 y 60"],
                "correcta": "20, 40 y 60",
                "explicacion": "El MCD debe ser un divisor de todos. 20 divide a 20, 40 y 60. En la opción B, 20 no divide a 30 exactamente."
            },
            {
                "pregunta": "3. Si el MCM de los números es 60, los números podrían ser:",
                "opciones": ["12 y 15", "15 y 18", "20 y 40"],
                "correcta": "12 y 15",
                "explicacion": "MCM(12, 15): 12,24,36,48,60 y 15,30,45,60. Coinciden en 60. En la opción C, el MCM sería 40."
            },
            {
                "pregunta": "4. Un faro se enciende cada 12s, otro cada 18s y otro cada 60s. Coinciden a las 6:30. ¿Cuántas veces coincidirán en los próximos 5 minutos?",
                "opciones": ["1 vez", "2 veces", "3 veces"],
                "correcta": "1 vez",
                "explicacion": "Calculamos MCM(12, 18, 60) = 180 segundos (3 minutos). En 5 minutos, solo volverán a coincidir una vez (a los 3 minutos)."
            },
            {
                "pregunta": "5. Se quiere dividir un campo de 360m x 150m en parcelas cuadradas lo más grandes posible. ¿Cuánto medirá el lado de cada parcela?",
                "opciones": ["10m", "30m", "50m"],
                "correcta": "30m",
                "explicacion": "Calculamos MCD(360, 150) = 30."
            }
        ]
    },

    # =================================================================
    # SESIÓN 3: FRACCIONES
    # =================================================================
    "sesion_3_mat": {
        "titulo": "Pensamiento Matemático - Sesión 3: Fracciones",
        "teoria": """
        ### 1. Tipos de Fracciones
        * **Propias:** Numerador < Denominador (Ej: 1/2). Valen menos de 1 entero.
        * **Impropias:** Numerador > Denominador (Ej: 5/2). Valen más de 1 entero.
        * **Mixtas:** Entero + Fracción propia (Ej: 1 1/3).

        ### 2. Operaciones con Fracciones
        * **Mismo denominador:** Se suman/restan directos los numeradores.
        * **Diferente denominador:**
            1. Calcular MCM de denominadores.
            2. Dividir MCM entre cada denominador y multiplicar por su numerador.
            3. Sumar/Restar resultados.

        ### 3. Fracciones Equivalentes
        Expresan la misma cantidad (Ej: 1/2 = 2/4). Se obtienen multiplicando o dividiendo numerador y denominador por el mismo número.
        """,
        "ejercicios": [
            # --- EJERCICIOS DE PRÁCTICA ---
            {
                "pregunta": "Encuentra una fracción equivalente a 9/12:",
                "opciones": ["3/4", "4/5", "2/3"],
                "correcta": "3/4",
                "explicacion": "Dividiendo ambos números entre 3 obtenemos 3/4."
            },
            {
                "pregunta": "Problema: Juan compra un bote de 1200g de helado. Se come 3/8. ¿Cuánto queda?",
                "opciones": ["450g", "750g", "800g"],
                "correcta": "750g",
                "explicacion": "Si come 3/8, quedan 5/8. (1200 ÷ 8) x 5 = 150 x 5 = 750g."
            },
            {
                "pregunta": "Problema: Un celular costó $1250 pero se vende a 2/5 de su costo. ¿Cuánto se perdió?",
                "opciones": ["$500", "$750", "$250"],
                "correcta": "$750",
                "explicacion": "Se vendió a $500 (1250 ÷ 5 x 2). La pérdida es Costo - Venta: 1250 - 500 = 750."
            },
            {
                "pregunta": "Suma: 3/4 + 2/4",
                "opciones": ["5/8", "5/4", "6/16"],
                "correcta": "5/4",
                "explicacion": "Al tener el mismo denominador, se pasa igual y se suman los numeradores: 3+2=5."
            },
            {
                "pregunta": "¿Qué fracción es mayor: 2/6 o 6/8?",
                "opciones": ["2/6", "6/8", "Son iguales"],
                "correcta": "6/8",
                "explicacion": "2/6 = 0.33... y 6/8 = 0.75. 6/8 es mayor."
            },
            # --- TAREA DE LA SESIÓN ---
            {
                "pregunta": "1. De los animales del zoo, 2/3 son mamíferos y 1/5 aves. ¿Qué fracción representan juntos?",
                "opciones": ["3/8", "13/15", "1/15"],
                "correcta": "13/15",
                "explicacion": "Suma de diferente denominador (MCM 15). (10 + 3) / 15 = 13/15."
            },
            {
                "pregunta": "2. Claudia gastó 3/4 de 16€. Ángel gastó 2/5 de 30€. ¿Quién gastó más?",
                "opciones": ["Claudia", "Ángel", "Iguales"],
                "correcta": "Iguales",
                "explicacion": "Claudia: (16÷4)x3 = 12. Ángel: (30÷5)x2 = 12."
            },
            {
                "pregunta": "3. Tenía cierta cantidad, gasté 1/5 y me sobraron $160. ¿Cuánto tenía?",
                "opciones": ["$200", "$300", "$180"],
                "correcta": "$200",
                "explicacion": "Si gasté 1/5, me quedan 4/5. Si 4 partes son 160, 1 parte es 40. Total (5 partes) = 200."
            },
            {
                "pregunta": "4. Llevé $1200 y gasté 13/16. ¿Cuánto me sobró?",
                "opciones": ["$225", "$300", "$975"],
                "correcta": "$225",
                "explicacion": "Gasté: (1200÷16)x13 = 75x13 = 975. Sobró: 1200 - 975 = 225. (O calculando los 3/16 restantes)."
            },
            {
                "pregunta": "5. El 1/5 de la edad de Michelle son 6 años. ¿Cuántos años tiene?",
                "opciones": ["30", "25", "20"],
                "correcta": "30",
                "explicacion": "Si 1 parte es 6, el total (5 partes) es 6 x 5 = 30."
            }
        ]
    },

    # =================================================================
    # SESIÓN 4: PORCENTAJES Y PROPORCIONES
    # =================================================================
    "sesion_4_mat": {
        "titulo": "Pensamiento Matemático - Sesión 4: Porcentajes, Razones y Proporciones",
        "teoria": """
        ### 1. Porcentajes
        El (%) significa "un tanto de 100".
        * 50% = mitad (0.5)
        * 25% = cuarta parte (0.25)
        * **Cálculo:** Multiplica la cantidad por el decimal (Ej: 23% de 500 -> 500 x 0.23).

        ### 2. Proporcionalidad Directa
        Cuando una cantidad aumenta, la otra también en la misma proporción.
        * **Regla de tres:** (Producto cruzado). Si 3 manzanas cuestan $8, ¿12 manzanas? -> (12 x 8) / 3 = 32.

        ### 3. Proporcionalidad Inversa
        Cuando una cantidad aumenta, la otra disminuye.
        * *Ejemplo:* Trabajadores vs Tiempo. Más trabajadores = Menos tiempo.
        * **Cálculo:** Se multiplica horizontal y se divide. (5 obreros tardan 14 días. ¿10 obreros? -> (5 x 14) / 10 = 7 días).
        """,
        "ejercicios": [
            # --- EJERCICIOS DE PRÁCTICA ---
            {
                "pregunta": "Calcula el 25% de 456:",
                "opciones": ["114", "100", "125"],
                "correcta": "114",
                "explicacion": "Multiplica 456 x 0.25 (o divide entre 4). Resultado: 114."
            },
            {
                "pregunta": "Problema: En un estacionamiento hay 420 coches, el 35% son blancos. ¿Cuántos NO son blancos?",
                "opciones": ["147", "273", "150"],
                "correcta": "273",
                "explicacion": "Si 35% son blancos, el 65% no lo son. 420 x 0.65 = 273. (O calculas los blancos 147 y restas)."
            },
            {
                "pregunta": "3 manzanas cuestan $8. ¿Cuánto cuestan 12 manzanas? (Prop. Directa)",
                "opciones": ["$24", "$32", "$36"],
                "correcta": "$32",
                "explicacion": "Regla de tres: (12 x 8) ÷ 3 = 32."
            },
            {
                "pregunta": "5 trabajadores tardan 14 días en una obra. ¿Cuánto tardarán 10 trabajadores? (Prop. Inversa)",
                "opciones": ["28 días", "7 días", "10 días"],
                "correcta": "7 días",
                "explicacion": "Al doble de trabajadores, mitad de tiempo. (5 x 14) ÷ 10 = 7."
            },
            {
                "pregunta": "Una llave tira 204 litros en 12 mins. ¿En cuánto tiempo tirará 340 litros?",
                "opciones": ["15 min", "20 min", "18 min"],
                "correcta": "20 min",
                "explicacion": "Cada minuto tira 17L (204/12). 340 ÷ 17 = 20 minutos."
            },
            # --- TAREA DE LA SESIÓN ---
            {
                "pregunta": "1. Nueve lápices cuestan $40.50. ¿Cuánto cuestan 4 lápices?",
                "opciones": ["$16", "$18", "$20"],
                "correcta": "$18",
                "explicacion": "Costo unitario: 40.50 ÷ 9 = 4.50. Entonces 4 x 4.50 = 18."
            },
            {
                "pregunta": "2. Cinco albañiles tardan 90 días en un muro. Para terminarlo en 15 días, ¿cuántos albañiles se necesitan?",
                "opciones": ["30", "40", "45"],
                "correcta": "30",
                "explicacion": "Inversa: (5 x 90) = 450 (días-hombre). 450 ÷ 15 = 30 albañiles."
            },
            {
                "pregunta": "3. Un hospital tiene 420 camas ocupadas, que son el 84% del total. ¿Cuántas camas hay en total?",
                "opciones": ["450", "500", "550"],
                "correcta": "500",
                "explicacion": "Regla de tres: 420 es a 84, como X es a 100. (420 x 100) ÷ 84 = 500."
            },
            {
                "pregunta": "4. De 475 hombres, 76 saben planchar. ¿Qué porcentaje es?",
                "opciones": ["16%", "20%", "30%"],
                "correcta": "16%",
                "explicacion": "(76 ÷ 475) x 100 = 16%."
            },
            {
                "pregunta": "5. Observa los segmentos: AB=5, BC=15, DE=P-1, EF=P+1. Si AB/BC = DE/EF, halla P.",
                "opciones": ["8", "4", "2"],
                "correcta": "2",
                "explicacion": "5/15 = 1/3. Entonces (P-1)/(P+1) debe ser 1/3. 3(P-1) = 1(P+1) -> 3P-3 = P+1 -> 2P=4 -> P=2."
            }
        ]
    },
# =================================================================
    # SESIÓN 5: RECTA NUMÉRICA Y UNIDADES
    # =================================================================
    "sesion_5_mat": {
        "titulo": "Pensamiento Matemático - Sesión 5: Recta Numérica y Medición",
        "teoria": """
        ### [cite_start]1. La Recta Numérica [cite: 578-583]
        Es una línea que contiene todos los números reales. 
        * **Orden:** Los números a la derecha son mayores.
        * **Decimales:** Se ordenan comparando cifra por cifra (entero, décima, centésima). 
          * *Ejemplo:* 19.24 es mayor que 18.05.

        ### [cite_start]2. Unidades de Medición [cite: 615-630]
        * **Masa (Peso):** Unidad base: Gramo (g). (Kg = 1000g).
        * **Longitud:** Unidad base: Metro (m). (Km = 1000m).
        * **Capacidad:** Unidad base: Litro (L).
        * **Tiempo:** Hora, minuto, segundo.
        * **Temperatura:** Grados Celsius, Fahrenheit, Kelvin.
        """,
        "ejercicios": [
            {
                "pregunta": "Ordena de mayor a menor: 19.24, 18.05, 17.59, 18.4",
                "opciones": ["19.24, 18.4, 18.05, 17.59", "19.24, 18.05, 18.4, 17.59", "17.59, 18.05, 18.4, 19.24"],
                "correcta": "19.24, 18.4, 18.05, 17.59",
                "explicacion": "Primero va el entero mayor (19). Luego los de 18: comparamos decimales, 18.4 (que es 18.40) es mayor que 18.05. Al final 17.59."
            },
            {
                "pregunta": "¿Qué unidad usarías para medir la distancia entre Toluca y Puebla (155 unidades)?",
                "opciones": ["Metros", "Kilómetros", "Centímetros"],
                "correcta": "Kilómetros",
                "explicacion": "Las distancias geográficas largas se miden en Kilómetros (km)."
            },
            {
                "pregunta": "Ubica el número racional entre 1 y 2 en la recta numérica:",
                "opciones": ["0.5", "1.5", "2.5"],
                "correcta": "1.5",
                "explicacion": "1.5 es mayor que 1 y menor que 2. (0.5 es menor que 1, y 2.5 es mayor que 2)."
            },
            {
                "pregunta": "Sofía midió la mesa y obtuvo 165 unidades. ¿Qué unidad usó?",
                "opciones": ["Metros", "Centímetros", "Kilómetros"],
                "correcta": "Centímetros",
                "explicacion": "165 metros sería un edificio. 165 km una carretera. 165 cm (1.65m) es lógico para una mesa."
            },
            {
                "pregunta": "Rubén trabaja 6 horas diarias por 5 días (30 horas). ¿A cuántos minutos equivale?",
                "opciones": ["1800 min", "300 min", "1200 min"],
                "correcta": "1800 min",
                "explicacion": "30 horas x 60 minutos = 1800 minutos."
            }
        ]
    },

    # =================================================================
    # SESIÓN 6: LENGUAJE ALGEBRAICO
    # =================================================================
    "sesion_6_mat": {
        "titulo": "Pensamiento Matemático - Sesión 6: Lenguaje Algebraico",
        "teoria": """
        ### [cite_start]1. Conceptos Básicos [cite: 749-770]
        * **Variable (Incógnita):** Letra (x, y) que representa un valor desconocido.
        * **Coeficiente:** Número que multiplica a la variable (ej: en **2x**, el 2 es coeficiente).
        * **Términos Semejantes:** Tienen la misma letra y exponente (ej: 5x y 3x).

        ### [cite_start]2. Traducción al Álgebra [cite: 798-800]
        * "Un número aumentado en 5": **x + 5**
        * "El doble de un número": **2x**
        * "La diferencia de dos números": **x - y**
        """,
        "ejercicios": [
            {
                "pregunta": "Traduce: 'Paulina tiene 10 años menos que el doble de la edad de Carlos (x)'.",
                "opciones": ["x - 10", "2x - 10", "10 - 2x"],
                "correcta": "2x - 10",
                "explicacion": "'Doble de Carlos' es 2x. '10 años menos' significa restar 10 al final. Orden correcto: 2x - 10."
            },
            {
                "pregunta": "Simplifica: 5x² - 4x² - 7x²",
                "opciones": ["-6x²", "6x²", "16x²"],
                "correcta": "-6x²",
                "explicacion": "Son términos semejantes. Operamos coeficientes: 5 - 4 - 7 = 1 - 7 = -6. Resultado: -6x²."
            },
            {
                "pregunta": "Ecuación para: 'La suma de las edades de Juan (x) y Luis es 84. Luis tiene 8 años menos que Juan'.",
                "opciones": ["x + (x - 8) = 84", "x - 8 = 84", "2x + 8 = 84"],
                "correcta": "x + (x - 8) = 84",
                "explicacion": "Juan = x. Luis = x - 8. La suma de ambos debe dar 84."
            },
            {
                "pregunta": "Traduce: 'El cuadrado de un número más 100'.",
                "opciones": ["2x + 100", "x² + 100", "(x+100)²"],
                "correcta": "x² + 100",
                "explicacion": "'Cuadrado' es potencia 2 (x²). 'Más 100' es suma simple."
            },
            {
                "pregunta": "Don Manuel da a Pedro $8 más que a Luis (x). ¿Cómo se expresa lo de Pedro?",
                "opciones": ["x - 8", "8x", "x + 8"],
                "correcta": "x + 8",
                "explicacion": "Si Luis es x, y Pedro recibe 'más', se suma la cantidad: x + 8."
            }
        ]
    },

    # =================================================================
    # SESIÓN 7: PROBLEMAS DE ECUACIONES
    # =================================================================
    "sesion_7_mat": {
        "titulo": "Pensamiento Matemático - Sesión 7: Problemas de Ecuaciones Lineales",
        "teoria": """
        ### [cite_start]Resolución de Problemas [cite: 896-902]
        Pasos clave:
        1. **Identificar la incógnita (x):** ¿Qué me piden buscar?
        2. **Plantear la ecuación:** Traducir el texto a números y letras.
        3. **Despejar x:** Mover términos (suma pasa restando, multiplica pasa dividiendo).
        4. **Comprobar:** Sustituir el valor hallado en el problema original.
        """,
        "ejercicios": [
            {
                "pregunta": "¿Cuánto mide una cuerda si sus tres cuartas partes miden 200m?",
                "opciones": ["266.66m", "300m", "150m"],
                "correcta": "266.66m",
                "explicacion": "Planteamiento: (3/4)x = 200. Despeje: x = (200 * 4) / 3 = 800 / 3 = 266.66."
            },
            {
                "pregunta": "La suma de tres números consecutivos es 219. ¿Cuál es el primero?",
                "opciones": ["72", "73", "74"],
                "correcta": "72",
                "explicacion": "x + (x+1) + (x+2) = 219 -> 3x + 3 = 219 -> 3x = 216 -> x = 72."
            },
            {
                "pregunta": "Si al doble de un número le sumas 8 es igual a 30. ¿Cuál es el número?",
                "opciones": ["11", "12", "13"],
                "correcta": "11",
                "explicacion": "2x + 8 = 30 -> 2x = 22 -> x = 11."
            },
            {
                "pregunta": "Vicente gasta 21 euros en pantalón y camisa. La camisa cuesta 2/5 del pantalón. ¿Precio pantalón?",
                "opciones": ["15", "16", "20"],
                "correcta": "15",
                "explicacion": "Pantalón=x. Camisa=2/5x. x + 2/5x = 21 -> 7/5x = 21 -> x = (21*5)/7 = 15."
            },
            {
                "pregunta": "Un padre tiene 35 años y su hijo 5. ¿En cuántos años la edad del padre será el triple del hijo?",
                "opciones": ["10 años", "5 años", "15 años"],
                "correcta": "10 años",
                "explicacion": "Probando 10 años: Padre=45, Hijo=15. 45 es el triple de 15. Ecuación: 35+x = 3(5+x)."
            }
        ]
    },

    # =================================================================
    # SESIÓN 8: SISTEMAS DE ECUACIONES
    # =================================================================
    "sesion_8_mat": {
        "titulo": "Pensamiento Matemático - Sesión 8: Sistemas de Ecuaciones",
        "teoria": """
        ### [cite_start]Sistemas de Ecuaciones 2x2 [cite: 994-1003]
        Se usan cuando tenemos dos incógnitas y dos condiciones diferentes.
        * **Métodos de solución:** Suma y Resta (Reducción), Sustitución o Igualación.
        * **Ejemplo clásico:** Boletos de adulto y niño.
          1. Ecuación de cantidad: Adultos + Niños = Total Personas.
          2. Ecuación de dinero: (PrecioA * A) + (PrecioN * N) = Total Dinero.
        """,
        "ejercicios": [
            {
                "pregunta": "En un teatro hay 800 personas. Recaudación $21,125. Adulto $40, Niño $15. ¿Cuántos niños hay?",
                "opciones": ["435", "365", "525"],
                "correcta": "435",
                "explicacion": "A+N=800 y 40A+15N=21125. Despejando A=800-N y sustituyendo: 40(800-N)+15N=21125. -25N = -10875 -> N=435."
            },
            {
                "pregunta": "En una granja hay cerdos y patos. Cabezas: 52, Patas: 170. ¿Cuántos cerdos?",
                "opciones": ["35", "33", "20"],
                "correcta": "33",
                "explicacion": "C+P=52 y 4C+2P=170. Multiplicamos primera por -2: -2C-2P=-104. Sumamos: 2C=66 -> C=33."
            },
            {
                "pregunta": "Si Patricia le da a Julissa $300, tienen lo mismo. Si Julissa le da a Patricia $300, Patricia tiene el doble. ¿Cuánto tiene Patricia?",
                "opciones": ["$2100", "$1500", "$900"],
                "correcta": "$2100",
                "explicacion": "P-300 = J+300. P+300 = 2(J-300). Resolviendo el sistema obtenemos P=2100."
            },
            {
                "pregunta": "Estacionamiento: 83 vehículos (coches y motos). 256 ruedas. ¿Cuántos coches?",
                "opciones": ["45", "38", "50"],
                "correcta": "45",
                "explicacion": "C+M=83, 4C+2M=256. -2C-2M=-166. Restando queda 2C=90 -> C=45."
            },
            {
                "pregunta": "Un padre plantea 20 problemas. Paga $15 por acierto, cobra $5 por fallo. La hija recibe $240. ¿Cuántos falló?",
                "opciones": ["3", "5", "6"],
                "correcta": "3",
                "explicacion": "A+F=20. 15A - 5F = 240. Resolviendo, A=17, F=3."
            }
        ]
    },
    
    # =================================================================
    # SESIÓN 9: GEOMETRÍA (ÁREAS Y VOLÚMENES)
    # =================================================================
    "sesion_9_mat": {
        "titulo": "Pensamiento Matemático - Sesión 9: Áreas y Volúmenes",
        "teoria": """
        ### 1. Perímetro y Área
        * **Perímetro (P):** Es la suma de los lados de una figura (el contorno).
        * **Área (A):** Es la medida de la superficie interior.
          * *Cuadrado:* L x L
          * *Rectángulo:* Base x Altura (b x h)
          * *Triángulo:* (Base x Altura) / 2
          * *Círculo:* Área = π x r² | Perímetro = π x Diámetro

        ### 2. Volumen
        Es el espacio que ocupa un cuerpo tridimensional.
        * **Prismas (Cajas):** Volumen = Área de la base x Altura.
        * **Cubo:** Lado x Lado x Lado (L³).
        * **Cilindro:** (π x r²) x h.
        """,
        "ejercicios": [
            {
                "pregunta": "Calcula el área de un triángulo con base de 12 cm y altura de 5 cm.",
                "opciones": ["30 cm²", "60 cm²", "17 cm²"],
                "correcta": "30 cm²",
                "explicacion": "Fórmula: (b x h) / 2. (12 x 5) / 2 = 60 / 2 = 30."
            },
            {
                "pregunta": "Si un cuadrado tiene un perímetro de 36 cm, ¿cuánto mide cada lado?",
                "opciones": ["9 cm", "6 cm", "12 cm"],
                "correcta": "9 cm",
                "explicacion": "El cuadrado tiene 4 lados iguales. 36 ÷ 4 = 9 cm."
            },
            {
                "pregunta": "¿Cuál es el volumen de un cubo que mide 3 metros por lado?",
                "opciones": ["9 m³", "27 m³", "54 m³"],
                "correcta": "27 m³",
                "explicacion": "Volumen cubo = L³. 3 x 3 x 3 = 27."
            },
            {
                "pregunta": "Calcula el área de un círculo cuyo radio mide 4 cm (considera pi=3.14).",
                "opciones": ["50.24 cm²", "25.12 cm²", "12.56 cm²"],
                "correcta": "50.24 cm²",
                "explicacion": "Área = π x r². r² = 4x4 = 16. Entonces 3.14 x 16 = 50.24."
            },
            {
                "pregunta": "Una alberca rectangular mide 10m de largo, 5m de ancho y 2m de profundidad. ¿Cuál es su volumen?",
                "opciones": ["100 m³", "50 m³", "17 m³"],
                "correcta": "100 m³",
                "explicacion": "Volumen prisma = Largo x Ancho x Alto. 10 x 5 x 2 = 100."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. El área de un rectángulo es 48 cm² y su base mide 8 cm. ¿Cuánto mide su altura?",
                "opciones": ["6 cm", "40 cm", "8 cm"],
                "correcta": "6 cm",
                "explicacion": "Área = b x h. 48 = 8 x h. Despejamos h = 48 / 8 = 6."
            },
            {
                "pregunta": "2. ¿Cuántos litros caben en un tanque cúbico de 2 metros de lado? (Recuerda: 1m³ = 1000 Litros).",
                "opciones": ["8000 L", "4000 L", "2000 L"],
                "correcta": "8000 L",
                "explicacion": "Volumen = 2 x 2 x 2 = 8 m³. Como 1 m³ son 1000 litros, son 8000 litros."
            },
            {
                "pregunta": "3. Halla el perímetro de una circunferencia con diámetro de 10 cm (pi=3.14).",
                "opciones": ["31.4 cm", "78.5 cm", "15.7 cm"],
                "correcta": "31.4 cm",
                "explicacion": "Perímetro = π x Diámetro. 3.14 x 10 = 31.4."
            },
            {
                "pregunta": "4. Se quiere pintar una pared de 4m x 3m. Si el bote de pintura rinde 10m², ¿cuántos botes necesito?",
                "opciones": ["2 botes", "1 bote", "1.5 botes"],
                "correcta": "2 botes",
                "explicacion": "Área pared = 12 m². Un bote cubre 10, así que necesito un segundo bote para los 2 m² restantes."
            },
            {
                "pregunta": "5. ¿Cuál es el volumen de un cilindro con base de área 20 cm² y altura de 10 cm?",
                "opciones": ["200 cm³", "2000 cm³", "30 cm³"],
                "correcta": "200 cm³",
                "explicacion": "Volumen = Área Base x Altura. 20 x 10 = 200."
            }
        ]
    },

    # =================================================================
    # SESIÓN 10: FUNCIONES Y GRÁFICAS
    # =================================================================
    "sesion_10_mat": {
        "titulo": "Pensamiento Matemático - Sesión 10: Modelos Lineales y Cuadráticos",
        "teoria": """
        ### Tipos de Funciones
        * **Función Constante:** La variable dependiente (y) no cambia. Su gráfica es una línea horizontal.
          * *Ejemplo:* y = 5
        * **Función Lineal:** Su gráfica es una línea recta inclinada. Tiene la forma **y = mx + b**.
          * *m:* Pendiente (inclinación). Si es positiva sube, si es negativa baja.
          * *b:* Intersección (donde cruza al eje vertical).
        * **Función Cuadrática:** Su gráfica es una curva llamada **Parábola**. Tiene la forma **y = ax² + bx + c**.
          * Si el término x² es positivo, abre hacia arriba (U).
          * Si es negativo, abre hacia abajo (∩).
        """,
        "ejercicios": [
            {
                "pregunta": "¿Qué gráfica representa la ecuación y = 3x - 1?",
                "opciones": ["Una recta", "Una parábola", "Una hipérbola"],
                "correcta": "Una recta",
                "explicacion": "Al tener la variable 'x' con exponente 1 (lineal), su gráfica siempre es una línea recta."
            },
            {
                "pregunta": "Si f(x) = x² - 3, ¿cuánto vale f(2)?",
                "opciones": ["1", "-1", "4"],
                "correcta": "1",
                "explicacion": "Sustituimos x por 2: (2)² - 3 = 4 - 3 = 1."
            },
            {
                "pregunta": "¿Cómo es la gráfica de y = -x² + 2?",
                "opciones": ["Parábola hacia abajo", "Parábola hacia arriba", "Línea recta"],
                "correcta": "Parábola hacia abajo",
                "explicacion": "Es cuadrática (x²), por lo que es parábola. Como el signo de x² es negativo, abre hacia abajo."
            },
            {
                "pregunta": "En la ecuación y = 5x + 2, ¿cuál es el valor de la pendiente?",
                "opciones": ["5", "2", "x"],
                "correcta": "5",
                "explicacion": "En la forma y=mx+b, la pendiente es el número 'm' que acompaña a la x. Aquí es 5."
            },
            {
                "pregunta": "Un taxi cobra $10 el banderazo y $5 por km. ¿Cuál es su modelo?",
                "opciones": ["y = 5x + 10", "y = 10x + 5", "y = 15x"],
                "correcta": "y = 5x + 10",
                "explicacion": "El costo fijo (b) es 10. El costo variable (m) es 5 por cada km (x). y = 5x + 10."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. Evalúa la función f(x) = 2x + 4 cuando x = -3.",
                "opciones": ["-2", "2", "-10"],
                "correcta": "-2",
                "explicacion": "2(-3) + 4 = -6 + 4 = -2."
            },
            {
                "pregunta": "2. ¿Qué ecuación representa una función constante?",
                "opciones": ["y = 8", "y = x", "y = x + 8"],
                "correcta": "y = 8",
                "explicacion": "No tiene variable 'x'. El valor de y siempre es 8, sin importar cuánto valga x."
            },
            {
                "pregunta": "3. ¿En qué punto corta al eje Y la recta y = 3x - 5?",
                "opciones": ["-5", "3", "5"],
                "correcta": "-5",
                "explicacion": "El corte con el eje Y está dado por el término independiente (b). En este caso, -5."
            },
            {
                "pregunta": "4. La trayectoria de un balón lanzado al aire es una:",
                "opciones": ["Parábola", "Línea Recta", "Circunferencia"],
                "correcta": "Parábola",
                "explicacion": "El movimiento de proyectiles bajo la gravedad describe una curva parabólica hacia abajo."
            },
            {
                "pregunta": "5. Si la pendiente de una recta es negativa, la recta:",
                "opciones": ["Baja de izquierda a derecha", "Sube de izquierda a derecha", "Es horizontal"],
                "correcta": "Baja de izquierda a derecha",
                "explicacion": "Pendiente negativa significa que la función es decreciente."
            }
        ]
    },

    # =================================================================
    # SESIÓN 11: BINOMIOS (PRODUCTOS NOTABLES)
    # =================================================================
    "sesion_11_mat": {
        "titulo": "Pensamiento Matemático - Sesión 11: Binomios y Productos Notables",
        "teoria": """
        ### Productos Notables
        Reglas para multiplicar binomios rápidamente sin hacer toda la operación.

        **1. Binomio al Cuadrado (a + b)²**
        * Regla: El cuadrado del primero + el doble del primero por el segundo + el cuadrado del segundo.
        * Fórmula: **a² + 2ab + b²**
        
        **2. Binomios Conjugados (a + b)(a - b)**
        * Son iguales pero con signo contrario en medio.
        * Regla: El cuadrado del primero MENOS el cuadrado del segundo.
        * Fórmula: **a² - b²**

        **3. Binomios con Término Común (x + a)(x + b)**
        * Tienen una letra igual y números distintos.
        * Regla: Cuadrado del común + (suma de los no comunes) por el común + (multiplicación de los no comunes).
        * Fórmula: **x² + (a+b)x + ab**
        """,
        "ejercicios": [
            {
                "pregunta": "Desarrolla el binomio al cuadrado: (x + 3)²",
                "opciones": ["x² + 6x + 9", "x² + 9", "x² + 3x + 9"],
                "correcta": "x² + 6x + 9",
                "explicacion": "1° Cuadrado de x -> x². 2° Doble de x por 3 -> 6x. 3° Cuadrado de 3 -> 9."
            },
            {
                "pregunta": "Resuelve los binomios conjugados: (x + 5)(x - 5)",
                "opciones": ["x² - 25", "x² + 25", "x² - 10x + 25"],
                "correcta": "x² - 25",
                "explicacion": "Es una diferencia de cuadrados. Cuadrado del primero (x²) menos cuadrado del segundo (25)."
            },
            {
                "pregunta": "Desarrolla: (x - 4)²",
                "opciones": ["x² - 8x + 16", "x² - 16", "x² + 8x - 16"],
                "correcta": "x² - 8x + 16",
                "explicacion": "El término medio es negativo porque: 2(x)(-4) = -8x. El último siempre es positivo (-4)²=16."
            },
            {
                "pregunta": "Multiplica: (x + 2)(x + 4) -> Término común",
                "opciones": ["x² + 6x + 8", "x² + 8x + 6", "x² + 8"],
                "correcta": "x² + 6x + 8",
                "explicacion": "Suma de no comunes: 2+4=6 (término medio 6x). Multiplicación: 2x4=8 (término final 8)."
            },
            {
                "pregunta": "Resultado de (2a + 3)²",
                "opciones": ["4a² + 12a + 9", "4a² + 9", "2a² + 6a + 9"],
                "correcta": "4a² + 12a + 9",
                "explicacion": "Cuadrado de 2a es 4a². Doble de (2a)(3) es 12a. Cuadrado de 3 es 9."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. Resultado de (m - 8)(m + 8)",
                "opciones": ["m² - 64", "m² + 64", "m² - 16m + 64"],
                "correcta": "m² - 64",
                "explicacion": "Conjugados: cuadrado del primero menos cuadrado del segundo."
            },
            {
                "pregunta": "2. Desarrolla (x + 10)²",
                "opciones": ["x² + 20x + 100", "x² + 100", "x² + 10x + 100"],
                "correcta": "x² + 20x + 100",
                "explicacion": "Término medio es el doble: 2 * x * 10 = 20x."
            },
            {
                "pregunta": "3. Multiplica (x - 3)(x + 5)",
                "opciones": ["x² + 2x - 15", "x² - 2x - 15", "x² - 15"],
                "correcta": "x² + 2x - 15",
                "explicacion": "Suma de (-3 + 5) = +2. Multiplicación de (-3)(5) = -15."
            },
            {
                "pregunta": "4. ¿Cuál es el término faltante? (x - 6)² = x² ______ + 36",
                "opciones": ["-12x", "+12x", "-6x"],
                "correcta": "-12x",
                "explicacion": "El doble del primero por el segundo: 2(x)(-6) = -12x."
            },
            {
                "pregunta": "5. Resultado de (3x - 1)(3x + 1)",
                "opciones": ["9x² - 1", "9x² + 1", "3x² - 1"],
                "correcta": "9x² - 1",
                "explicacion": "Conjugados. (3x)² = 9x². (1)² = 1. Se restan."
            }
        ]
    },

    # =================================================================
    # SESIÓN 12: FACTORIZACIÓN
    # =================================================================
    "sesion_12_mat": {
        "titulo": "Pensamiento Matemático - Sesión 12: Factorización",
        "teoria": """
        ### Factorización
        Es el proceso inverso a los productos notables. Consiste en descomponer una expresión algebraica en una multiplicación.

        **1. Factor Común**
        * Se busca el número y letra que se repite en todos los términos.
        * *Ejemplo:* 4x² + 8x -> El 4 y la x se repiten -> **4x(x + 2)**.

        **2. Trinomio Cuadrado Perfecto (TCP)**
        * Viene de un binomio al cuadrado.
        * Se saca raíz al primero y al último.
        * *Ejemplo:* x² + 6x + 9 -> Raíces x y 3 -> **(x + 3)²**.

        **3. Trinomio de la forma x² + bx + c**
        * Buscamos dos números que **multiplicados den c** y **sumados den b**.
        * *Ejemplo:* x² + 5x + 6 -> (x + 3)(x + 2) porque 3x2=6 y 3+2=5.
        """,
        "ejercicios": [
            {
                "pregunta": "Factoriza: x² + 7x + 10",
                "opciones": ["(x + 5)(x + 2)", "(x + 10)(x + 1)", "(x - 5)(x - 2)"],
                "correcta": "(x + 5)(x + 2)",
                "explicacion": "Buscamos dos números que multiplicados den 10 y sumados 7. Son 5 y 2."
            },
            {
                "pregunta": "Factoriza por término común: 5x² - 15x",
                "opciones": ["5x(x - 3)", "5(x² - 3x)", "x(5x - 15)"],
                "correcta": "5x(x - 3)",
                "explicacion": "El máximo común divisor de 5 y 15 es 5. La letra común es x. Factor: 5x."
            },
            {
                "pregunta": "Factoriza la diferencia de cuadrados: x² - 49",
                "opciones": ["(x + 7)(x - 7)", "(x - 7)²", "(x + 7)²"],
                "correcta": "(x + 7)(x - 7)",
                "explicacion": "Raíz de x² es x. Raíz de 49 es 7. Se ponen conjugados (uno más, uno menos)."
            },
            {
                "pregunta": "Factoriza el TCP: x² - 10x + 25",
                "opciones": ["(x - 5)²", "(x + 5)²", "(x - 25)(x + 1)"],
                "correcta": "(x - 5)²",
                "explicacion": "Raíz de 25 es 5. Como el término medio es negativo, es (x - 5)²."
            },
            {
                "pregunta": "Factoriza: x² - 3x - 10",
                "opciones": ["(x - 5)(x + 2)", "(x - 10)(x + 1)", "(x + 5)(x - 2)"],
                "correcta": "(x - 5)(x + 2)",
                "explicacion": "Multiplicados dan -10 y sumados -3. Los números son -5 y +2."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. ¿Cuál es el factor común de 12a³ + 4a?",
                "opciones": ["4a", "12a", "a"],
                "correcta": "4a",
                "explicacion": "El 4 divide al 12 y al 4. La 'a' está en ambos."
            },
            {
                "pregunta": "2. Factoriza x² - 81",
                "opciones": ["(x + 9)(x - 9)", "(x - 9)²", "(x + 81)(x - 1)"],
                "correcta": "(x + 9)(x - 9)",
                "explicacion": "Es diferencia de cuadrados. Raíz de 81 es 9."
            },
            {
                "pregunta": "3. Factoriza x² + 8x + 12",
                "opciones": ["(x + 6)(x + 2)", "(x + 4)(x + 3)", "(x + 12)(x + 1)"],
                "correcta": "(x + 6)(x + 2)",
                "explicacion": "Dos números que multiplicados den 12 y sumados 8. Son 6 y 2."
            },
            {
                "pregunta": "4. Factoriza x² + 2x + 1",
                "opciones": ["(x + 1)²", "(x - 1)²", "x(x + 2)"],
                "correcta": "(x + 1)²",
                "explicacion": "Es un Trinomio Cuadrado Perfecto. Raíz de 1 es 1. (x+1)²."
            },
            {
                "pregunta": "5. Factoriza x² - x - 20",
                "opciones": ["(x - 5)(x + 4)", "(x + 5)(x - 4)", "(x - 10)(x + 2)"],
                "correcta": "(x - 5)(x + 4)",
                "explicacion": "Multiplicados -20, sumados -1. Números: -5 y +4."
            }
        ]
    },
    # =================================================================
    # SESIÓN 13: RECTAS EN EL PLANO
    # =================================================================
    "sesion_13_mat": {
        "titulo": "Pensamiento Matemático - Sesión 13: Rectas en el Plano",
        "teoria": """
        ### La Recta en el Plano Cartesiano
        Las ecuaciones de primer grado con dos variables (ej. $y = mx + b$) se representan gráficamente como una línea recta.
        
        **Elementos clave de la ecuación $y = mx + b$:**
        * **m (Pendiente):** Indica la inclinación.
          * Si $m$ es positiva ($2x$), la recta sube (creciente).
          * Si $m$ es negativa ($-2x$), la recta baja (decreciente).
        * **b (Ordenada al origen):** Es el punto donde la recta corta al eje Y (vertical).
          * Ejemplo: En $y = 3x + 4$, la recta cruza el eje Y en el 4 positivo.
        """,
        "ejercicios": [
            {
                "pregunta": "¿Cuál es el punto de intersección con el eje Y de la recta y = -x + 5?",
                "opciones": ["(5,0)", "(0,5)", "(0,-1)"],
                "correcta": "(0,5)",
                "explicacion": "El término independiente (b) es +5, por lo que corta al eje Y en la coordenada (0, 5)."
            },
            {
                "pregunta": "¿Qué gráfica corresponde a y = 2x + 1?",
                "opciones": ["Una recta que sube y cruza en 1", "Una recta que baja y cruza en 1", "Una recta horizontal"],
                "correcta": "Una recta que sube y cruza en 1",
                "explicacion": "La pendiente (2) es positiva, así que sube. La ordenada al origen es 1, así que cruza Y en 1."
            },
            {
                "pregunta": "¿Cuál es la ordenada al origen de la recta y = -2x + 3?",
                "opciones": ["(3,0)", "(0,3)", "(0,-2)"],
                "correcta": "(0,3)",
                "explicacion": "La ordenada al origen es el valor de b, en este caso 3. Coordenada (0,3)."
            },
            {
                "pregunta": "¿Qué representación tiene la ecuación y = 8.5x - 11?",
                "opciones": ["Recta decreciente", "Recta creciente", "Curva"],
                "correcta": "Recta creciente",
                "explicacion": "Como el coeficiente de x (8.5) es positivo, la recta es creciente (va hacia arriba)."
            },
            {
                "pregunta": "Identifica la pendiente en y = -4x + 6",
                "opciones": ["6", "-4", "4"],
                "correcta": "-4",
                "explicacion": "La pendiente es el número que multiplica a la x, en este caso -4."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. ¿Cuál es el punto de intersección de la recta y = 4x + 2 con el eje Y?",
                "opciones": ["(0,2)", "(2,0)", "(0,4)"],
                "correcta": "(0,2)",
                "explicacion": "El valor de b es 2, así que la intersección es (0,2)."
            },
            {
                "pregunta": "2. Si la ecuación es y = -x + 1, ¿dónde corta al eje Y?",
                "opciones": ["(0,1)", "(1,0)", "(0,-1)"],
                "correcta": "(0,1)",
                "explicacion": "Corta en el valor independiente, que es +1."
            },
            {
                "pregunta": "3. ¿Cómo es la gráfica de y = -5x + 1?",
                "opciones": ["Creciente", "Decreciente", "Horizontal"],
                "correcta": "Decreciente",
                "explicacion": "La pendiente es -5 (negativa), por lo tanto la recta va hacia abajo."
            },
            {
                "pregunta": "4. ¿Cuál es la ordenada al origen de y = 15x + 2.5?",
                "opciones": ["(0, 2.5)", "(2.5, 0)", "(15, 0)"],
                "correcta": "(0, 2.5)",
                "explicacion": "Es el término independiente 2.5 en el eje Y."
            },
            {
                "pregunta": "5. La ecuación y = 3x representa una recta que:",
                "opciones": ["Pasa por el origen (0,0)", "Corta en 3", "Es paralela al eje X"],
                "correcta": "Pasa por el origen (0,0)",
                "explicacion": "No tiene término b (b=0), por lo que pasa exactamente por el centro del plano."
            }
        ]
    },

    # =================================================================
    # SESIÓN 14: PARÁBOLAS
    # =================================================================
    "sesion_14_mat": {
        "titulo": "Pensamiento Matemático - Sesión 14: Parábolas en el plano",
        "teoria": """
        ### La Parábola
        Las ecuaciones cuadráticas (donde la x está al cuadrado: $y = ax^2 + bx + c$) se grafican como una curva llamada **parábola**.
        
        **Características principales:**
        * **Concavidad (Hacia dónde abre):**
          * Si $x^2$ es positivo ($y = x^2$): Abre hacia **ARRIBA** (forma de U).
          * Si $x^2$ es negativo ($y = -x^2$): Abre hacia **ABAJO** (forma de montaña).
        * **Intersección Y:** El término independiente (c) indica dónde corta al eje vertical.
        * **Intersección X:** Son las soluciones de la ecuación cuando $y=0$ (Raíces).
        """,
        "ejercicios": [
            {
                "pregunta": "¿Hacia dónde abre la parábola y = -x² + 4?",
                "opciones": ["Hacia arriba", "Hacia abajo", "Es una recta"],
                "correcta": "Hacia abajo",
                "explicacion": "El término cuadrático es negativo (-x²), por lo que abre hacia abajo."
            },
            {
                "pregunta": "¿Cuál es la ordenada al origen de y = 2x² - 11?",
                "opciones": ["(0, -11)", "(-11, 0)", "(0, 2)"],
                "correcta": "(0, -11)",
                "explicacion": "El término independiente es -11, ese es el corte con el eje Y."
            },
            {
                "pregunta": "Identifica uno de los puntos de intersección con el eje X de: y = x² - 16",
                "opciones": ["x = 4", "x = 16", "x = 8"],
                "correcta": "x = 4",
                "explicacion": "Igualamos a 0: x² - 16 = 0 -> x² = 16. La raíz cuadrada de 16 es 4 (y -4)."
            },
            {
                "pregunta": "¿Cómo es la gráfica de y = 5x² + 2?",
                "opciones": ["U hacia arriba", "U invertida hacia abajo", "Línea recta"],
                "correcta": "U hacia arriba",
                "explicacion": "El 5x² es positivo, así que abre hacia arriba."
            },
            {
                "pregunta": "¿Cuál es la ordenada al origen de y = x² - 8x - 4?",
                "opciones": ["(0, 4)", "(0, -4)", "(-4, 0)"],
                "correcta": "(0, -4)",
                "explicacion": "El término sin x es -4."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. ¿Cuál es la ordenada al origen de y = 12x² + 4?",
                "opciones": ["(0, 4)", "(4, 0)", "(0, 12)"],
                "correcta": "(0, 4)",
                "explicacion": "Corta al eje Y en el término independiente +4."
            },
            {
                "pregunta": "2. ¿Hacia dónde abre la gráfica de y = -3x²?",
                "opciones": ["Arriba", "Abajo", "Derecha"],
                "correcta": "Abajo",
                "explicacion": "Coeficiente negativo (-3) indica apertura hacia abajo."
            },
            {
                "pregunta": "3. Puntos donde la parábola y = x² - 9 corta al eje X:",
                "opciones": ["3 y -3", "9 y -9", "0 y 9"],
                "correcta": "3 y -3",
                "explicacion": "x² = 9. Las raíces son +3 y -3."
            },
            {
                "pregunta": "4. La gráfica de y = x² + 2x - 3 corta al eje Y en:",
                "opciones": ["-3", "2", "1"],
                "correcta": "-3",
                "explicacion": "El término independiente es -3."
            },
            {
                "pregunta": "5. Si la parábola tiene vértice en el origen y abre hacia arriba, su ecuación puede ser:",
                "opciones": ["y = x²", "y = -x²", "y = x + 1"],
                "correcta": "y = x²",
                "explicacion": "Es la parábola base positiva."
            }
        ]
    },

    # =================================================================
    # SESIÓN 15: ÁNGULOS Y CÍRCULO
    # =================================================================
    "sesion_15_mat": {
        "titulo": "Pensamiento Matemático - Sesión 15: Ángulos y Circunferencia",
        "teoria": """
        ### Ángulos en Triángulos
        * La suma de los ángulos internos de **cualquier** triángulo es siempre **180°**.
        * Ejemplo: Si tienes un triángulo con ángulos de 50° y 60°, el tercero mide: $180 - (50+60) = 70°$.

        ### La Circunferencia
        * **Elementos:** Radio (del centro a la orilla), Diámetro (cuerda que pasa por el centro, vale 2 radios), Cuerda (une dos puntos), Tangente (toca un solo punto).
        * **Ángulos en la circunferencia:**
          * **Ángulo Central:** Tiene el vértice en el centro. Mide **lo mismo** que su arco.
          * **Ángulo Inscrito:** Tiene el vértice en la orilla del círculo. Mide la **mitad** de su arco.
        """,
        "ejercicios": [
            {
                "pregunta": "En un triángulo, dos ángulos miden 60° y 40°. ¿Cuánto mide el tercero?",
                "opciones": ["80°", "100°", "90°"],
                "correcta": "80°",
                "explicacion": "Suma total = 180°. 180 - (60 + 40) = 180 - 100 = 80°."
            },
            {
                "pregunta": "Si un ángulo central mide 80°, ¿cuánto mide el arco que lo subtiende?",
                "opciones": ["40°", "80°", "160°"],
                "correcta": "80°",
                "explicacion": "El ángulo central mide exactamente lo mismo que su arco."
            },
            {
                "pregunta": "Si un arco mide 100°, ¿cuánto mide su ángulo inscrito?",
                "opciones": ["50°", "100°", "200°"],
                "correcta": "50°",
                "explicacion": "El ángulo inscrito mide la MITAD del arco. 100 / 2 = 50°."
            },
            {
                "pregunta": "Es la recta que toca a la circunferencia en un solo punto:",
                "opciones": ["Secante", "Tangente", "Cuerda"],
                "correcta": "Tangente",
                "explicacion": "Por definición, la tangente solo toca un punto externo. La secante la corta en dos."
            },
            {
                "pregunta": "Si los tres ángulos de un triángulo son iguales (equilátero), ¿cuánto mide cada uno?",
                "opciones": ["60°", "90°", "45°"],
                "correcta": "60°",
                "explicacion": "180° dividido entre 3 ángulos iguales da 60°."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. Determina el valor de x si los ángulos de un triángulo son x, 2x y 3x.",
                "opciones": ["30°", "60°", "90°"],
                "correcta": "30°",
                "explicacion": "x + 2x + 3x = 180 -> 6x = 180 -> x = 30."
            },
            {
                "pregunta": "2. ¿Cómo se llama el segmento que une dos puntos de la circunferencia sin pasar necesariamente por el centro?",
                "opciones": ["Radio", "Cuerda", "Diámetro"],
                "correcta": "Cuerda",
                "explicacion": "El diámetro es un caso especial de cuerda, pero la definición general es cuerda."
            },
            {
                "pregunta": "3. Un ángulo inscrito mide 30°. ¿Cuánto mide el arco correspondiente?",
                "opciones": ["15°", "30°", "60°"],
                "correcta": "60°",
                "explicacion": "El arco es el doble del ángulo inscrito. 30 * 2 = 60°."
            },
            {
                "pregunta": "4. En un triángulo rectángulo, un ángulo agudo mide 35°. ¿Cuánto mide el otro agudo?",
                "opciones": ["55°", "45°", "35°"],
                "correcta": "55°",
                "explicacion": "Ya tenemos 90°. Los otros dos deben sumar 90°. 90 - 35 = 55°."
            },
            {
                "pregunta": "5. ¿Cuánto suman los ángulos alrededor del centro de un círculo?",
                "opciones": ["180°", "360°", "270°"],
                "correcta": "360°",
                "explicacion": "Una vuelta completa equivale a 360 grados."
            }
        ]
    },

    # =================================================================
    # SESIÓN 16: DESIGUALDAD DEL TRIÁNGULO
    # =================================================================
    "sesion_16_mat": {
        "titulo": "Pensamiento Matemático - Sesión 16: Desigualdad del Triángulo",
        "teoria": """
        ### Regla de Construcción de Triángulos
        No cualquier conjunto de tres líneas puede formar un triángulo. Para que se cierre la figura, debe cumplirse la **Desigualdad del Triángulo**:
        
        **"La suma de dos lados cualesquiera debe ser siempre MAYOR que el tercer lado."**
        
        * $a + b > c$
        * $a + c > b$
        * $b + c > a$
        
        *Ejemplo:* Lados 3, 4 y 10.
        ¿3 + 4 > 10? No (7 no es mayor que 10). **No se puede formar triángulo.**
        """,
        "ejercicios": [
            {
                "pregunta": "¿Es posible formar un triángulo con lados de 3, 4 y 5 cm?",
                "opciones": ["Sí", "No"],
                "correcta": "Sí",
                "explicacion": "3+4=7 (>5), 3+5=8 (>4), 4+5=9 (>3). Cumple todas."
            },
            {
                "pregunta": "¿Con qué medidas SÍ es posible trazar un triángulo?",
                "opciones": ["13, 6, 5", "7, 7, 11", "1, 2, 5"],
                "correcta": "7, 7, 11",
                "explicacion": "A) 6+5=11 (no es mayor a 13). C) 1+2=3 (no es mayor a 5). B) 7+7=14 (>11), cumple."
            },
            {
                "pregunta": "Si dos lados miden 12 y 25, ¿el tercer lado puede medir 10?",
                "opciones": ["Sí", "No"],
                "correcta": "No",
                "explicacion": "10 + 12 = 22. 22 NO es mayor que 25. La figura no cerraría."
            },
            {
                "pregunta": "Si dos lados miden 9 y 14 cm, el tercer lado puede medir:",
                "opciones": ["3 cm", "25 cm", "10 cm"],
                "correcta": "10 cm",
                "explicacion": "Debe ser menor que la suma (9+14=23) y mayor que la resta (14-9=5). Solo 10 cumple."
            },
            {
                "pregunta": "¿Es posible formar un triángulo con lados 2, 2 y 4?",
                "opciones": ["Sí", "No"],
                "correcta": "No",
                "explicacion": "2 + 2 = 4. No es mayor que 4, es igual. Quedaría una línea plana, no un triángulo."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. ¿Con cuáles medidas NO se forma un triángulo?",
                "opciones": ["10, 10, 10", "3, 4, 8", "6, 8, 10"],
                "correcta": "3, 4, 8",
                "explicacion": "3 + 4 = 7. 7 no es mayor que 8. Es imposible."
            },
            {
                "pregunta": "2. Si dos lados miden 10 y 10, el tercero debe ser menor a:",
                "opciones": ["10", "20", "15"],
                "correcta": "20",
                "explicacion": "La suma es 10+10=20. El tercer lado debe ser menor a esa suma."
            },
            {
                "pregunta": "3. ¿Se puede formar un triángulo con medidas 9, 11 y 4?",
                "opciones": ["Sí", "No"],
                "correcta": "Sí",
                "explicacion": "4+9=13 (>11). Cumple la condición de que la suma de los pequeños supere al grande."
            },
            {
                "pregunta": "4. Condición para que exista el triángulo:",
                "opciones": ["a + b = c", "a + b > c", "a + b < c"],
                "correcta": "a + b > c",
                "explicacion": "La suma de dos lados siempre debe superar al tercero."
            },
            {
                "pregunta": "5. ¿Qué pasa si la suma de dos lados es igual al tercero?",
                "opciones": ["Se forma un triángulo plano", "Son líneas coincidentes (no hay triángulo)", "Es un triángulo rectángulo"],
                "correcta": "Son líneas coincidentes (no hay triángulo)",
                "explicacion": "Los lados se acostarían sobre el lado mayor formando una sola línea."
            }
        ]
    },

    # =================================================================
    # SESIÓN 17: PROBABILIDAD Y ESTADÍSTICA
    # =================================================================
    "sesion_17_mat": {
        "titulo": "Pensamiento Matemático - Sesión 17: Probabilidad y Estadística",
        "teoria": """
        ### Estadística Básica
        * **Media (Promedio):** Suma de todos los datos dividida entre la cantidad de datos.
        * **Mediana:** El dato que queda justo en el centro al ordenarlos de menor a mayor.
        * **Moda:** El dato que más se repite.

        ### Probabilidad
        Mide qué tan posible es que ocurra un evento.
        * **Fórmula:** $P(A) = \\frac{\\text{Casos Favorables}}{\\text{Casos Totales}}$
        * **Espacio Muestral:** Conjunto de todos los resultados posibles (Ej. en un dado: {1,2,3,4,5,6}).
        * **Aleatorio vs Determinista:** Aleatorio es azar (lanzar moneda), Determinista es seguro (calentar agua hierve).
        """,
        "ejercicios": [
            {
                "pregunta": "Calcula el promedio (media) de: 5, 6, 7, 7, 8, 9",
                "opciones": ["6", "7", "8"],
                "correcta": "7",
                "explicacion": "Suma: 5+6+7+7+8+9 = 42. Total de datos: 6. 42 / 6 = 7."
            },
            {
                "pregunta": "En el lanzamiento de un dado, ¿cuál es la probabilidad de que salga un número par?",
                "opciones": ["1/2", "1/6", "2/3"],
                "correcta": "1/2",
                "explicacion": "Casos totales: 6 (1,2,3,4,5,6). Pares: 3 (2,4,6). Probabilidad: 3/6 = 1/2."
            },
            {
                "pregunta": "Encuentra la mediana de: 2, 5, 8, 9, 10",
                "opciones": ["5", "8", "9"],
                "correcta": "8",
                "explicacion": "Ordenados quedan 2, 5, **8**, 9, 10. El centro es 8."
            },
            {
                "pregunta": "Señala un experimento aleatorio:",
                "opciones": ["Saber a qué hora amanece", "Ganar la lotería", "Calcular el área de un cuadrado"],
                "correcta": "Ganar la lotería",
                "explicacion": "Depende del azar. Los otros tienen resultados fijos o calculables."
            },
            {
                "pregunta": "Calcula la moda de: 3, 5, 2, 3, 7, 3, 8",
                "opciones": ["3", "5", "7"],
                "correcta": "3",
                "explicacion": "El 3 se repite tres veces, más que cualquier otro."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. Espacio muestral de lanzar una moneda:",
                "opciones": ["{Águila}", "{Sol}", "{Águila, Sol}"],
                "correcta": "{Águila, Sol}",
                "explicacion": "Son los dos únicos resultados posibles."
            },
            {
                "pregunta": "2. Probabilidad de sacar una bola roja de una urna con 3 rojas y 7 azules.",
                "opciones": ["3/7", "3/10", "7/10"],
                "correcta": "3/10",
                "explicacion": "Favorables: 3. Totales: 3+7=10. Resultado: 3/10."
            },
            {
                "pregunta": "3. Promedio de calificaciones: 10, 8, 9, 9, 10, 8",
                "opciones": ["9", "8.5", "9.5"],
                "correcta": "9",
                "explicacion": "Suma=54. Datos=6. 54/6 = 9."
            },
            {
                "pregunta": "4. Mediana de: 1, 2, 100",
                "opciones": ["2", "51", "100"],
                "correcta": "2",
                "explicacion": "El dato central es 2."
            },
            {
                "pregunta": "5. Si P(A) = 0, el evento es:",
                "opciones": ["Seguro", "Posible", "Imposible"],
                "correcta": "Imposible",
                "explicacion": "Probabilidad cero significa que nunca ocurrirá."
            }
        ]
    },

    # =================================================================
    # SESIÓN 18: SUCESIONES
    # =================================================================
    "sesion_18_mat": {
        "titulo": "Pensamiento Matemático - Sesión 18: Progresiones",
        "teoria": """
        ### Sucesiones o Progresiones
        Son conjuntos de números ordenados que siguen una regla.
        
        **1. Progresión Aritmética:**
        * Cada término se obtiene **sumando** una cantidad fija llamada diferencia ($d$) al anterior.
        * Fórmula: $a_n = a_1 + (n-1)d$
        * Ejemplo: 2, 5, 8, 11... (Va sumando 3).
        
        **2. Progresión Geométrica:**
        * Cada término se obtiene **multiplicando** por una cantidad fija llamada razón ($r$).
        * Fórmula: $a_n = a_1 \cdot r^{n-1}$
        * Ejemplo: 3, 6, 12, 24... (Se multiplica por 2).
        """,
        "ejercicios": [
            {
                "pregunta": "¿Qué número sigue en la sucesión: 15, 11, 7, 3...?",
                "opciones": ["0", "-1", "1"],
                "correcta": "-1",
                "explicacion": "La regla es restar 4. 3 - 4 = -1."
            },
            {
                "pregunta": "¿Qué número sigue en la sucesión geométrica: 3, 15, 75, 375...?",
                "opciones": ["1875", "450", "1125"],
                "correcta": "1875",
                "explicacion": "La razón es multiplicar por 5. 375 * 5 = 1875."
            },
            {
                "pregunta": "En la sucesión aritmética 5, 13, 21, 29... ¿Cuál es la diferencia (d)?",
                "opciones": ["5", "8", "6"],
                "correcta": "8",
                "explicacion": "13 - 5 = 8. 21 - 13 = 8. La diferencia es 8."
            },
            {
                "pregunta": "¿Cuál es el décimo término de la sucesión 7, 15, 23, 31...?",
                "opciones": ["71", "79", "87"],
                "correcta": "79",
                "explicacion": "Formula: a10 = 7 + (10-1)(8) = 7 + 9*8 = 7 + 72 = 79."
            },
            {
                "pregunta": "Suma de los primeros 10 términos de: 1, 5, 9, 13...",
                "opciones": ["190", "176", "200"],
                "correcta": "190",
                "explicacion": "a10 = 1 + 9(4) = 37. Suma = n(a1+an)/2 = 10(1+37)/2 = 10(38)/2 = 190."
            },
            # --- TAREA Y REPASO ---
            {
                "pregunta": "1. ¿Qué número sigue en: 2, 4, 8, 16...?",
                "opciones": ["24", "32", "20"],
                "correcta": "32",
                "explicacion": "Es geométrica por 2. 16 * 2 = 32."
            },
            {
                "pregunta": "2. ¿Qué número sigue en: 52, 46, 40, 34...?",
                "opciones": ["30", "28", "26"],
                "correcta": "28",
                "explicacion": "Va restando 6. 34 - 6 = 28."
            },
            {
                "pregunta": "3. En la sucesión 29, 36, 43, 50... el término 10 es:",
                "opciones": ["92", "99", "85"],
                "correcta": "92",
                "explicacion": "a1=29, d=7. a10 = 29 + 9(7) = 29 + 63 = 92."
            },
            {
                "pregunta": "4. Sigue la serie: -1, -7, -13, -19...",
                "opciones": ["-20", "-25", "-21"],
                "correcta": "-25",
                "explicacion": "Resta 6 cada vez. -19 - 6 = -25."
            },
            {
                "pregunta": "5. ¿Qué número sigue en la sucesión 13, 26, 52, 104...?",
                "opciones": ["208", "156", "200"],
                "correcta": "208",
                "explicacion": "Es el doble del anterior. 104 * 2 = 208."
            }
        ]
    }
    # COPIA Y PEGA AQUÍ LAS DEMÁS SESIONES
}

# ==========================================
# 3. INTERFAZ DE USUARIO
# ==========================================

def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2991/2991148.png", width=100)
    st.sidebar.title("Plataforma EXANI-I")
    
    # Verificar secretos
    if "gcp_service_account" not in st.secrets:
        st.error("⚠️ No se encontraron las credenciales de Google. Configura el archivo .streamlit/secrets.toml")
        return

    # --- AQUÍ SE DEFINE LA VARIABLE 'modo' ---
    modo = st.sidebar.radio("Navegación", ["Estudiante", "Docente (Admin)"])

    # ---------------- MODO ESTUDIANTE ----------------
    if modo == "Estudiante":
        st.title("🎓 Preparación para Bachillerato")
        
        # Si NO está logueado, mostrar pestañas de Ingreso/Registro
        if 'usuario_id' not in st.session_state:
            tab_login, tab_registro = st.tabs(["🔐 Ingresar (Ya tengo cuenta)", "📝 Registrarse (Soy nuevo)"])
            
            # --- PESTAÑA 1: LOGIN ---
            with tab_login:
                with st.form("login_form"):
                    st.write("Si ya te registraste antes, entra aquí:")
                    login_nombre = st.text_input("Tu Nombre Completo:")
                    login_pass = st.text_input("Tu Contraseña:", type="password")
                    btn_ingresar = st.form_submit_button("Entrar y Continuar")
                    
                    if btn_ingresar:
                        if login_nombre and login_pass:
                            with st.spinner("Buscando tu historial..."):
                                uid = autenticar_usuario(login_nombre, login_pass)
                                if uid:
                                    st.session_state['usuario_id'] = uid
                                    st.session_state['usuario_nombre'] = login_nombre.strip().upper()
                                    st.success("¡Bienvenido de nuevo!")
                                    st.rerun()
                                else:
                                    st.error("Nombre o contraseña incorrectos.")
                        else:
                            st.warning("Por favor llena ambos campos.")

            # --- PESTAÑA 2: REGISTRO ---
            with tab_registro:
                with st.form("registro_form"):
                    st.write("Crea tu cuenta para guardar tu avance:")
                    reg_nombre = st.text_input("Nombre Completo (Apellidos y Nombres):")
                    col1, col2 = st.columns(2)
                    reg_escuela = col1.text_input("Escuela:")
                    reg_grupo = col2.text_input("Grupo:")
                    reg_pass = st.text_input("Crea una contraseña secreta:", type="password")
                    st.caption("⚠️ ¡No olvides tu contraseña! La necesitarás mañana.")
                    
                    btn_registrar = st.form_submit_button("Crear Cuenta")
                    
                    if btn_registrar:
                        if reg_nombre and reg_pass:
                            with st.spinner("Creando tu perfil..."):
                                uid, mensaje = registrar_usuario(reg_nombre, reg_escuela, reg_grupo, reg_pass)
                                if uid:
                                    st.session_state['usuario_id'] = uid
                                    st.session_state['usuario_nombre'] = reg_nombre.strip().upper()
                                    st.success("¡Registro exitoso!")
                                    st.rerun()
                                else:
                                    st.error(mensaje)
                        else:
                            st.warning("El nombre y la contraseña son obligatorios.")

        # --- SI YA ESTÁ LOGUEADO (DASHBOARD DEL ALUMNO) ---
        else:
            nombre_alumno = st.session_state['usuario_nombre']
            uid = st.session_state['usuario_id']
            
            # Barra superior personalizada
            col_info, col_logout = st.columns([4, 1])
            with col_info:
                st.info(f"👤 Alumno: **{nombre_alumno}** | 📅 Hoy es: {datetime.now().strftime('%d/%m/%Y')}")
            with col_logout:
                if st.button("Cerrar Sesión"):
                    del st.session_state['usuario_id']
                    del st.session_state['usuario_nombre']
                    st.rerun()

            # Recuperar avance real desde Google Sheets
            sesiones_hechas = obtener_sesiones_completadas(uid)
            progreso_pct = len(sesiones_hechas) / len(CONTENIDO_CURSO) if len(CONTENIDO_CURSO) > 0 else 0
            
            st.progress(progreso_pct, text=f"Tu avance general: {len(sesiones_hechas)} de {len(CONTENIDO_CURSO)} sesiones completadas.")

            st.divider()
            
            # Selector inteligente de sesión
            lista_sesiones = list(CONTENIDO_CURSO.keys())
            
            # Determinar cuál es la siguiente sesión disponible
            indice_sugerido = 0
            for i, sesion in enumerate(lista_sesiones):
                if sesion not in sesiones_hechas:
                    indice_sugerido = i
                    break
            
            st.write("### 📚 Menú de Sesiones")
            sesion_seleccionada = st.selectbox(
                "Selecciona una sesión para trabajar:", 
                lista_sesiones, 
                index=indice_sugerido, 
                format_func=lambda x: ("✅ " if x in sesiones_hechas else "🔲 ") + CONTENIDO_CURSO[x]['titulo']
            )
            
            mostrar_sesion_estudio(uid, sesion_seleccionada)

    # ---------------- MODO DOCENTE ----------------
    elif modo == "Docente (Admin)":
        st.title("👨‍🏫 Panel de Control (Google Sheets)")
        password = st.sidebar.text_input("Contraseña", type="password")
        
        if password == "ATP2025":
            if st.button("🔄 Actualizar Datos desde Drive"):
                st.cache_data.clear()
            
            df = obtener_historial_progreso()
            
            if not df.empty:
                st.metric("Total de Intentos Registrados", len(df))
                st.subheader("Bitácora de Actividad")
                st.dataframe(df[['nombre_completo', 'grupo', 'sesion_id', 'puntaje', 'fecha_intento']].sort_values('fecha_intento', ascending=False))
                
                st.subheader("Análisis por Alumno")
                lista_alumnos = df['nombre_completo'].unique()
                alumno = st.selectbox("Selecciona un alumno:", lista_alumnos)
                if alumno:
                    df_alumno = df[df['nombre_completo'] == alumno]
                    st.write(f"Intentos de **{alumno}**:")
                    st.table(df_alumno[['sesion_id', 'puntaje', 'fecha_intento']])
            else:
                st.info("Aún no hay datos registrados en la hoja de 'Progreso'.")

def mostrar_sesion_estudio(uid, sesion_key):
    contenido = CONTENIDO_CURSO[sesion_key]
    st.divider()
    st.header(contenido['titulo'])
    
    tab1, tab2 = st.tabs(["📖 Teoría", "✍️ Ejercicios"])
    
    with tab1:
        st.markdown(contenido['teoria'])
    
    with tab2:
        st.write("Responde para avanzar:")
        respuestas = {}
        for idx, ej in enumerate(contenido['ejercicios']):
            st.markdown(f"**{idx+1}. {ej['pregunta']}**")
            respuestas[f"p_{idx}"] = st.radio(f"R{idx}", ej['opciones'], key=f"{sesion_key}_{idx}", label_visibility="collapsed")
            st.write("---")
        
        if st.button("Calificar Sesión", type="primary"):
            puntaje = 0
            total = len(contenido['ejercicios'])
            
            for idx, ej in enumerate(contenido['ejercicios']):
                if respuestas[f"p_{idx}"] == ej['correcta']:
                    puntaje += 1
                    st.success(f"✅ P{idx+1}: Correcto")
                else:
                    st.error(f"❌ P{idx+1}: Incorrecto")
                    with st.expander(f"Ver explicación P{idx+1}"):
                        st.info(ej['explicacion'])
            
            st.metric("Calificación", f"{puntaje}/{total}")
            
            # Guardar en Google Sheets
            with st.spinner("Guardando en la nube..."):
                guardar_progreso_sesion(uid, sesion_key, puntaje, total)
                st.toast("¡Progreso guardado en Google Drive!", icon="☁️")
                # Forzar recarga para actualizar barra de progreso
                # st.rerun() 

if __name__ == "__main__":
    main()









