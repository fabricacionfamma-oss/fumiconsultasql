import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inspector SQL - FAMMA", layout="wide", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Inspector de Tablas - Base de Datos FAMMA")
st.write("Usa esta herramienta para comprobar si las tablas realmente tienen datos en el mes seleccionado y si los nombres de las máquinas coinciden.")

col1, col2 = st.columns(2)
with col1:
    mes = st.number_input("Mes a consultar:", min_value=1, max_value=12, value=3)
with col2:
    anio = st.number_input("Año a consultar:", min_value=2023, max_value=2030, value=2026)

if st.button("🔍 Ejecutar Rayos X en la Base de Datos", type="primary"):
    with st.spinner("Conectando con FAMMA y escaneando tablas..."):
        try:
            conn = st.connection("wii_bi", type="sql")

            # 1. REVISAR NOMBRES EXACTOS DE LAS MÁQUINAS
            st.markdown("### 1. Catálogo de Máquinas (Tabla `CELL`)")
            st.info("💡 Fíjate en la columna 'Name'. Así es EXACTAMENTE como deben escribirse en nuestro diccionario de Python. ¡Cuidado con espacios al final o al principio!")
            df_cell = conn.query("SELECT CellId, Name FROM CELL ORDER BY Name")
            st.dataframe(df_cell, use_container_width=True)

            # 2. REVISAR TABLAS MENSUALES (KPIs)
            st.markdown("### 2. Tabla Mensual de OEE (Tabla `PROD_M_03`)")
            df_m03 = conn.query(f"SELECT TOP 100 * FROM PROD_M_03 WHERE Year = {anio} AND Month = {mes}")
            if df_m03.empty:
                st.error(f"❌ VACÍA. No hay datos consolidados mensuales para {mes}/{anio}.")
            else:
                st.success(f"✅ CON DATOS. Mostrando registros de {mes}/{anio}:")
                st.dataframe(df_m03, use_container_width=True)

            # 3. REVISAR TABLAS MENSUALES (PIEZAS)
            st.markdown("### 3. Tabla Mensual de Piezas (Tabla `PROD_M_01`)")
            df_m01 = conn.query(f"SELECT TOP 100 * FROM PROD_M_01 WHERE Year = {anio} AND Month = {mes}")
            if df_m01.empty:
                st.error(f"❌ VACÍA. No hay conteo de piezas mensuales para {mes}/{anio}.")
            else:
                st.success(f"✅ CON DATOS. Mostrando registros de {mes}/{anio}:")
                st.dataframe(df_m01, use_container_width=True)

            # 4. REVISAR TABLAS DIARIAS (KPIs)
            st.markdown("### 4. Tabla Diaria de OEE (Tabla `PROD_D_03`)")
            df_d03 = conn.query(f"SELECT TOP 100 * FROM PROD_D_03 WHERE YEAR(Date) = {anio} AND MONTH(Date) = {mes}")
            if df_d03.empty:
                st.error(f"❌ VACÍA. Tampoco hay datos diarios procesados en este mes.")
            else:
                st.success(f"✅ CON DATOS. Mostrando registros diarios de {mes}/{anio}:")
                st.dataframe(df_d03, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
