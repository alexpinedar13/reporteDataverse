from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from datetime import datetime
import requests
import pathlib

from modules.dataverse_exporter import get_dataverse_report
from modules.dataset_exporter import get_dataset_report
from modules.file_exporter import get_file_report

app = Flask(__name__)

def fetch_all_items(base_url, headers, entity_type):
    items = []
    start = 0
    per_page = 100
    while True:
        url = f"{base_url}/api/search?q=*&type={entity_type}&per_page={per_page}&start={start}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            break
        data = res.json().get('data', {})
        total_count = data.get('total_count', 0)
        fetched = data.get('items', [])
        items.extend(fetched)
        start += per_page
        if start >= total_count or not fetched:
            break
    return items

@app.route('/informes/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/informes/generar', methods=['POST'])
def generar():
    base_url = request.form.get('base_url')
    api_token = request.form.get('api_token')
    headers = {"X-Dataverse-key": api_token}

    try:
        # Extracción
        dv_items = fetch_all_items(base_url, headers, "dataverse")
        ds_items = fetch_all_items(base_url, headers, "dataset")

        df_dv = pd.DataFrame(get_dataverse_report(base_url, headers, dv_items))
        df_ds = pd.DataFrame(get_dataset_report(base_url, headers, ds_items))
        df_files = pd.DataFrame(get_file_report(base_url, headers, ds_items))

        # --- CORRECCIÓN DE RUTA ABSOLUTA CON PATHLIB ---
        # Obtiene la ruta absoluta de la raíz del proyecto (subiendo un nivel desde src/)
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        output_dir = BASE_DIR / "Informes"
        
        # Asegura la creación del directorio con permisos correctos
        output_dir.mkdir(parents=True, exist_ok=True)

        fecha_str = datetime.now().strftime("%d-%m-%Y_%H%M")
        file_name = f"Informe_Consolidado_Dataverse_{fecha_str}.xlsx"
        file_path = output_dir / file_name

        # Escritura del archivo Excel
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_dv.to_excel(writer, sheet_name='Dataverses', index=False)
            df_ds.to_excel(writer, sheet_name='Datasets', index=False)
            df_files.to_excel(writer, sheet_name='Archivos', index=False)

        return send_file(str(file_path), as_attachment=True)

    except Exception as e:
        return render_template('index.html', mensaje=f"Error durante la generación: {str(e)}")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)