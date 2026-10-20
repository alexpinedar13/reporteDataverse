import requests

def get_file_report(base_url, headers, items):
    print("[+] Procesando metadatos a nivel de Archivos...")
    file_records = []

    for item in items:
        pid = item.get("global_id")
        
        try:
            ds_url = f"{base_url}/api/datasets/:persistentId/?persistentId={pid}"
            ds_res = requests.get(ds_url, headers=headers)
            if ds_res.status_code != 200:
                continue

            ds_data = ds_res.json().get('data', {})
            latest_version = ds_data.get('latestVersion', {})
            files = latest_version.get('files', [])

            has_guestbook = ds_data.get('hasGuestbook', False)
            #ds_state = latest_version.get('versionState')
            statuses = item.get("publicationStatuses", [])

            # Extraer Unidad Académica para propagar al archivo
            metadata_blocks = latest_version.get('metadataBlocks', {})
            citation_fields = metadata_blocks.get('citation', {}).get('fields', [])
            if 'Urcitation' in metadata_blocks:
                citation_fields.extend(metadata_blocks['Urcitation'].get('fields', []))

            academic_unit = "N/A"
            for field in citation_fields:
                if field.get('typeName') in ['urfaculty', 'academicUnit']:
                    val = field.get('value')
                    academic_unit = val[0] if isinstance(val, list) else str(val)

            for f in files:
                data_file = f.get('dataFile', {})
                is_restricted = f.get('restricted', False)

                file_records.append({
                    "ID Archivo": data_file.get('id'),
                    "Nombre Archivo": data_file.get('filename'),
                    "Dataset PersistentID": pid,
                    "Tipo MIME": data_file.get('contentType'),
                    "Tamaño (Bytes)": data_file.get('filesize'),
                    "Estado Acceso": "Restringido" if is_restricted else "Abierto",
                    #"Estado Publicación": "Publicado" if ds_state == "RELEASED" else "Borrador",
                    "Estado Publicación": ", ".join(statuses) if isinstance(statuses, list) else str(statuses),
                    "Unidad Académica": academic_unit,
                    "Libro de Invitados (Guestbook)": "Sí" if has_guestbook else "No",
                    "Fecha Creación Archivo": data_file.get('creationDate', "N/A"),
                    "Fecha Publicación Dataset": ds_data.get("publicationDate", "N/A")
                })

        except Exception as e:
            print(f"   [!] Error extrayendo archivos del Dataset '{pid}': {str(e)}")

    return file_records