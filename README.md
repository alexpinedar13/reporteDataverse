/opt/script/informes/
├── main.py                        # Entrypoint: Orquestador y exportador a Excel
├── requirements.txt               # Dependencias del entorno virtual
├── README.md                      # Documentación técnica de administración
└── modules/
    ├── __init__.py                # Declaración de paquete Python
    ├── dataverse_exporter.py     # Extracción de Dataverses, ACLs, Admins y Usuarios
    ├── dataset_exporter.py       # Extracción de Datasets, DOIs, Autores, Licencias y Bloques UR
    └── file_exporter.py          # Extracción de Archivos, MIME Types, Guestbook y Restricciones