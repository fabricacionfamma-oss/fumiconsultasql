import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Diagnóstico SQL - Fumiscor", layout="wide", page_icon="🔍")

st.title("🔍 Explorador de Datos Crudos (SQL)")
st.write("""
Esta herramienta consulta directamente las tablas de la base de datos `wii_bi`. 
No aplica filtros de diccionario ni JOINs para que puedas ver exactamente qué está guardado.
""")

# ==========================================
# INTERFAZ DE SELECCIÓN
# ==========================================
col1, col2 = st.columns([1, 3])

with col1:
    # Por defecto, ponemos la fecha que queremos investigar
    fecha_consulta = st.date_input("Selecciona la fecha:", value=pd.to_datetime("2026-04-01"))
    
    # Preparamos las variables de fecha para esquivar el problema del DATETIME
    fecha_str = fecha_consulta.strftime('%Y-%m-%d')
    fecha_fin = (fecha_consulta + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

with col2:
    st.info(f"""
    **Consulta que se enviará:**
    `WHERE Date >= '{fecha_str}' AND Date < '{fecha_fin}'`
    (Esto asegura que traiga cualquier registro que haya ocurrido a cualquier hora dentro de ese día).
    """)

st.divider()

# ==========================================
# MOTOR DE CONSULTA
# ==========================================
if st.button("Consultar Base de Datos", type="primary"):
    with st.spinner("Conectando a SQL Server..."):
        try:
            conn = st.connection("wii_bi", type="sql")
            
            # --- 1. Tabla de Producción ---
            st.subheader(f"1. Producción Diaria (Tabla: PROD_D_01)")
            q_prod = f"""
                SELECT TOP 100 *
                FROM PROD_D_01
                WHERE Date >= '{fecha_str}' AND Date < '{fecha_fin}'
            """
            df_prod = conn.query(q_prod)
            
            if df_prod.empty:
                st.warning(f"⚠️ La consulta devolvió 0 filas. Físicamente no hay producción registrada para el {fecha_str}.")
            else:
                st.success(f"✅ Se encontraron registros. Mostrando los primeros {len(df_prod)}.")
                st.dataframe(df_prod, use_container_width=True)

            # --- 2. Tabla de OEE / Métricas ---
            st.subheader(f"2. Métricas OEE (Tabla: PROD_D_03)")
            q_metrics = f"""
                SELECT TOP 100 *
                FROM PROD_D_03
                WHERE Date >= '{fecha_str}' AND Date < '{fecha_fin}'
            """
            df_metrics = conn.query(q_metrics)
            
            if df_metrics.empty:
                st.warning(f"⚠️ No hay métricas OEE calculadas para el {fecha_str}.")
            else:
                st.success(f"✅ Se encontraron registros. Mostrando los primeros {len(df_metrics)}.")
                st.dataframe(df_metrics, use_container_width=True)

            # --- 3. Tabla de Eventos ---
            st.subheader(f"3. Eventos y Paradas (Tabla: EVENT_01)")
            q_events = f"""
                SELECT TOP 100 *
                FROM EVENT_01
                WHERE Date >= '{fecha_str}' AND Date < '{fecha_fin}'
            """
            df_events = conn.query(q_events)
            
            if df_events.empty:
                st.warning(f"⚠️ No hay eventos ni paradas registradas para el {fecha_str}.")
            else:
                st.success(f"✅ Se encontraron registros. Mostrando los primeros {len(df_events)}.")
                st.dataframe(df_events, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error crítico de conexión o consulta SQL: {e}")
