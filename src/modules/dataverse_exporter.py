import requests

def get_dataverse_report(base_url, headers, items):
    print("[+] Procesando metadatos a nivel de Dataverses...")
    processed_aliases = set()
    dv_records = []

    for item in items:
        # En resultados con type=dataverse, la llave del alias es 'identifier'
        dv_alias = item.get("identifier") or item.get("identifier_of_dataverse")
        
        if not dv_alias or dv_alias in processed_aliases:
            continue
        
        processed_aliases.add(dv_alias)
        
        try:
            # 1. Metadatos generales del Dataverse
            dv_info_url = f"{base_url}/api/dataverses/{dv_alias}"
            dv_res = requests.get(dv_info_url, headers=headers)
            dv_data = dv_res.json().get('data', {}) if dv_res.status_code == 200 else {}
            
            # 2. Asignación de Roles / Usuarios
            dv_roles_url = f"{base_url}/api/dataverses/{dv_alias}/assignments"
            roles_res = requests.get(dv_roles_url, headers=headers)
            assignments = roles_res.json().get('data', []) if roles_res.status_code == 200 else []
            
            admins = []
            other_users = []
            statusPublicaDataset = item.get("publicationStatuses", [])[0]
            #statusVersion = item.get("publicationStatuses", '')
            for assign in assignments:
                role_name = assign.get('roleName', '')
                assignee = assign.get('assignee', '').replace('@', '')
                
                # Consulta a la API de administración de usuarios
                user_url = f"{base_url}/api/admin/authenticatedUsers/{assignee}"
                u_res = requests.get(user_url, headers=headers)
                
                if u_res.status_code == 200:
                    u_info = u_res.json().get('data', {})
                    user_str = f"{u_info.get('displayName', '')} <{u_info.get('email', '')}>"
                else:
                    user_str = assignee

                if "Admin" in role_name or "Administrador" in role_name:
                    admins.append(user_str)
                else:
                    other_users.append(f"{user_str} ({role_name})")

            #pub_date = dv_data.get('publicationDate')
            pub_date = item.get('published_at', "N/A")
                
            dv_records.append({
                "Alias Dataverse": dv_alias,
                "URL": f'https://research-data.urosario.edu.co/dataverse/{dv_alias}',
                "Nombre Dataverse": dv_data.get("name", item.get("name")),
                #"Estado Publicación": "Publicado" if pub_date else "No Publicado",
                "Estado": statusPublicaDataset,
                #"EstadoVersion": statusVersion,
                "Unidad Académica / Afiliación": dv_data.get("affiliation", "N/A"),
                "URL Dataverse": f"{base_url}/dataverse/{dv_alias}",
                "numeroAdmin": len(admins),
                "Administradores": " | ".join(admins),
                "numeroOtros": len(other_users),
                "Otros Usuarios Asignados": " | ".join(other_users),
                "Fecha Creación": dv_data.get("creationDate", "N/A"),
                "Fecha Publicación": pub_date if statusPublicaDataset=="Published" else "N/A"
            })
        except Exception as e:
            print(f"   [!] Error procesando Dataverse '{dv_alias}': {str(e)}")

    return dv_records