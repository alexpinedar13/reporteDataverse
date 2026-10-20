---

## 2. Guía de Uso para el Gestor del Repositorio

Esta sección está diseñada para ser entregada directamente al administrador funcional o gestor documental a cargo de la herramienta.

---

# 📖 Manual de Usuario: Panel de Generación de Informes Dataverse

## 1. Parámetros de Acceso Requeridos
Para ejecutar la extracción de metadatos, la interfaz web le solicitará dos datos fundamentales:

* **URL Instancia Dataverse:** 
  * Corresponde a la dirección base oficial del repositorio institucional.
  * *Ejemplo:* `[https://research-data.urosario.edu.co](https://research-data.urosario.edu.co)`
* **Dataverse API Key (Token de Superusuario):** 
  * Llave de autenticación cifrada requerida para consultar metadatos protegidos y estructurados a nivel de sistema.

### 🔑 ¿Cómo obtener el API Token de Superusuario?
Si aún no cuenta con su token personal con privilegios administrativos, siga estos pasos:
1. Inicie sesión en la interfaz web de Dataverse con su cuenta de administrador.
2. Haga clic sobre su **nombre de usuario** en la esquina superior derecha y seleccione **API Token** (o ingrese a *Account Information* -> *API Token*).
3. Si no existe un token activo, haga clic en el botón **"Create Token"**.
4. Copie la cadena alfanumérica generada (ej. `92979613-0616-4b5e-893f-...`) y guárdela de forma segura; este token reemplaza su contraseña para las peticiones de extracción.

---

## 2. Instrucciones de Uso de la Herramienta

1. Abra su navegador web e ingrese a la ruta asignada por el departamento de TI:
   `http://<IP_O_DOMINIO>/informes/`
2. Ingrese la **URL de la instancia** y su **API Token** en los campos correspondientes.
3. Haga clic en el botón **"🚀 Iniciar Extracción y Descargar Excel"**.
4. **Nota de Rendimiento:** Debido al volumen masivo de registros en el repositorio, la consulta y consolidación de metadatos puede tardar **entre 3 y 10 minutos** en completarse. Por favor, no cierre ni recargue la pestaña del navegador mientras el sistema procesa la información. Al finalizar, la descarga del archivo Excel comenzará de forma automática.

---

## 3. Estructura y Elementos del Archivo Descargado (`.xlsx`)

El archivo Excel generado se titula bajo la nomenclatura `Informe_Consolidado_Dataverse_DD-MM-YYYY_HHMM.xlsx` y contiene **3 hojas independientes** organizadas de la siguiente forma:

### 📄 Hoja 1: `Dataverses`
Registra la estructura jerárquica de los contenedores (facultades, grupos o colecciones).
* **Identificador / Alias:** Nombre corto único del Dataverse.
* **Nombre del Dataverse:** Título institucional visible.
* **Fecha de Creación:** Timestamp de alta en el sistema.

### 📊 Hoja 2: `Datasets`
Contiene la auditoría detallada a nivel de conjuntos de datos, incorporando la lógica avanzada de discriminación de estados.
* **DOI / PersistentIdentifer:** Enlace persistente único del dataset.
* **Título Dataset:** Nombre oficial del conjunto de datos.
* **Dataverse Padre:** Contenedor al que pertenece.
* **Estado Version (`publicationStatuses`):** Clasificación exacta obtenida del motor de búsqueda (ej. `Published`, `Published, Draft` si posee modificaciones sin publicar, o `Unpublished, Draft` si es borrador nuevo).
* **Unidad Académica / Facultad:** Metadato extraído de los bloques institucionales personalizados (`Urcitation`).
* **Autores y Afiliaciones:** Listado completo concatenado de los creadores del dataset.
* **Licencia:** Tipo de licenciamiento asignado (Creative Commons, personalizada, etc.).
* **Fechas:** Creación y Publicación oficial.

### 📁 Hoja 3: `Archivos`
Detalla todos los archivos digitales adjuntos dentro de los datasets del repositorio.
* **Nombre de Archivo:** Fichero almacenado.
* **Dataset Padre (DOI):** Relación directa con el conjunto de datos contenedor.
* **Tipo MIME / Formato:** Extensión y naturaleza técnica del archivo.
* **Tamaño (Bytes):** Peso volumétrico del recurso digital.
* **Estado del Archivo:** Hereda el estado de publicación del dataset al que pertenece (Publicado / Borrador).