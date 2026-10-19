import requests
import pandas as pd
import time
import os
from datetime import datetime
fecha = datetime.now().strftime("%d-%m-%Y")
#archivo = f'/opt/script/informes/informe_avanzado{fecha}.csv'
os.makedirs("./Informes", exist_ok=True)
archivo = f'./Informes/informe_avanzado{fecha}.csv'
#BASE_URL = "http://localhost:8080" # Sin barra diagonal al final
#BASE_URL = "http://10.194.194.27:8080" # Cambiar a la URL de producción si es externo
BASE_URL = "https://research-data.urosario.edu.co"
API_TOKEN = "92979613-0616-4b5e-893f-c3315b5078bc"
HEADERS = {"X-Dataverse-key": API_TOKEN}

# 1. Obtener la lista base desde Search API (ej. tus 300 datasets)
search_url = f"{BASE_URL}/api/search?q=*&type=dataset&per_page=300"
search_response = requests.get(search_url, headers=HEADERS).json()
items = search_response.get('data', {}).get('items', [])
full_report = []
print(f"Procesando {len(items)} datasets de forma profunda...")

for item in items:
    pid = item.get("global_id")
    dv_alias = item.get("identifier_of_dataverse")
    statusPublicaDataset = item.get("publicationStatuses", [])[0]
    statusVersion = item.get("versionState", '')


    # 2. Consultar el detalle del Dataset para extraer Autores completos y Academic Unit
    ds_url = f"{BASE_URL}/api/datasets/:persistentId/?persistentId={pid}"
    try:
        ds_data = requests.get(ds_url, headers=HEADERS).json()
        #print (ds_data)
        # Navegar al bloque de citación estructurado
        latest_version = ds_data['data']['latestVersion']
        metadata_blocks = latest_version['metadataBlocks']['Urcitation']['fields']
        
        # Extracción de Autores con su ORCID/DOI y Affiliation
        authors_list = []
        author_field = next((f for f in metadata_blocks if f['typeName'] == 'author'), None)
        #print (author_field)
        if author_field:
            for auth in author_field['value']:
                name = auth.get('authorName', {}).get('value', '')
                aff = auth.get('authorAffiliation', {}).get('value', 'N/A')
                id_val = auth.get('authorIdentifier', {}).get('value', 'N/A')
                authors_list.append(f"{name} ({aff}) - ID: {id_val}")
        
        # Extracción de Academic Unit (Metadato personalizado institucional)
        # Nota: Ajusta 'academicUnit' si el nombre técnico en tu archivo .tsv varía
        academic_unit = ""
        au_field = next((f for f in metadata_blocks if f['typeName'] == 'urfaculty'), None)
        if au_field:
            academic_unit = au_field.get('value', [])[0]
            
        # 3. Consultar el Dataverse contenedor para extraer correos y afiliación de los dueños
        dv_url = f"{BASE_URL}/api/dataverses/{dv_alias}/assignments"
        dv_data = requests.get(dv_url, headers=HEADERS).json()
        dv_admin = dv_data.get('data', [])
        roles_dv_list = []
        for admin in dv_admin:
            idAdmin = admin.get('id', '')
            userAdmin = admin.get('assignee', '')
            role = admin.get('roleName', '')
            #Ya consultado los rolles y asignacion se va a validar los nombres y correos
            user_url = f"{BASE_URL}/api/admin/authenticatedUsers/{userAdmin.replace('@','')}"
            user_data = requests.get(user_url, headers=HEADERS).json()
            userAdmin = user_data.get('data', {})
            userName = userAdmin.get('displayName','')
            userAff = userAdmin.get ('affiliation','')
            userEmail = userAdmin.get('email','')
            roles_dv_list.append(f"{userName} ({userAff}) - email: {userEmail}")
            #print (f"{userName} ({userAff}) - email: {userEmail}")
        
        # contacts_list = []
        # for contact in dv_contacts:
        #     c_name = contact.get('contactUser', {}).get('displayInfo', {}).get('title', 'N/A')
        #     c_email = contact.get('contactEmail', 'N/A')
        #     contacts_list.append(f"{c_name} <{c_email}>")

        # Guardar en la estructura del reporte
        full_report.append({
            "DOI": pid,
            "EstadoDataset": latest_version.get("versionState"),
            "datasetTitulo": item.get("name"),
            "numeroAutores": len(authors_list),
            "autoresDataset": " | ".join(authors_list),
            "UnidadAcademicaDataset": academic_unit,
            "EstadoPublicacionDataset": statusPublicaDataset,
            "EstadoVersion": statusVersion,
            "idDataverse": dv_alias,
            "nombreDataverse": item.get("name_of_dataverse"),
            "numeroAdmin": len(roles_dv_list),
            "AdminDataverse": " | ".join(roles_dv_list)
        })
        print(f'Se procesa exitosamente el DOI {pid}')
        time.sleep(0.1) # Evitar saturación del pool de conexiones de Payara
    except Exception as e:
        print(f"Error procesando {pid}: {str(e)}")
        full_report.append({
            "DOI": pid,
            "EstadoDataset": latest_version.get("versionState"),
            "datasetTitulo": item.get("name"),
            "numeroAutores": len(item.get("authors",[])),
            "autoresDataset": "|".join(item.get("authors",[])),
            "UnidadAcademicaDataset": "",
            "EstadoPublicacionDataset": statusPublicaDataset,
            "EstadoVersion": statusVersion,
            "idDataverse": dv_alias,
            "nombreDataverse": item.get("name_of_dataverse"),
            "numeroAdmin": "",
            "AdminDataverse": ""
            #"numeroAdmin": len(roles_dv_list),
            #"AdminDataverse": " | ".join(roles_dv_list)
        })

# Convertir a DataFrame y descargar
df = pd.DataFrame(full_report)
df.to_csv(archivo, index=False, encoding="utf-8-sig", sep=";")
print(f'Reporte generado exitosamente en {archivo}')