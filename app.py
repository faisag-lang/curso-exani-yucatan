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
CONTENIDO_CURSO = {
    "sesion_1_mat": {
        "titulo": "Pensamiento Matemático - Sesión 1: Aritmética",
        "teoria": """
        ### Conceptos básicos de Aritmética
        
        **1. Números Primos y Compuestos**
        * **Primos:** Son aquellos que son divisibles únicamente entre dos números: ellos mismos y la unidad (1). (Ejemplos: 2, 3, 5, 7, 11).
        * **Compuestos:** Son aquellos que tienen más de dos divisores. (Ejemplos: 4, 6, 8, 9).
        
        **2. Criterios de Divisibilidad**
        Reglas para saber si un número es divisible sin hacer la división:
        * **Divisible por 2:** Si termina en cero o cifra par.
        * **Divisible por 3:** Si la suma de sus dígitos es múltiplo de 3.
        * **Divisible por 5:** Si termina en cero o cinco.
        """,
        "ejercicios": [
            {
                "pregunta": "¿El número 123 se clasifica como...?",
                "opciones": ["Par y primo", "Impar y compuesto", "Impar y primo"],
                "correcta": "Impar y compuesto",
                "explicacion": "El 123 es impar (termina en 3). Además, 1+2+3=6 (múltiplo de 3), por lo que es compuesto."
            },
            {
                "pregunta": "¿El número 315 es divisible por...?",
                "opciones": ["2 y 3", "3, 4 y 5", "3 y 5"],
                "correcta": "3 y 5",
                "explicacion": "Termina en 5 (divisible por 5). Suma de dígitos 3+1+5=9 (divisible por 3)."
            }
        ]
    },
    "sesion_2_mat": {
        "titulo": "Pensamiento Matemático - Sesión 2: Jerarquía de Operaciones",
        "teoria": """
        ### Jerarquía de Operaciones
        Orden estricto para resolver:
        1. **Signos de agrupación:** (), [], {}.
        2. **Raíces y Potencias.**
        3. **Multiplicaciones y Divisiones:** De izquierda a derecha.
        4. **Sumas y Restas.**
        """,
        "ejercicios": [
            {
                "pregunta": "¿Cuál es el resultado de: 4 - 6 ÷ 2?",
                "opciones": ["-1", "1", "5"],
                "correcta": "1",
                "explicacion": "Primero división: 6÷2=3. Luego resta: 4-3=1."
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