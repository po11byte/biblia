import streamlit as st
import requests
import random
import json
from datetime import datetime

st.set_page_config(page_title="📖 API Bible Quiz", page_icon="✝", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .question-card {
        background-color: #f8fff8;
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bible-verse {
        background-color: #FFF8DC;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DAA520;
        font-style: italic;
        margin: 1rem 0;
    }
    .api-status {
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)
APIS_CONFIG = {
    "Bible API": {
        "url": "https://bible-api.com/",
        "needs_key": False,
        "description": "API gratuita para versículos bíblicos"
    },
    "Open Bible API": {
        "url": "https://api.openbible.info/",
        "needs_key": False,
        "description": "API de datos bíblicos abiertos"
    }
}
BIBLE_VERSIONS = {
    "RV1960": "Reina-Valera 1960",
    "NVI": "Nueva Versión Internacional",
    "DHH": "Dios Habla Hoy",
    "RVA": "Reina Valera Actualizada",
    "KJV": "King James Version",
    "ESV": "English Standard Version"
}
if 'puntuacion' not in st.session_state:
    st.session_state.puntuacion = 0
if 'preguntas_respondidas' not in st.session_state:
    st.session_state.preguntas_respondidas = 0
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = None
if 'mostrar_respuesta' not in st.session_state:
    st.session_state.mostrar_respuesta = False
if 'respuesta_usuario' not in st.session_state:
    st.session_state.respuesta_usuario = None
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'api_status' not in st.session_state:
    st.session_state.api_status = {}

def obtener_verso_biblico(libro, capitulo, versiculo, version="RV1960"):
    """Obtiene un versículo específico de la Bible API"""
    try:
        referencia = f"{libro}+{capitulo}:{versiculo}"
        url = f"https://bible-api.com/{referencia}?translation={version.lower()}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "texto": data.get('text', '').replace('\n', ' '),
                "referencia": data.get('reference', ''),
                "version": version,
                "success": True
            }
        else:
            return {"success": False, "error": "Error en la API"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def generar_pregunta_desde_api(tipo_pregunta, version="RV1960"):
    """Genera preguntas usando APIs bíblicas"""
    
    libros_biblicos = [
        {"libro": "Juan", "capitulo": 3, "versiculo": 16, "pregunta": "¿Qué dice Juan 3:16?"},
        {"libro": "Génesis", "capitulo": 1, "versiculo": 1, "pregunta": "¿Qué dice Génesis 1:1?"},
        {"libro": "Salmos", "capitulo": 23, "versiculo": 1, "pregunta": "¿Qué dice Salmos 23:1?"},
        {"libro": "Mateo", "capitulo": 5, "versiculo": 3, "pregunta": "¿Qué dice Mateo 5:3?"},
        {"libro": "Romanos", "capitulo": 8, "versiculo": 28, "pregunta": "¿Qué dice Romanos 8:28?"},
        {"libro": "1 Corintios", "capitulo": 13, "versiculo": 4, "pregunta": "¿Qué dice 1 Corintios 13:4?"},
        {"libro": "Filipenses", "capitulo": 4, "versiculo": 13, "pregunta": "¿Qué dice Filipenses 4:13?"},
        {"libro": "Proverbios", "capitulo": 3, "versiculo": 5, "pregunta": "¿Qué dice Proverbios 3:5?"},
        {"libro": "Isaías", "capitulo": 40, "versiculo": 31, "pregunta": "¿Qué dice Isaías 40:31?"},
        {"libro": "Jeremías", "capitulo": 29, "versiculo": 11, "pregunta": "¿Qué dice Jeremías 29:11?"}
    ]
    
    libro_seleccionado = random.choice(libros_biblicos)
    verso_info = obtener_verso_biblico(
        libro_seleccionado["libro"], 
        libro_seleccionado["capitulo"], 
        libro_seleccionado["versiculo"],
        version
    )
    
    if verso_info["success"]:
        texto_verso = verso_info["texto"]
        palabras_clave = [palabra for palabra in texto_verso.split() if len(palabra) > 4][:3]
        opciones_incorrectas = generar_opciones_incorrectas(palabras_clave, texto_verso)
        
        pregunta = {
            "pregunta": libro_seleccionado["pregunta"],
            "opciones": [texto_verso] + opciones_incorrectas,
            "respuesta": texto_verso,
            "referencia": verso_info["referencia"],
            "version": version,
            "tipo": "Versículo",
            "dificultad": random.choice(["Fácil", "Intermedia", "Difícil"]),
            "explicacion": f"Este es el versículo completo de {verso_info['referencia']} en la versión {BIBLE_VERSIONS.get(version, version)}."
        }
        

        random.shuffle(pregunta["opciones"])
        return pregunta
    else:
        return None

def generar_opciones_incorrectas(palabras_clave, texto_correcto):
    """Genera opciones incorrectas basadas en versículos similares"""
    versos_similares = [
        "Porque de tal manera amó Dios al mundo, que ha dado a su Hijo unigénito, para que todo aquel que en él cree, no se pierda, mas tenga vida eterna.",
        "En el principio creó Dios los cielos y la tierra.",
        "Jehová es mi pastor; nada me faltará.",
        "Bienaventurados los pobres en espíritu, porque de ellos es el reino de los cielos.",
        "Y sabemos que a los que aman a Dios, todas las cosas les ayudan a bien, esto es, a los que conforme a su propósito son llamados.",
        "El amor es sufrido, es benigno; el amor no tiene envidia, el amor no es jactancioso, no se envanece;",
        "Todo lo puedo en Cristo que me fortalece.",
        "Fíate de Jehová de todo tu corazón, y no te apoyes en tu propia prudencia.",
        "Pero los que esperan a Jehová tendrán nuevas fuerzas; levantarán alas como las águilas; correrán, y no se cansarán; caminarán, y no se fatigarán.",
        "Porque yo sé los pensamientos que tengo acerca de vosotros, dice Jehová, pensamientos de paz, y no de mal, para daros el fin que esperáis."
    ]
    opciones = [v for v in versos_similares if v != texto_correcto]
    return random.sample(opciones, min(3, len(opciones)))

def verificar_status_apis():
    """Verifica el estado de las APIs"""
    status = {}
    try:
        response = requests.get("https://bible-api.com/John+3:16", timeout=5)
        status["Bible API"] = " Conectada" if response.status_code == 200 else " Error"
    except:
        status["Bible API"] = " Sin conexión"
    
    return status

def reiniciar_quiz():
    """Reinicia el quiz"""
    st.session_state.puntuacion = 0
    st.session_state.preguntas_respondidas = 0
    st.session_state.historial = []
    st.session_state.mostrar_respuesta = False
    st.session_state.respuesta_usuario = None
st.markdown('<h1 class="main-header"> Bible Quiz con APIs</h1>', unsafe_allow_html=True)
st.markdown("### Preguntas bíblicas en tiempo real usando APIs gratuitas")

with st.sidebar:
    st.header(" Configuración de APIs")
    version_seleccionada = st.selectbox(
        "Versión de la Biblia:",
        list(BIBLE_VERSIONS.keys()),
        format_func=lambda x: BIBLE_VERSIONS[x]
    )
    
    st.markdown("---")
    st.header(" Estado de APIs")
    
    if st.button(" Verificar Conexión APIs"):
        st.session_state.api_status = verificar_status_apis()
    
    for api, status in st.session_state.api_status.items():
        st.write(f"{api}: {status}")
    
    st.markdown("---")
    st.header(" Tu Progreso")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Puntuación", st.session_state.puntuacion)
    with col2:
        st.metric("Preguntas", st.session_state.preguntas_respondidas)
    
    if st.session_state.preguntas_respondidas > 0:
        porcentaje = (st.session_state.puntuacion / st.session_state.preguntas_respondidas) * 100
        st.metric("Porcentaje", f"{porcentaje:.1f}%")
    
    st.markdown("---")
    
    if st.button(" Reiniciar Quiz", type="primary"):
        reiniciar_quiz()
        st.rerun()
        col_left, col_right = st.columns([3, 1])

with col_left:
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button(" Nueva Pregunta desde API", use_container_width=True):
            with st.spinner("Obteniendo pregunta desde la API..."):
                nueva_pregunta = generar_pregunta_desde_api("versiculo", version_seleccionada)
                
                if nueva_pregunta:
                    st.session_state.pregunta_actual = nueva_pregunta
                    st.session_state.mostrar_respuesta = False
                    st.session_state.respuesta_usuario = None
                    st.success(" Pregunta obtenida exitosamente!")
                else:
                    st.error(" Error al obtener pregunta de la API")
    
    with col_btn2:
        if st.session_state.pregunta_actual and not st.session_state.mostrar_respuesta:
            if st.button(" Mostrar Respuesta", use_container_width=True):
                st.session_state.mostrar_respuesta = True
                if st.session_state.pregunta_actual:
                 pregunta = st.session_state.pregunta_actual
        
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.write(f"*Dificultad:*  {pregunta['dificultad']}")
        with col_info2:
            st.write(f"*Tipo:*  {pregunta['tipo']}")
        with col_info3:
            st.write(f"*Versión:* {BIBLE_VERSIONS.get(pregunta['version'], pregunta['version'])}")
            st.markdown(f"###  {pregunta['pregunta']}")
            if not st.session_state.mostrar_respuesta:
               respuesta_seleccionada = st.radio(
                "Selecciona el versículo correcto:",
                pregunta['opciones'],
                key="opciones_respuesta"
            )
            
            if st.button(" Enviar Respuesta", type="primary"):
                st.session_state.respuesta_usuario = respuesta_seleccionada
                st.session_state.mostrar_respuesta = True
                st.session_state.preguntas_respondidas += 1
                if respuesta_seleccionada == pregunta['respuesta']:
                    st.session_state.puntuacion += 1
                st.session_state.historial.append({
                    'pregunta': pregunta['pregunta'],
                    'respuesta_usuario': respuesta_seleccionada[:100] + "..." if len(respuesta_seleccionada) > 100 else respuesta_seleccionada,
                    'respuesta_correcta': pregunta['respuesta'][:100] + "..." if len(pregunta['respuesta']) > 100 else pregunta['respuesta'],
                    'correcta': respuesta_seleccionada == pregunta['respuesta'],
                    'referencia': pregunta['referencia'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                if st.session_state.mostrar_respuesta:
                 st.markdown("---")
                 st.markdown(f'<div class="bible-verse">', unsafe_allow_html=True)
            st.write(f" Referencia:** {pregunta['referencia']}")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.session_state.respuesta_usuario:
                if st.session_state.respuesta_usuario == pregunta['respuesta']:
                    st.success(" *¡Correcto!* Has identificado el versículo correctamente.")
                else:
                    st.error(" *Incorrecto.* No has seleccionado el versículo correcto.")
                    st.write(" Versículo completo:")
                    st.info(pregunta['respuesta'])
                    st.write(f" Explicación:** {pregunta['explicacion']}")
        
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("👆 Haz clic en 'Nueva Pregunta desde API' para comenzar")

with col_right:
    st.markdown("###  Puntuación")
    st.metric("", f"{st.session_state.puntuacion}/{st.session_state.preguntas_respondidas}")
    
    if st.session_state.preguntas_respondidas > 0:
        porcentaje = (st.session_state.puntuacion / st.session_state.preguntas_respondidas) * 100
        st.write(f"{porcentaje:.1f}%** de aciertos")
    
    st.markdown("---")
    st.markdown("###  Estadísticas")
    
    if st.session_state.historial:
        correctas = sum(1 for h in st.session_state.historial if h['correcta'])
        total = len(st.session_state.historial)
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Correctas", correctas)
        with col_stat2:
            st.metric("Total", total)
            if st.session_state.historial:
             st.markdown("---")
    st.subheader(" Historial de Preguntas")
    
    for i, historial in enumerate(st.session_state.historial[:5]):
        with st.expander(f"Pregunta {i+1}: {historial['pregunta']} - {historial['timestamp']}", expanded=False):
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.write(f"*Tu respuesta:* {historial['respuesta_usuario']}")
            with col_h2:
                if historial['correcta']:
                    st.success(" Correcta")
                else:
                    st.error(" Incorrecta")
            
            st.write(f"*Referencia:* {historial['referencia']}")
            st.markdown("---")
st.subheader(" Información de las APIs")

col_api1, col_api2 = st.columns(2)

with col_api1:
    st.markdown("###  Bible API")
    st.write("*URL:* https://bible-api.com/")
    st.write("*Características:*")
    st.write("-  Totalmente gratuita")
    st.write("-  No requiere API key")
    st.write("-  Múltiples versiones de la Biblia")
    st.write("-  Fácil de usar")

with col_api2:
    st.markdown("### Open Bible API")
    st.write("*URL:* https://api.openbible.info/")
    st.write("*Características:*")
    st.write("-  Datos bíblicos abiertos")
    st.write("-  No requiere API key")
    st.write("-  Información de referencias cruzadas")
    st.write("-  Metadatos bíblicos")
    st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📖 <strong>Bible Quiz con APIs</strong> - Preguntas generadas en tiempo real desde APIs bíblicas</p>
    <p><em>"Toda la Escritura es inspirada por Dios y útil para enseñar, para redargüir, para corregir, para instruir en justicia" - 2 Timoteo 3:16</em></p>
</div>
""", unsafe_allow_html=True)






            


        


















