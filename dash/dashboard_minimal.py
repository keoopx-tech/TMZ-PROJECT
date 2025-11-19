import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# ==========================================
# CONFIGURACIÓN BACKEND
# ==========================================

def cargar_datos_backend():
    """
    Conecta con el backend para obtener datos.
    Reemplaza esta función con tu conexión real a base de datos.
    """
    # OPCIÓN 1: Conexión a base de datos
    # import psycopg2  # o pymysql, sqlite3, etc.
    # conn = psycopg2.connect(...)
    # df = pd.read_sql("SELECT * FROM pacientes", conn)
    
    # OPCIÓN 2: API REST
    # import requests
    # response = requests.get("https://tu-api.com/pacientes")
    # df = pd.DataFrame(response.json())
    
    # OPCIÓN 3: Archivo local en servidor (temporal)
    
    df = pd.read_excel("datos/tmz.xlsx")
    
    # SIMULACIÓN (reemplazar con código real)
    return None

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================

st.set_page_config(
    page_title="Tamizaje Genético",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS MINIMALISTAS
# ==========================================

st.markdown("""
    <style>
    /* Paleta minimalista para salud */
    :root {
        --primary-color: #2E5266;
        --secondary-color: #6E8898;
        --accent-color: #9FB1BC;
        --success-color: #52B788;
        --warning-color: #FFB703;
        --danger-color: #E63946;
        --bg-light: #F8F9FA;
    }
    
    /* Fondo limpio */
    .main {
        background-color: white;
        padding: 1rem 2rem;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tarjetas minimalistas */
    .metric-card {
        background: white;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Botones limpios */
    .stButton>button {
        background: white;
        border: 1px solid #DEE2E6;
        border-radius: 6px;
        color: #2E5266;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        border-color: #2E5266;
        background: #F8F9FA;
    }
    
    /* Paciente seleccionado */
    .stButton>button:focus {
        border-color: #2E5266;
        background: #EDF2F7;
        box-shadow: 0 0 0 2px rgba(46,82,102,0.1);
    }
    
    /* Tabs minimalistas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        border-bottom: 1px solid #E9ECEF;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border: none;
        color: #6C757D;
        padding: 0.75rem 0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2E5266;
        border-bottom: 2px solid #2E5266;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #2E5266;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6C757D;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    /* Headers limpios */
    h1 {
        color: #2E5266;
        font-weight: 600;
        font-size: 1.75rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2E5266;
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #495057;
        font-weight: 600;
        font-size: 1.125rem;
        margin-bottom: 0.75rem;
    }
    
    /* Sidebar limpio */
    [data-testid="stSidebar"] {
        background: #F8F9FA;
        border-right: 1px solid #E9ECEF;
    }
    
    /* Inputs limpios */
    .stTextInput>div>div>input {
        border: 1px solid #DEE2E6;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
    }
    
    .stSelectbox>div>div>div {
        border: 1px solid #DEE2E6;
        border-radius: 6px;
    }
    
    /* Info boxes minimalistas */
    .stAlert {
        border-radius: 6px;
        border: 1px solid;
        padding: 1rem;
    }
    
    /* Divisores sutiles */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #E9ECEF;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER PRINCIPAL
# ==========================================

col_header_logo, col_header_title = st.columns([1, 5])

with col_header_logo:
    st.markdown("### 🏥")

with col_header_title:
    st.markdown("# Tamizaje Genético")
    st.caption("Sistema de seguimiento de pacientes respiratorios")

st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)

# ==========================================
# CARGA DE DATOS
# ==========================================

# Intentar cargar desde backend
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_data():
    """Obtiene datos del backend con cache"""
    df = cargar_datos_backend()
    
    # Si no hay conexión backend, usar datos de sesión como fallback
    if df is None and 'df' in st.session_state:
        return st.session_state['df']
    
    return df

# Cargar datos
df = get_data()

# Si no hay datos, mostrar opción de carga manual (temporal)
if df is None:
    col_upload1, col_upload2 = st.columns([2, 1])
    
    with col_upload1:
        st.info("📊 **Modo de desarrollo**: Carga temporal de datos")
        uploaded_file = st.file_uploader(
            "Cargar archivo Excel",
            type=['xlsx', 'xls'],
            help="Esta opción es temporal. En producción, los datos vendrán del backend automáticamente."
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.session_state['df'] = df
                st.success("✅ Datos cargados correctamente")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col_upload2:
        st.markdown("""
        ### 🔧 Configuración Backend
        
        Para conectar al backend, edita la función `cargar_datos_backend()`:
        
        **PostgreSQL:**
        ```python
        import psycopg2
        conn = psycopg2.connect(...)
        ```
        
        **API REST:**
        ```python
        import requests
        response = requests.get(...)
        ```
        """)
    
    st.stop()

# ==========================================
# SIDEBAR - FILTROS
# ==========================================

st.sidebar.markdown("### 🔍 Filtros")

# Búsqueda rápida
busqueda = st.sidebar.text_input(
    "Buscar paciente",
    placeholder="Nombre o cédula...",
    label_visibility="collapsed"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Filtros principales
ciudad_options = ["Todas"] + sorted(df['CIUDAD'].dropna().unique().tolist())
ciudad_sel = st.sidebar.selectbox("Ciudad", ciudad_options, label_visibility="visible")

eps_options = ["Todas"] + sorted(df['EPS'].dropna().unique().tolist())
eps_sel = st.sidebar.selectbox("EPS", eps_options)

if 'ESTADO' in df.columns:
    estado_options = ["Todos"] + sorted(df['ESTADO'].dropna().unique().tolist())
    estado_sel = st.sidebar.selectbox("Estado", estado_options)
else:
    estado_sel = "Todos"

# Filtros clínicos
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("**Filtros Clínicos**")

if 'ANTECEDENTES TABAQUISMO' in df.columns:
    tabaquismo_sel = st.sidebar.radio(
        "Tabaquismo",
        ["Todos", "SI", "NO"],
        horizontal=True,
        label_visibility="visible"
    )
else:
    tabaquismo_sel = "Todos"

# Aplicar filtros
df_filtrado = df.copy()

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['NOMBRE'].str.contains(busqueda, case=False, na=False) |
        df_filtrado['CEDULA'].astype(str).str.contains(busqueda, case=False, na=False)
    ]

if ciudad_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['CIUDAD'] == ciudad_sel]

if eps_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['EPS'] == eps_sel]

if estado_sel != "Todos" and 'ESTADO' in df.columns:
    df_filtrado = df_filtrado[df_filtrado['ESTADO'] == estado_sel]

if tabaquismo_sel != "Todos" and 'ANTECEDENTES TABAQUISMO' in df.columns:
    df_filtrado = df_filtrado[df_filtrado['ANTECEDENTES TABAQUISMO'] == tabaquismo_sel]

# Botón limpiar
if st.sidebar.button("🔄 Limpiar filtros", use_container_width=True):
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.caption(f"📊 {len(df_filtrado)} de {len(df)} pacientes")

# ==========================================
# KPIs PRINCIPALES
# ==========================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Pacientes", len(df_filtrado))

with col2:
    tomadas = len(df_filtrado[df_filtrado['FECHA TOMA MUESTRA'].notna()]) if 'FECHA TOMA MUESTRA' in df_filtrado.columns else 0
    porc = (tomadas / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
    st.metric("Muestras Tomadas", tomadas, f"{porc:.0f}%")

with col3:
    enviadas = 0
    if 'MUESTRA ENVIADA A ESPAÑA' in df_filtrado.columns:
        enviadas = len(df_filtrado[df_filtrado['MUESTRA ENVIADA A ESPAÑA'].isin(['SI', 'SÍ', 'Si', 'si'])])
    st.metric("Enviadas", enviadas)

with col4:
    completados = 0
    if 'RESULTADOS ENVIADOS' in df_filtrado.columns:
        completados = len(df_filtrado[df_filtrado['RESULTADOS ENVIADOS'].isin(['SI', 'SÍ', 'Si', 'si'])])
    st.metric("Completados", completados)

with col5:
    if 'ANTECEDENTES TABAQUISMO' in df_filtrado.columns:
        fumadores = len(df_filtrado[df_filtrado['ANTECEDENTES TABAQUISMO'] == 'SI'])
        st.metric("Tabaquismo", fumadores)
    else:
        st.metric("Registros", len(df_filtrado))

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# LAYOUT PRINCIPAL
# ==========================================

col_lista, col_detalle = st.columns([1, 2.5])

# Lista de pacientes
with col_lista:
    st.markdown("### Pacientes")
    
    df_sorted = df_filtrado.sort_values('FECHA REGISTRO', ascending=False) if 'FECHA REGISTRO' in df_filtrado.columns else df_filtrado
    
    for idx, row in df_sorted.head(50).iterrows():
        estado = row.get('ESTADO', 'Sin estado')
        
        if estado == 'Completado':
            estado_emoji = "✅"
        elif 'Proceso' in str(estado):
            estado_emoji = "🔄"
        else:
            estado_emoji = "⏳"
        
        if st.button(
            f"{estado_emoji} {row['NOMBRE'][:30]}...\n📋 {row['CEDULA']}",
            key=f"btn_{idx}",
            use_container_width=True
        ):
            st.session_state['paciente_sel'] = row.to_dict()

# Detalle del paciente
with col_detalle:
    if 'paciente_sel' in st.session_state:
        p = st.session_state['paciente_sel']
        
        # Header
        col_h1, col_h2 = st.columns([3, 1])
        
        with col_h1:
            st.markdown(f"## {p['NOMBRE']}")
            st.caption(f"CC: {p['CEDULA']} • {p.get('CIUDAD', 'N/A')}")
        
        with col_h2:
            estado = p.get('ESTADO', 'Sin estado')
            if estado == 'Completado':
                st.success("✅ Completado")
            elif 'Proceso' in str(estado):
                st.info("🔄 En proceso")
            else:
                st.warning("⏳ Pendiente")
        
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📋 General", "🫁 Respiratorio", "📅 Timeline"])
        
        with tab1:
            col_g1, col_g2, col_g3 = st.columns(3)
            
            with col_g1:
                st.markdown("**Datos Personales**")
                st.caption(f"Edad: {p.get('EDAD', 'N/A')} años")
                st.caption(f"Género: {p.get('GÉNERO', 'N/A')}")
                st.caption(f"EPS: {p.get('EPS', 'N/A')}")
            
            with col_g2:
                st.markdown("**Diagnóstico**")
                st.caption(p.get('DIAGNOSTICO PRIMARIO', 'N/A')[:50])
                st.caption(f"Médico: {p.get('NOMBRE MÉDICO', 'N/A')}")
            
            with col_g3:
                st.markdown("**Ubicación**")
                st.caption(f"Ciudad: {p.get('CIUDAD', 'N/A')}")
                st.caption(f"Depto: {p.get('DEPARTAMENTO', 'N/A')}")
        
        with tab2:
            st.markdown("**Síntomas Respiratorios**")
            
            sintomas = [
                ("Tabaquismo", "ANTECEDENTES TABAQUISMO"),
                ("Dif. con Ejercicio", "DIFICULTAD RESPIRATORIA CON EL EJERCICI0"),
                ("Tos Crónica", "TOS MAS DE 3 MESES AL AÑO"),
                ("Sibilancias", "SIBILANCIAS")
            ]
            
            cols = st.columns(2)
            for idx, (nombre, campo) in enumerate(sintomas):
                valor = p.get(campo, 'N/A')
                with cols[idx % 2]:
                    if valor in ['SI', 'SÍ', 'Si', 'si']:
                        st.error(f"❌ {nombre}")
                    elif valor in ['NO', 'No', 'no']:
                        st.success(f"✅ {nombre}")
                    else:
                        st.caption(f"⚪ {nombre}: {valor}")
        
        with tab3:
            st.markdown("**Proceso**")
            
            fases = [
                ("Registro", p.get('FECHA REGISTRO')),
                ("Toma Muestra", p.get('FECHA TOMA MUESTRA')),
                ("Envío España", p.get('FECHA ENVIO MUESTRAS A ESPAÑA')),
                ("Resultados", p.get('FECHA DE RECIBIDO'))
            ]
            
            for nombre, fecha in fases:
                if pd.notna(fecha) and str(fecha) not in ['', 'N/A', 'nan']:
                    st.success(f"✅ {nombre}: {fecha}")
                else:
                    st.caption(f"⏳ {nombre}: Pendiente")
    
    else:
        st.markdown("## 👈 Selecciona un paciente")
        st.caption("Haz clic en un paciente de la lista para ver su información")
        
        # Preview de datos
        st.markdown("### Vista previa")
        st.dataframe(
            df_filtrado[['NOMBRE', 'CEDULA', 'CIUDAD', 'EPS']].head(10),
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# GRÁFICOS
# ==========================================

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("## Análisis")

tab_geo, tab_proceso = st.tabs(["🌍 Distribución", "📊 Progreso"])

with tab_geo:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        if 'CIUDAD' in df_filtrado.columns:
            ciudad_counts = df_filtrado['CIUDAD'].value_counts().head(10)
            fig = px.bar(
                x=ciudad_counts.values,
                y=ciudad_counts.index,
                orientation='h',
                title='Pacientes por Ciudad',
                color=ciudad_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2E5266'),
                xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col_g2:
        if 'EPS' in df_filtrado.columns:
            eps_counts = df_filtrado['EPS'].value_counts().head(8)
            fig = px.pie(
                values=eps_counts.values,
                names=eps_counts.index,
                title='Distribución por EPS',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2E5266')
            )
            st.plotly_chart(fig, use_container_width=True)

with tab_proceso:
    fases = ['Registrados', 'Muestra Tomada', 'Enviadas', 'Resultados', 'Completados']
    valores = [
        len(df_filtrado),
        len(df_filtrado[df_filtrado['FECHA TOMA MUESTRA'].notna()]) if 'FECHA TOMA MUESTRA' in df_filtrado.columns else 0,
        len(df_filtrado[df_filtrado['MUESTRA ENVIADA A ESPAÑA'] == 'SI']) if 'MUESTRA ENVIADA A ESPAÑA' in df_filtrado.columns else 0,
        len(df_filtrado[df_filtrado['FECHA DE RECIBIDO'].notna()]) if 'FECHA DE RECIBIDO' in df_filtrado.columns else 0,
        len(df_filtrado[df_filtrado['RESULTADOS ENVIADOS'] == 'SI']) if 'RESULTADOS ENVIADOS' in df_filtrado.columns else 0
    ]
    
    fig = go.Figure(go.Funnel(
        y=fases,
        x=valores,
        textinfo="value+percent initial",
        marker=dict(color=['#2E5266', '#447189', '#5A8FAC', '#70ADCF', '#86CBF2'])
    ))
    fig.update_layout(
        title='Embudo del Proceso',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2E5266')
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# FOOTER
# ==========================================

st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
st.caption(f"🏥 Sistema de Tamizaje Genético • Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")