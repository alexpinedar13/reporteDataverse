import requests

def get_dataset_report(base_url, headers, items):
    print("[+] Procesando metadatos a nivel de Datasets...")
    ds_records = []

    for item in items:
        pid = item.get("global_id")
        dv_alias = item.get("identifier_of_dataverse")
        
        try:
            ds_url = f"{base_url}/api/datasets/:persistentId/?persistentId={pid}"
            ds_res = requests.get(ds_url, headers=headers)
            if ds_res.status_code != 200:
                continue
            

            ds_data = ds_res.json().get('data', {})
            latest_version = ds_data.get('latestVersion', {})
            #version_state = latest_version.get('versionState') # RELEASED, DRAFT, DEACCESSED

            # Parseo de Bloques de Metadatos (citation y Urcitation)
            metadata_blocks = latest_version.get('metadataBlocks', {})
            citation_fields = metadata_blocks.get('citation', {}).get('fields', [])
            statuses = item.get("publicationStatuses", [])

            if 'Urcitation' in metadata_blocks:
                citation_fields.extend(metadata_blocks['Urcitation'].get('fields', []))

            authors = []
            academic_unit = "N/A"

            for field in citation_fields:
                t_name = field.get('typeName')
                if t_name == 'author':
                    for auth in field.get('value', []):
                        name = auth.get('authorName', {}).get('value', '')
                        aff = auth.get('authorAffiliation', {}).get('value', '')
                        authors.append(f"{name} ({aff})" if aff else name)
                elif t_name in ['urfaculty', 'academicUnit', 'grantAgency']:
                    val = field.get('value')
                    academic_unit = val[0] if isinstance(val, list) else str(val)

            ds_records.append({
                "DOI / PersistentID": pid,
                "Título Dataset": item.get("name"),
                "Dataverse Padre": dv_alias,
                #"Estado Version": version_state,
                "Estado Version": ", ".join(statuses) if isinstance(statuses, list) else str(statuses),
                #"Estado Publicación": "Publicado" if version_state == "RELEASED" else ("Borrador" if version_state == "DRAFT" else "Desclasificado"),
                "Unidad Académica": academic_unit,
                "Autores": " | ".join(authors),
                "Número Autores": len(authors),
                "Licencia": latest_version.get('license', {}).get('name', 'Personalizada'),
                "Fecha Creación": latest_version.get("createTime", "N/A"),
                "Fecha Publicación": latest_version.get("publicationDate", "N/A")
            })

        except Exception as e:
            print(f"   [!] Error procesando Dataset '{pid}': {str(e)}")

    return ds_records