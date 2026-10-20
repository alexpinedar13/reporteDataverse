# 📊 Generador de Informes Consolidados para Dataverse (Metadata Exporter)

Herramienta administrativa desarrollada en Python (**Flask + Pandas + OpenPyXL**) diseñada para la extracción automatizada, procesamiento y consolidación de metadatos de repositorios institucionales Dataverse (**Dataverses, Datasets y Archivos**) en un único libro de Excel estructurado.

---

## 🛠️ Stack Tecnológico e Infraestructura
* **Sistema Operativo:** Rocky Linux / RHEL / AlmaLinux
* **Servidor de Aplicaciones Principal:** Payara Server (Java EE) / Dataverse Core
* **Backend de Informes:** Python 3.10+ ejecutado mediante entorno virtual (`.venv`)
* **Framework Web Auxiliar:** Flask
* **Gestor de Dependencias:** `uv`
* **Servidor Web / Proxy Inverso:** Apache HTTPD (`mod_proxy`) con directivas de timeout extendido.
* **Orquestador de Procesos:** Systemd

---

## 📂 Estructura de Directorios del Proyecto

El repositorio se encuentra ubicado en `/usr/local/dataverse/script/reporteDataverse/` y cuenta con la siguiente arquitectura de archivos:

```text
/usr/local/dataverse/script/reporteDataverse/
├── .streamlit/                # Configuración auxiliar (si aplica)
├── .venv/                     # Entorno virtual de Python con dependencias instaladas
├── csvAntiguos/               # Histórico de respaldos en CSV
├── Informes/                  # Directorio de salida donde se guardan los .xlsx generados
├── src/                       # Código fuente de la aplicación Flask
│   ├── app.py                 # Script base de Streamlit (obsoleto/alternativo)
│   ├── main.py                # Orquestador CLI principal de extracción
│   ├── web_app.py             # Servidor web Flask encargado de la interfaz y peticiones POST/GET
│   ├── modules/               # Módulos de extracción de metadatos de la API Dataverse
│   │   ├── dataverse_exporter.py # Extracción de contenedores (Dataverses)
│   │   ├── dataset_exporter.py   # Extracción de conjuntos de datos y estados de publicación
│   │   └── file_exporter.py      # Extracción y asociación de ficheros digitales
│   └── templates/
│       └── index.html         # Interfaz gráfica web clásica para el administrador
├── Gestion Informe.xlsx       # Formato de gestión de referencia
├── informe.py                 # Script auxiliar de procesamiento
├── logCreacion.log            # Registro de logs del sistema
├── pyproject.toml             # Definición de dependencias y metadatos del proyecto
├── uv.lock                    # Bloqueo de versiones de paquetes de Python
└── README.md                  # Documentación técnica del sistema
```

## ⚙️ Paso a Paso: Puesta en Marcha y Despliegue
# 1. Preparación del Entorno y Dependencias
*Posiciónate en la ruta del proyecto y asegúrate de tener *sincronizadas las dependencias necesarias dentro del entorno *virtual:
```text
Bash
cd /usr/local/dataverse/script/reporteDataverse
```
# Prerequisitos
El script se ejecuta por medio del gestor uv entonces es necesario verificar que ya este instalado con uv -version si no instalar con:

```text
Bash
pip install uv
```
Ahora si se puede sincronizar el gestor para utilizar las dependencias y configuracion de pyproject.toml adicional activar el venv
```text
Bash
uv sync
```
# Instalación de librerías mediante uv del entorno virtual
Si todo salio bien solo realizando el uv sync ya se sincronizan e instalan las librerias si las tiene entonces se puede con
```text
uv add flask openpyxl requests pandas
```
# 2. Configuración del Servicio Systemd
Para garantizar que la aplicación corra de manera persistente en segundo plataforma y se reinicie automáticamente ante caídas del servidor o reinicios del sistema operativo, creamos el archivo de servicio en systemd.

Crea o edita el archivo de definición:
```text
Bash
sudo nano /etc/systemd/system/dataverse-reports.service
```
Configura el servicio con los siguientes parámetros de ejecución (ejecutando como root para evitar bloqueos de permisos POSIX sobre las rutas de exportación):

```text
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
Recarga los daemons de Systemd, habilita e inicia el servicio:
```
```text
Bash
sudo systemctl daemon-reload
sudo systemctl enable --now dataverse-reports.service
```

Valida el estado actual del servicio:
```text
Bash
sudo systemctl status dataverse-reports.service
```

# 3. Configuración del Firewall (Rocky Linux / Firewalld)
Dado que el servicio web opera internamente en el puerto 8501, asegúrate de que el firewall del sistema operativo permita el tráfico local o el direccionamiento requerido por el proxy:
```text
Bash
# Verificar estado de firewalld
sudo firewall-cmd --state
```

# Si el puerto 8501 requiere acceso directo interno o de prueba:
```text
sudo firewall-cmd --zone=public --add-port=8501/tcp --permanent
sudo firewall-cmd --reload
```
# 4. Configuración del Proxy Inverso en Apache HTTPD
Para exponer la herramienta institucionalmente bajo la ruta amigable /informes, configuramos el VirtualHost de Apache.

Edita el archivo de configuración correspondiente (ej. /etc/httpd/conf.sites.d/dataverse-vhost.conf o /etc/httpd/conf.d/dataverse-vhost.conf):

```text
Bash
sudo nano /etc/httpd/conf.d/dataverse-vhost.conf
```

Asegúrate de incluir el módulo proxy y las directivas de Timeout extendido (vitales para evitar errores de tipo 502 Proxy Error debido al tiempo que toma consultar la API de Dataverse en repositorios con alto volumen de datos):
```text
Apache
LoadModule proxy_module modules/mod_proxy.so

ProxyPreserveHost On

# Extender el tiempo de espera del proxy a 1000 segundos para peticiones pesadas de la API
ProxyTimeout 1000
Timeout 1000

# Redirección limpia y directa para Flask bajo /informes
ProxyPass /informes http://127.0.0.1:8501/informes
ProxyPassReverse /informes http://127.0.0.1:8501/informes
```
Ahora reinicia el servicio de apache para efectuar los cambios

```text
Bash
sudo systemctl restart httpd
```
🧪 Pruebas de Funcionamiento y Verificación
Verificar que el puerto de escucha de Python esté activo:

```text
Bash
ss -tulpn | grep 8501
```

Respuesta esperada: Un socket escuchando en 127.0.0.1:8501 o 0.0.0.0:8501 bajo el proceso de Python.

Revisar los logs del servicio en tiempo real:

```text
Bash
sudo journalctl -u dataverse-reports.service -f -n 50
```
Prueba de acceso web:
Abre tu navegador web e ingresa a la URL configurada:
```text
http://<IP_O_DOMINIO>/informes
# para nuestro caso quedaria
http://10.194.194.27/informes/
```
Deberás visualizar el formulario de autenticación para ingresar la URL de Dataverse y el Token de API de superusuario.

# 💡 Recomendaciones Operativas para el Administrador (Rocky Linux)
Tiempos de Ejecución: Debido a que la extracción recorre de manera iterativa todos los objetos indexados en la API de búsqueda de Dataverse, el proceso puede demorar entre 5 y 10 minutos dependiendo de la cantidad de datasets. No interrumpa el proceso de Apache; el ProxyTimeout 1000 garantiza que la conexión permanezca abierta hasta que el archivo Excel sea generado y descargado con éxito.

Permisos del Sistema de Archivos: La aplicación crea automáticamente la carpeta /usr/local/dataverse/script/reporteDataverse/Informes/ mediante rutas absolutas usando pathlib. Asegúrese de que el usuario ejecutor en Systemd cuente con privilegios de escritura en dicha ruta.