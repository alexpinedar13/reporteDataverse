import os
import pandas as pd
from datetime import datetime
import requests

from modules.dataverse_exporter import get_dataverse_report
from modules.dataset_exporter import get_dataset_report
from modules.file_exporter import get_file_report

# --- CONFIGURACIÓN DE ENTORNO ---
#BASE_URL = "https://research-data.urosario.edu.co"
#API_TOKEN = "92979613-0616-4b5e-893f-c3315b5078bc"

BASE_URL = "http://10.194.194.27:8080" # Cambiar a la URL de producción si es externo
API_TOKEN = "36f279ef-f413-467c-9c7a-3e8bcf0cb691"

HEADERS = {"X-Dataverse-key": API_TOKEN}

def fetch_search_items(entity_type):
    """
    Realiza paginación sobre la API de Búsqueda para evitar límites de corte.
    """
    items = []
    start = 0
    per_page = 100
    
    while True:
        url = f"{BASE_URL}/api/search?q=*&type={entity_type}&per_page={per_page}&start={start}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"[X] Error en consulta de {entity_type} (HTTP {res.status_code})")
            break
            
        data = res.json().get('data', {})
        total_count = data.get('total_count', 0)
        fetched_items = data.get('items', [])
        
        items.extend(fetched_items)
        start += per_page
        
        if start >= total_count or not fetched_items:
            break
            
    return items

def main():
    fecha_str = datetime.now().strftime("%d-%m-%Y_%H%M")
    output_dir = "./Informes"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"Informe_Consolidado_Dataverse_{fecha_str}.xlsx")

    print(f"[*] Conectando a {BASE_URL}...")
    
    # 1. Búsqueda explícita de TODOS los Dataverses (incluidos vacíos)
    dv_items = fetch_search_items("dataverse")
    print(f"[*] Total de Dataverses detectados en el índice: {len(dv_items)}")

    # 2. Búsqueda de Datasets para el reporte de Datasets y Archivos
    ds_items = fetch_search_items("dataset")
    print(f"[*] Total de Datasets detectados en el índice: {len(ds_items)}")

    # 3. Invocar módulos enviando sus respectivas listas de items
    df_dv = pd.DataFrame(get_dataverse_report(BASE_URL, HEADERS, dv_items))
    df_ds = pd.DataFrame(get_dataset_report(BASE_URL, HEADERS, ds_items))
    df_files = pd.DataFrame(get_file_report(BASE_URL, HEADERS, ds_items))


    # 4. Generar libro de Excel consolidado
    print(f"[*] Generando archivo Excel consolidado en: {file_path}")
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df_dv.to_excel(writer, sheet_name='Dataverses', index=False)
        df_ds.to_excel(writer, sheet_name='Datasets', index=False)
        df_files.to_excel(writer, sheet_name='Archivos', index=False)

    print("\n" + "="*60)
    print("RESUMEN EJECUTIVO EXTRAÍDO EXITOSAMENTE")
    print("="*60)
    print(f" Total Dataverses procesados: {len(df_dv)}")
    print(f" Total Datasets procesados:   {len(df_ds)}")
    print(f" Total Archivos registrados:  {len(df_files)}")
    print("="*60)

if __name__ == "__main__":
    main()