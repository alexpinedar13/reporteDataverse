# Generador de Informes Consolidados - Dataverse (Metadata Exporter)

Herramienta administrativa desarrollada en Python (Flask + Pandas + OpenPyXL) para la extracción automatizada y consolidación de metadatos de repositorios Dataverse (Dataverses, Datasets y Archivos) en un único libro de Excel estructurado.

## 🛠️ Stack Tecnológico
* **Backend:** Python 3.10+ / Flask / Requests / Pandas / OpenPyXL
* **Gestión de Dependencias:** `uv`
* **Servidor Web / Proxy Inverso:** Apache HTTPD (`mod_proxy`)
* **Orquestador de Procesos:** Systemd (Linux RHEL/CentOS/AWS Linux)

---

## 📂 Estructura del Proyecto
```text
reporteDataverse/
├── src/
│   ├── web_app.py               # Aplicación web Flask (Interfaz y Control)
│   ├── modules/
│   │   ├── dataverse_exporter.py # Extracción de metadatos de Dataverses y roles
│   │   ├── dataset_exporter.py   # Extracción de Datasets, autores y estado de versión (Draft/Released)
│   │   └── file_exporter.py      # Extracción y asociación de archivos
│   └── templates/
│       └── index.html            # Interfaz gráfica web para el gestor
├── Informes/                     # Directorio de salida de los reportes .xlsx generados
├── pyproject.toml                # Definición de dependencias (uv)
└── README.md                     # Documentación técnica
⚙️ Instalación y Configuración del Entorno
Clonar o posicionarse en el directorio del proyecto:

Bash
cd /usr/local/dataverse/script/reporteDataverse
Sincronizar dependencias con uv:

Bash
uv sync
# O instalar manualmente en el entorno virtual .venv:
.venv/bin/pip install flask openpyxl requests pandas
Configuración del Servicio Systemd (/etc/systemd/system/dataverse-reports.service):

Ini, TOML
[Unit]
Description=Dataverse Report Generator Flask Dashboard
After=network.target payara.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/usr/local/dataverse/script/reporteDataverse
ExecStart=/usr/local/dataverse/script/reporteDataverse/.venv/bin/python src/web_app.py
Restart=always
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
Habilitar e iniciar el servicio:

Bash
sudo systemctl daemon-reload