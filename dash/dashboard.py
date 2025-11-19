import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Tamizaje Genético",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .stButton>button {width: 100%;}
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("🧬 Dashboard de Tamizaje Genético")
st.markdown("### Seguimiento de Pacientes - Análisis Respiratorio")
st.markdown("---")

# Subir archivo
uploaded_file = st.file_uploader(
    "📤 Cargar archivo Excel con datos de pacientes",
    type=['xlsx', 'xls'],
    help="Sube tu archivo Excel con la información de los pacientes"
)

if uploaded_file is not None:
    try:
        # Leer el archivo
        df = pd.read_excel(uploaded_file)
        
        # Guardar en session_state
        if 'df' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
            st.session_state['df'] = df
            st.session_state['file_name'] = uploaded_file.name
        
        df = st.session_state['df']
        
        # === SIDEBAR - FILTROS ===
        st.sidebar.header("🔍 Filtros de Búsqueda")
        
        # Buscar por nombre o cédula
        busqueda = st.sidebar.text_input(
            "🔎 Buscar paciente",
            placeholder="Nombre o cédula..."
        )
        
        # Filtros principales
        st.sidebar.markdown("### 📊 Filtros Generales")
        
        ciudades = ["Todas"] + sorted(df['CIUDAD'].dropna().unique().tolist())
        ciudad_sel = st.sidebar.selectbox("🏙️ Ciudad", ciudades)
        
        eps_list = ["Todas"] + sorted(df['EPS'].dropna().unique().tolist())
        eps_sel = st.sidebar.selectbox("🏥 EPS", eps_list)
        
        if 'ESTADO' in df.columns:
            estados = ["Todos"] + sorted(df['ESTADO'].dropna().unique().tolist())
            estado_sel = st.sidebar.selectbox("📊 Estado", estados)
        else:
            estado_sel = "Todos"
        
        if 'MES' in df.columns:
            meses = ["Todos"] + sorted(df['MES'].dropna().unique().tolist())
            mes_sel = st.sidebar.selectbox("📅 Mes", meses)
        else:
            mes_sel = "Todos"
        
        # Filtros clínicos
        st.sidebar.markdown("### 🩺 Filtros Clínicos")
        
        if 'ANTECEDENTES TABAQUISMO' in df.columns:
            tabaquismo_options = ["Todos", "SI", "NO"]
            tabaquismo_sel = st.sidebar.selectbox("🚬 Tabaquismo", tabaquismo_options)
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
        
        if mes_sel != "Todos" and 'MES' in df.columns:
            df_filtrado = df_filtrado[df_filtrado['MES'] == mes_sel]
        
        if tabaquismo_sel != "Todos" and 'ANTECEDENTES TABAQUISMO' in df.columns:
            df_filtrado = df_filtrado[df_filtrado['ANTECEDENTES TABAQUISMO'] == tabaquismo_sel]
        
        # Botón para limpiar filtros
        if st.sidebar.button("🔄 Limpiar Filtros"):
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.info(f"**📊 Mostrando:** {len(df_filtrado)} de {len(df)} pacientes")
        
        # === KPIs PRINCIPALES ===
        st.markdown("## 📊 Indicadores Clave")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="👥 Total Pacientes",
                value=len(df_filtrado),
                delta=f"{len(df_filtrado)}/{len(df)}"
            )
        
        with col2:
            tomadas = len(df_filtrado[df_filtrado['FECHA TOMA MUESTRA'].notna()]) if 'FECHA TOMA MUESTRA' in df_filtrado.columns else 0
            porcentaje_tomadas = (tomadas / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
            st.metric(
                label="💉 Muestras Tomadas",
                value=tomadas,
                delta=f"{porcentaje_tomadas:.0f}%"
            )
        
        with col3:
            enviadas = 0
            if 'MUESTRA ENVIADA A ESPAÑA' in df_filtrado.columns:
                enviadas = len(df_filtrado[
                    df_filtrado['MUESTRA ENVIADA A ESPAÑA'].isin(['SI', 'SÍ', 'Si', 'si', 'YES', 'Yes'])
                ])
            st.metric(
                label="✈️ Enviadas a España",
                value=enviadas
            )
        
        with col4:
            completados = 0
            if 'RESULTADOS ENVIADOS' in df_filtrado.columns:
                completados = len(df_filtrado[
                    df_filtrado['RESULTADOS ENVIADOS'].isin(['SI', 'SÍ', 'Si', 'si', 'YES', 'Yes'])
                ])
            st.metric(
                label="✅ Completados",
                value=completados
            )
        
        with col5:
            if 'ANTECEDENTES TABAQUISMO' in df_filtrado.columns:
                fumadores = len(df_filtrado[df_filtrado['ANTECEDENTES TABAQUISMO'] == 'SI'])
                st.metric(
                    label="🚬 Tabaquismo",
                    value=fumadores
                )
            else:
                st.metric(label="📋 Registros", value=len(df_filtrado))
        
        st.markdown("---")
        
        # === LAYOUT PRINCIPAL ===
        col_lista, col_detalle = st.columns([1, 2.5])
        
        # === LISTA DE PACIENTES ===
        with col_lista:
            st.subheader(f"📋 Pacientes ({len(df_filtrado)})")
            
            # Ordenar por fecha de registro
            df_sorted = df_filtrado.sort_values('FECHA REGISTRO', ascending=False) if 'FECHA REGISTRO' in df_filtrado.columns else df_filtrado
            
            # Crear contenedor scrolleable
            with st.container():
                for idx, row in df_sorted.iterrows():
                    # Determinar color según estado
                    estado = row.get('ESTADO', 'Sin estado')
                    if estado == 'Completado':
                        estado_emoji = "🟢"
                    elif 'Proceso' in str(estado):
                        estado_emoji = "🟡"
                    else:
                        estado_emoji = "⚪"
                    
                    # Botón de paciente
                    if st.button(
                        f"{estado_emoji} **{row['NOMBRE'][:35]}...**\n📋 CC: {row['CEDULA']} | 🏙️ {row.get('CIUDAD', 'N/A')}",
                        key=f"patient_{idx}",
                        use_container_width=True
                    ):
                        st.session_state['paciente_seleccionado'] = row.to_dict()
        
        # === DETALLE DEL PACIENTE ===
        with col_detalle:
            if 'paciente_seleccionado' in st.session_state:
                paciente = st.session_state['paciente_seleccionado']
                
                # Header del paciente
                col_header1, col_header2 = st.columns([3, 1])
                
                with col_header1:
                    st.markdown(f"# 👤 {paciente['NOMBRE']}")
                    st.markdown(f"**📋 Cédula:** {paciente['CEDULA']}")
                
                with col_header2:
                    # Estado con color
                    estado = paciente.get('ESTADO', 'Sin estado')
                    if estado == 'Completado':
                        st.success(f"✅ {estado}")
                    elif 'Proceso' in str(estado):
                        st.info(f"🔄 {estado}")
                    else:
                        st.warning(f"⏳ {estado}")
                
                st.markdown("---")
                
                # Información básica en cards
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.markdown("### 📍 Ubicación")
                    st.markdown(f"**Ciudad:** {paciente.get('CIUDAD', 'N/A')}")
                    st.markdown(f"**Departamento:** {paciente.get('DEPARTAMENTO', 'N/A')}")
                    st.markdown(f"**Zona:** {paciente.get('ZONA', 'N/A')}")
                
                with col_info2:
                    st.markdown("### 👤 Personal")
                    st.markdown(f"**Edad:** {paciente.get('EDAD', 'N/A')} años")
                    st.markdown(f"**Género:** {paciente.get('GÉNERO', 'N/A')}")
                    st.markdown(f"**Rango:** {paciente.get('RANGO DE EDAD', 'N/A')}")
                
                with col_info3:
                    st.markdown("### 🏥 Aseguradora")
                    st.markdown(f"**EPS:** {paciente.get('EPS', 'N/A')}")
                    st.markdown(f"**Sede:** {paciente.get('SEDES', 'N/A')}")
                
                st.markdown("---")
                
                # Tabs con información detallada
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🩺 Clínica", 
                    "🫁 Síntomas Respiratorios", 
                    "📅 Timeline", 
                    "👥 Administrativa",
                    "📝 Observaciones"
                ])
                
                # TAB 1: INFORMACIÓN CLÍNICA
                with tab1:
                    col_clin1, col_clin2 = st.columns(2)
                    
                    with col_clin1:
                        st.markdown("### 🩺 Diagnóstico")
                        diag_primario = paciente.get('DIAGNOSTICO PRIMARIO', 'N/A')
                        st.info(diag_primario)
                        
                        st.markdown("**Diagnóstico CIE:**")
                        st.write(paciente.get('DIAGNOSTICO', 'N/A'))
                        
                        st.markdown("### 👨‍⚕️ Médico Tratante")
                        st.write(paciente.get('NOMBRE MÉDICO', 'N/A'))
                    
                    with col_clin2:
                        st.markdown("### 🏥 Institución")
                        st.write(f"**IPS/Instituto:** {paciente.get('IPS/INSTITUTO QUE REMITE', 'N/A')}")
                        st.write(f"**Lugar de Toma:** {paciente.get('MD ORDENA/LUGAR DE TOMA', 'N/A')}")
                        
                        st.markdown("### 🔬 Código Progenika")
                        codigo = paciente.get('CODIGO PROGENIKA', 'N/A')
                        if codigo and codigo != 'N/A':
                            st.code(codigo)
                        else:
                            st.write("Pendiente de asignación")
                
                # TAB 2: SÍNTOMAS RESPIRATORIOS
                with tab2:
                    st.markdown("### 🫁 Evaluación de Síntomas Respiratorios")
                    
                    sintomas = [
                        ("🚬", "Antecedentes de Tabaquismo", "ANTECEDENTES TABAQUISMO"),
                        ("🏃", "Dificultad Respiratoria con Ejercicio", "DIFICULTAD RESPIRATORIA CON EL EJERCICI0"),
                        ("😮‍💨", "Episodios de Dificultad en Reposo", "EPISODIOS DIFICULTAD RESPIRATORIA EN REPOSO"),
                        ("🤧", "Tos (>3 meses/año)", "TOS MAS DE 3 MESES AL AÑO"),
                        ("💧", "Expectoración", "EXPECTORACIÓN"),
                        ("🌬️", "Sibilancias", "SIBILANCIAS")
                    ]
                    
                    col_sint1, col_sint2 = st.columns(2)
                    
                    for idx, (emoji, nombre, campo) in enumerate(sintomas):
                        valor = paciente.get(campo, 'N/A')
                        
                        target_col = col_sint1 if idx % 2 == 0 else col_sint2
                        
                        with target_col:
                            if valor in ['SI', 'SÍ', 'Si', 'si', 'YES', 'Yes']:
                                st.error(f"{emoji} **{nombre}:** ✅ SI")
                            elif valor in ['NO', 'No', 'no']:
                                st.success(f"{emoji} **{nombre}:** ❌ NO")
                            else:
                                st.info(f"{emoji} **{nombre}:** ⚪ {valor}")
                
                # TAB 3: TIMELINE
                with tab3:
                    st.markdown("### 📅 Timeline del Proceso")
                    
                    fases = [
                        ("📝", "Registro", paciente.get('FECHA REGISTRO'), None),
                        ("💉", "Toma de Muestra", paciente.get('FECHA TOMA MUESTRA'), paciente.get('QUIEN TOMO LA MUESTRA')),
                        ("✈️", "Enviada a España", paciente.get('FECHA ENVIO MUESTRAS A ESPAÑA'), None),
                        ("📥", "Resultados Recibidos", paciente.get('FECHA DE RECIBIDO'), None),
                        ("📧", "Resultados Enviados", 
                         "✅ Completado" if paciente.get('RESULTADOS ENVIADOS') in ['SI', 'SÍ', 'Si'] else "⏳ Pendiente", 
                         None)
                    ]
                    
                    for icono, fase, fecha, extra_info in fases:
                        col_time1, col_time2 = st.columns([3, 1])
                        
                        with col_time1:
                            if pd.notna(fecha) and str(fecha) not in ['', 'N/A', 'nan', 'Pendiente', '⏳ Pendiente']:
                                st.success(f"{icono} **{fase}**")
                                st.caption(f"📅 {fecha}")
                                if extra_info:
                                    st.caption(f"👤 {extra_info}")
                            else:
                                st.warning(f"{icono} **{fase}**")
                                st.caption("⏳ Pendiente")
                    
                    # Info adicional
                    if paciente.get('MES DE TOMA'):
                        st.info(f"📆 **Mes de Toma:** {paciente['MES DE TOMA']}")
                    
                    if paciente.get('ORDEN X MES'):
                        st.info(f"🔢 **Orden del Mes:** {paciente['ORDEN X MES']}")
                
                # TAB 4: ADMINISTRATIVA
                with tab4:
                    col_admin1, col_admin2 = st.columns(2)
                    
                    with col_admin1:
                        st.markdown("### 👥 Equipo Responsable")
                        st.write(f"**Representante:** {paciente.get('REPRESENTANTE', 'N/A')}")
                        st.write(f"**Reportante:** {paciente.get('REPORTANTE 1', 'N/A')}")
                        st.write(f"**Quien tomó muestra:** {paciente.get('QUIEN TOMO LA MUESTRA', 'N/A')}")
                    
                    with col_admin2:
                        st.markdown("### 📋 Información de Proceso")
                        st.write(f"**Mes:** {paciente.get('MES', 'N/A')}")
                        st.write(f"**Orden x Mes:** {paciente.get('ORDEN X MES', 'N/A')}")
                        
                        # Resultados corte
                        resultado_corte = paciente.get('RESULTADOS A CORTE 14 OCTUBRE JOHN', 'N/A')
                        if resultado_corte and resultado_corte != 'N/A':
                            st.info(f"**Resultado Corte:** {resultado_corte}")
                
                # TAB 5: OBSERVACIONES
                with tab5:
                    st.markdown("### 📝 Notas y Observaciones")
                    
                    obs_general = paciente.get('OBSERVACIONES', '')
                    obs_toma = paciente.get('OBSERVACIÓN DE TOMA', '')
                    
                    if obs_general and str(obs_general) not in ['', 'nan', 'N/A']:
                        st.warning("**📌 Observaciones Generales:**")
                        st.write(obs_general)
                        st.markdown("---")
                    
                    if obs_toma and str(obs_toma) not in ['', 'nan', 'N/A']:
                        st.info("**💉 Observación de Toma:**")
                        st.write(obs_toma)
                        st.markdown("---")
                    
                    if (not obs_general or str(obs_general) in ['', 'nan', 'N/A']) and \
                       (not obs_toma or str(obs_toma) in ['', 'nan', 'N/A']):
                        st.info("✅ Sin observaciones registradas")
                
            else:
                # Mensaje inicial
                st.markdown("## 👈 Selecciona un paciente")
                st.info("Haz clic en un paciente de la lista para ver su información detallada")
                
                # Mostrar preview de datos
                st.markdown("### 📊 Vista previa de datos cargados")
                st.dataframe(df_filtrado.head(10), use_container_width=True)
        
        # === ESTADÍSTICAS Y GRÁFICOS ===
        st.markdown("---")
        st.markdown("## 📊 Análisis Estadístico")
        
        tab_stats1, tab_stats2, tab_stats3 = st.tabs([
            "🏙️ Distribución Geográfica",
            "🩺 Análisis Clínico",
            "📈 Progreso del Proceso"
        ])
        
        with tab_stats1:
            col_geo1, col_geo2 = st.columns(2)
            
            with col_geo1:
                if 'CIUDAD' in df_filtrado.columns:
                    ciudad_counts = df_filtrado['CIUDAD'].value_counts().reset_index()
                    ciudad_counts.columns = ['Ciudad', 'Cantidad']
                    fig_ciudad = px.bar(
                        ciudad_counts,
                        x='Ciudad',
                        y='Cantidad',
                        title='📍 Pacientes por Ciudad',
                        color='Cantidad',
                        color_continuous_scale='Blues',
                        text='Cantidad'
                    )
                    fig_ciudad.update_traces(textposition='outside')
                    st.plotly_chart(fig_ciudad, use_container_width=True)
            
            with col_geo2:
                if 'EPS' in df_filtrado.columns:
                    eps_counts = df_filtrado['EPS'].value_counts().reset_index()
                    eps_counts.columns = ['EPS', 'Cantidad']
                    fig_eps = px.pie(
                        eps_counts,
                        values='Cantidad',
                        names='EPS',
                        title='🏥 Distribución por EPS',
                        hole=0.4
                    )
                    st.plotly_chart(fig_eps, use_container_width=True)
        
        with tab_stats2:
            col_clin1, col_clin2 = st.columns(2)
            
            with col_clin1:
                if 'ANTECEDENTES TABAQUISMO' in df_filtrado.columns:
                    tabaq_data = df_filtrado['ANTECEDENTES TABAQUISMO'].value_counts()
                    fig_tabaq = go.Figure(data=[
                        go.Bar(x=tabaq_data.index, y=tabaq_data.values, 
                               marker_color=['#FF6B6B', '#4ECDC4'])
                    ])
                    fig_tabaq.update_layout(title='🚬 Antecedentes de Tabaquismo')
                    st.plotly_chart(fig_tabaq, use_container_width=True)
            
            with col_clin2:
                # Gráfico de síntomas
                sintomas_cols = [
                    'DIFICULTAD RESPIRATORIA CON EL EJERCICI0',
                    'TOS MAS DE 3 MESES AL AÑO',
                    'SIBILANCIAS'
                ]
                
                sintomas_data = []
                for col in sintomas_cols:
                    if col in df_filtrado.columns:
                        count_si = len(df_filtrado[df_filtrado[col] == 'SI'])
                        sintomas_data.append({
                            'Síntoma': col.replace('DIFICULTAD RESPIRATORIA CON EL EJERCICI0', 'Dif. Respiratoria')
                                           .replace('TOS MAS DE 3 MESES AL AÑO', 'Tos Crónica')
                                           .replace('SIBILANCIAS', 'Sibilancias'),
                            'Cantidad': count_si
                        })
                
                if sintomas_data:
                    df_sintomas = pd.DataFrame(sintomas_data)
                    fig_sintomas = px.bar(
                        df_sintomas,
                        x='Síntoma',
                        y='Cantidad',
                        title='🫁 Prevalencia de Síntomas Respiratorios',
                        color='Cantidad',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_sintomas, use_container_width=True)
        
        with tab_stats3:
            # Embudo del proceso
            fases_nombres = ['Registrados', 'Muestra Tomada', 'Enviadas España', 'Resultados', 'Completados']
            fases_valores = [
                len(df_filtrado),
                len(df_filtrado[df_filtrado['FECHA TOMA MUESTRA'].notna()]) if 'FECHA TOMA MUESTRA' in df_filtrado.columns else 0,
                len(df_filtrado[df_filtrado['MUESTRA ENVIADA A ESPAÑA'] == 'SI']) if 'MUESTRA ENVIADA A ESPAÑA' in df_filtrado.columns else 0,
                len(df_filtrado[df_filtrado['FECHA DE RECIBIDO'].notna()]) if 'FECHA DE RECIBIDO' in df_filtrado.columns else 0,
                len(df_filtrado[df_filtrado['RESULTADOS ENVIADOS'] == 'SI']) if 'RESULTADOS ENVIADOS' in df_filtrado.columns else 0
            ]
            
            fig_funnel = go.Figure(go.Funnel(
                y=fases_nombres,
                x=fases_valores,
                textinfo="value+percent initial",
                marker={"color": ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]}
            ))
            fig_funnel.update_layout(title='📊 Embudo del Proceso de Tamizaje')
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        # === BOTONES DE DESCARGA ===
        st.markdown("---")
        st.markdown("## 📥 Exportar Datos")
        
        col_down1, col_down2, col_down3 = st.columns(3)
        
        with col_down1:
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Descargar Datos Filtrados (CSV)",
                data=csv,
                file_name=f'pacientes_filtrados_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
            )
        
        with col_down2:
            csv_all = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📋 Descargar Todos los Datos (CSV)",
                data=csv_all,
                file_name=f'pacientes_completo_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
            )
        
        with col_down3:
            # Excel filtrado
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, index=False, sheet_name='Pacientes')
            buffer.seek(0)
            
            st.download_button(
                label="📊 Descargar Filtrados (Excel)",
                data=buffer,
                file_name=f'pacientes_filtrados_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.exception(e)
        st.info("Por favor verifica que el archivo Excel contenga las columnas correctas.")

else:
    # === PANTALLA DE BIENVENIDA ===
    col_welcome1, col_welcome2 = st.columns([2, 1])
    
    with col_welcome1:
        st.markdown("""
        ## 👋 Bienvenido al Dashboard de Tamizaje Genético
        
        Este sistema te permite:
        
        ✅ **Cargar y visualizar** datos de pacientes desde Excel  
        ✅ **Filtrar** por ciudad, EPS, estado y síntomas clínicos  
        ✅ **Ver detalles completos** de cada paciente  
        ✅ **Analizar síntomas respiratorios** (tabaquismo, tos, sibilancias, etc.)  
        ✅ **Hacer seguimiento** del proceso completo (toma → España → resultados)  
        ✅ **Generar gráficos** estadísticos automáticamente  
        ✅ **Exportar reportes** en CSV y Excel  
        
        ### 📋 Columnas Esperadas:
        
        **Datos Personales:** NOMBRE, CEDULA, GÉNERO, EDAD, RANGO DE EDAD  
        **Ubicación:** CIUDAD, DEPARTAMENTO, ZONA  
        **Sistema de Salud:** EPS, IPS/INSTITUTO QUE REMITE, SEDES  
        **Diagnóstico:** DIAGNOSTICO PRIMARIO, DIAGNOSTICO, NOMBRE MÉDICO  
        **Síntomas Respiratorios:** ANTECEDENTES TABAQUISMO, DIFICULTAD RESPIRATORIA, TOS, SIBILANCIAS, etc.  
        **Proceso:** FECHA REGISTRO, FECHA TOMA MUESTRA, FECHA ENVIO ESPAÑA, RESULTADOS ENVIADOS  
        **Administrativo:** REPRESENTANTE, REPORTANTE 1, CODIGO PROGENIKA  
        **Otros:** OBSERVACIONES, OBSERVACIÓN DE TOMA  
        """)
    
    with col_welcome2:
        st.info("""
        ### 🚀 Inicio Rápido
        
        1. Prepara tu Excel
        2. Haz clic en "Browse files"
        3. ¡Explora tus datos!
        """)
        
        st.success("""
        ### 💡 Tip


### 💡 Tip
        
        Usa los filtros del sidebar para encontrar pacientes específicos rápidamente.
        """)
        
        st.warning("""
        ### ⚠️ Importante
        
        Asegúrate de que los nombres de las columnas en tu Excel coincidan exactamente con los esperados.
        """)

# === FOOTER ===
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🧬 Dashboard de Tamizaje Genético | Desarrollado con Streamlit</p>
        <p>📊 Versión 1.0 | 2025</p>
    </div>
""", unsafe_allow_html=True)