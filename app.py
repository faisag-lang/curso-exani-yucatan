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

def registrar_o_login(nombre, escuela, grupo):
    """Registra al usuario en la hoja 'Usuarios' si no existe."""
    sh = conectar_google_sheets()
    if not sh: return None
    
    worksheet = sh.worksheet("Usuarios")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre = nombre.strip().upper()
    
    # Verificar si el usuario ya existe
    if not df.empty and nombre in df['nombre_completo'].values:
        usuario_row = df[df['nombre_completo'] == nombre].iloc[0]
        return usuario_row['id'], nombre
    else:
        # Generar nuevo ID
        nuevo_id = 1 if df.empty else df['id'].max() + 1
        nuevo_usuario = [int(nuevo_id), nombre, escuela, grupo, fecha_hoy]
        worksheet.append_row(nuevo_usuario)
        return nuevo_id, nombre

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
        * **Divisible por 2:** Si termina en cero o cifra par (0, 2, 4, 6, 8).
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
    }
    # COPIA Y PEGA AQUÍ LAS DEMÁS SESIONES
}

# ==========================================
# 3. INTERFAZ DE USUARIO
# ==========================================

def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2991/2991148.png", width=100)
    st.sidebar.title("Plataforma EXANI-I")
    
    # Verificar secretos antes de iniciar
    if "gcp_service_account" not in st.secrets:
        st.error("⚠️ No se encontraron las credenciales de Google. Configura el archivo .streamlit/secrets.toml")
        return

    modo = st.sidebar.radio("Navegación", ["Estudiante", "Docente (Admin)"])

    if modo == "Estudiante":
        st.title("🎓 Preparación para Bachillerato")
        
        if 'usuario_id' not in st.session_state:
            with st.form("login_form"):
                st.write("### Identificación")
                nombre = st.text_input("Nombre Completo:")
                col1, col2 = st.columns(2)
                escuela = col1.text_input("Escuela:")
                grupo = col2.text_input("Grupo:")
                submit = st.form_submit_button("Ingresar y Guardar")
                
                if submit and nombre:
                    with st.spinner("Conectando con la base de datos..."):
                        uid, uname = registrar_o_login(nombre, escuela, grupo)
                        st.session_state['usuario_id'] = uid
                        st.session_state['usuario_nombre'] = uname
                        st.rerun()
        else:
            st.success(f"Hola, **{st.session_state['usuario_nombre']}**. Tu progreso se guarda automáticamente en la nube.")
            
            if st.sidebar.button("Cerrar Sesión"):
                del st.session_state['usuario_id']
                st.rerun()
            
            # Selector de sesión
            lista_sesiones = list(CONTENIDO_CURSO.keys())
            sesion_seleccionada = st.selectbox("Elige una sesión:", lista_sesiones, format_func=lambda x: CONTENIDO_CURSO[x]['titulo'])
            
            mostrar_sesion_estudio(st.session_state['usuario_id'], sesion_seleccionada)

    elif modo == "Docente (Admin)":
        st.title("👨‍🏫 Panel de Control (Google Sheets)")
        password = st.sidebar.text_input("Contraseña", type="password")
        
        if password == "ATP2025":
            if st.button("🔄 Actualizar Datos desde Drive"):
                st.cache_data.clear()
            
            df = obtener_historial_progreso()
            
            if not df.empty:
                # Métricas rápidas
                st.metric("Total de Intentos Registrados", len(df))
                
                # Tabla general
                st.subheader("Bitácora de Actividad")
                st.dataframe(df[['nombre_completo', 'grupo', 'sesion_id', 'puntaje', 'fecha_intento']].sort_values('fecha_intento', ascending=False))
                
                # Análisis por alumno
                st.subheader("Análisis por Alumno")
                alumno = st.selectbox("Selecciona un alumno:", df['nombre_completo'].unique())
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

if __name__ == "__main__":

    main()


