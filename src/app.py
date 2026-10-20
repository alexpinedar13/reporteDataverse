import streamlit as st
import os
import pandas as pd
from datetime import datetime
import requests

from modules.dataverse_exporter import get_dataverse_report
from modules.dataset_exporter import get_dataset_report
from modules.file_exporter import get_file_report

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Generador de Informes Dataverse",
    page_icon="📊",
    layout="wide"
)

# --- ESTILOS INSTITUCIONALES ---
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #003366; }
    .sub-header { font-size: 14px; color: #555555; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Gestor de Reportes Consolidados - Dataverse")
st.markdown("Herramienta de extracción de metadatos para acreditación e informes institucionales.")

st.divider()

# --- PANEL DE CONFIGURACIÓN DE PARÁMETROS ---
col1, col2 = st.columns(2)

with col1:
    base_url = st.text_input("URL Instancia Dataverse", value="https://research-data.urosario.edu.co")
    
with col2:
    #api_token = st.text_input("Dataverse API Key (Superuser Token)", value="92979613-0616-4b5e-893f-c3315b5078bc", type="password")
    api_token = st.text_input("Dataverse API Key (Superuser Token)", type="password")

headers = {"X-Dataverse-key": api_token}

# --- FUNCIONES AUXILIARES ---
def fetch_search_items(entity_type, progress_bar):
    items = []
    start = 0
    per_page = 100
    
    while True:
        url = f"{base_url}/api/search?q=*&type={entity_type}&per_page={per_page}&start={start}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            st.error(f"Error consultando {entity_type} (HTTP {res.status_code})")
            break
            
        data = res.json().get('data', {})
        total_count = data.get('total_count', 0)
        fetched_items = data.get('items', [])
        
        items.extend(fetched_items)
        start += per_page
        
        if total_count > 0:
            progress_bar.progress(min(start / total_count, 1.0), text=f"Extrayendo {entity_type} ({len(items)} de {total_count})...")
            
        if start >= total_count or not fetched_items:
            break
            
    return items

# --- BOTÓN DE EJECUCIÓN ---
st.subheader("Generación de Informe")

if st.button("🚀 Iniciar Extracción de Metadatos", type="primary"):
    if not api_token:
        st.warning("Debe proporcionar un API Token válido.")
    else:
        try:
            status_area = st.empty()
            progress_bar = st.progress(0)
            
            status_area.info("Iniciando conexión con la API de Dataverse...")
            
            # 1. Extracción de Dataverses
            dv_items = fetch_search_items("dataverse", progress_bar)
            status_area.info(f"Dataverses detectados: {len(dv_items)}. Extrayendo Datasets...")
            
            # 2. Extracción de Datasets
            ds_items = fetch_search_items("dataset", progress_bar)
            status_area.info(f"Datasets detectados: {len(ds_items)}. Procesando metadatos estructurados...")
            
            # 3. Procesamiento Módulos
            with st.spinner("Procesando roles de Dataverses, autores y detalles de archivos..."):
                df_dv = pd.DataFrame(get_dataverse_report(base_url, headers, dv_items))
                df_ds = pd.DataFrame(get_dataset_report(base_url, headers, ds_items))
                df_files = pd.DataFrame(get_file_report(base_url, headers, ds_items))

            # 4. Generación de Excel en memoria
            fecha_str = datetime.now().strftime("%d-%m-%Y_%H%M")
            file_name = f"Informe_Consolidado_Dataverse_{fecha_str}.xlsx"
            output_dir = "./Informes"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, file_name)

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_dv.to_excel(writer, sheet_name='Dataverses', index=False)
                df_ds.to_excel(writer, sheet_name='Datasets', index=False)
                df_files.to_excel(writer, sheet_name='Archivos', index=False)

            progress_bar.progress(1.0, text="¡Extracción completada!")
            status_area.success("El informe ha sido generado exitosamente.")

            st.divider()

            # --- VISTA PREVIA Y MÉTRICAS CLAVE ---
            st.subheader("Métricas de la Extracción")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Dataverses", len(df_dv))
            m2.metric("Total Datasets", len(df_ds))
            m3.metric("Total Archivos", len(df_files))

            # --- BOTÓN DE DESCARGA DIRECTA ---
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥 Descargar Informe Consolidado (.xlsx)",
                    data=f,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # --- PESTAÑAS DE VISUALIZACIÓN PREVIA ---
            st.subheader("Vista Previa del Informe")
            tab1, tab2, tab3 = st.tabs(["Dataverses", "Datasets", "Archivos"])
            with tab1:
                st.dataframe(df_dv.head(20))
            with tab2:
                st.dataframe(df_ds.head(20))
            with tab3:
                st.dataframe(df_files.head(20))

        except Exception as e:
            st.error(f"Ocurrió un error en la extracción: {str(e)}")