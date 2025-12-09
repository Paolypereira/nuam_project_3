# 🌐 NUAM – Mantenedor Bursátil y API Regional

**NUAM** es una aplicación desarrollada en **Django + Django REST Framework**, que permite administrar información bursátil de los mercados de **Chile, Colombia y Perú**.  
El proyecto incluye un **panel administrativo**, una **API funcional**, un **catálogo de empresas**, un **convertidor de moneda**, un **dashboard de visualización de datos** y un **modelo de datos (M.E.R)** accesible desde la interfaz principal.

---

## ✅ Funcionalidades principales

- Panel administrativo completo con Django Admin (CRUD sobre empresas, países y tablas relacionadas).
- Catálogo HTML de empresas, cargado dinámicamente desde la API (fetch a `/catalogo-data/`).
- API REST operativa con Django REST Framework:
  - `GET /api/empresas/`, `POST`, `PUT`, `DELETE` según permisos.
  - `GET /api/paises/`
  - `GET /api/top-empresas/?pais=CHL&n=5`
- Documentación autogenerada OpenAPI/Swagger:
  - Swagger UI en `/swagger/`
  - ReDoc en `/redoc/`
- Modelo entidad–relación (M.E.R) accesible desde `/mer/` con zoom sobre la imagen.
- Convertidor de moneda conectado a API externa en `/convertir-moneda/`.
- **Dashboard de monedas** en `/dashboard-monedas/`:
  - Comparación actual de CLP, COP, PEN y UF frente a una moneda base seleccionable (USD, CLP, COP, PEN, UF).
  - Evolución histórica simulada de cada moneda.
  - Resumen rápido (fecha de datos, moneda más fuerte y más débil).
  - Gráfico doughnut de participación relativa por moneda.
- Manejo de errores 404/500 personalizados y logging a archivo (`logs/django_errors.log`).
- Integración con Kafka (publicación de eventos cuando se crea/edita una Empresa).

---

## ⚙️ Requisitos previos

| Herramienta         | Windows                                                                 | Linux/Ubuntu                                       |
|---------------------|-------------------------------------------------------------------------|----------------------------------------------------|
| **Python 3.10+**    | ✅ [Descargar desde python.org](https://www.python.org/downloads/)      | `sudo apt install python3 python3-venv python3-pip` |
| **Git**             | ✅ [Descargar desde git-scm.com](https://git-scm.com/downloads)         | `sudo apt install git`                             |
| **Docker** (Kafka)  | [Docker Desktop](https://www.docker.com/products/docker-desktop/)       | `sudo apt install docker.io docker-compose`        |

---

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio

git clone https://github.com/Paolypereira/nuam_project_3.git
cd nuam_project_3


### 2️⃣ Crear entorno virtual

**Windows PowerShell:**

python -m venv .venv
..venv\Scripts\Activate.ps1


**Linux / Ubuntu:**

python3 -m venv .venv
source .venv/bin/activate


Si en Windows aparece error al activar el entorno, abrir PowerShell como Administrador y ejecutar:

Set-ExecutionPolicy RemoteSigned


### 3️⃣ Crear carpeta de logs

En una instalación nueva la carpeta `logs/` no existe (Git no versiona carpetas vacías).  
Debe crearse manualmente en la raíz del proyecto (donde está `manage.py`):

mkdir logs


Django usará esta carpeta para escribir el archivo `logs/django_errors.log`.

### 4️⃣ Instalar dependencias

pip install -r requirements.txt


### 5️⃣ Aplicar migraciones de base de datos

python manage.py migrate


Si falla, eliminar `db.sqlite3` y repetir el comando.

### 6️⃣ Crear superusuario (obligatorio para Admin)

python manage.py createsuperuser


Ingresar username, email y password y guardarlos para login.

### 7️⃣ Cargar países base (Chile, Colombia, Perú)

python manage.py cargar_paises


### 8️⃣ Cargar datos bursátiles desde Excel

El archivo Excel está en:

cargas/2025/10/Informe_Bursatil_Regional_2025-08.xlsx


Ejemplo de importación en Windows:

python manage.py seed_empresas --file "C:\Users\TuUsuario\proyecto\cargas\2025\10\Informe_Bursatil_Regional_2025-08.xlsx"


La salida mostrará algo como:

Empresas creadas: 0, actualizadas: 159, omitidas: 72


### 9️⃣ Ejecutar el servidor de desarrollo

**Windows:**

python manage.py runserver


**Linux / Ubuntu:**

python3 manage.py runserver


Verás algo como:

Starting development server at http://127.0.0.1:8000/


### 🔟 Abrir el sitio en el navegador

1. Abrir Chrome/Firefox/Edge.  
2. Ir a `http://127.0.0.1:8000/`.

---

## 🖥️ Interfaz principal y usuarios

Al ingresar verás estas opciones:

| Sección                   | Descripción                                         |
|---------------------------|-----------------------------------------------------|
| 🏢 Catálogo de Empresas   | Visualiza las empresas cargadas desde Excel.       |
| ⚙️ Panel Admin            | CRUD completo mediante Django Admin.               |
| 🧩 Diagrama NUAM (M.E.R)  | Visualización del modelo de datos.                 |
| 🔄 Convertidor de moneda  | Conversión entre CLP, COP, PEN y USD.              |
| 📊 Dashboard de monedas   | Visualización comparativa de CLP, COP, PEN y UF.   |
| 🔌 API REST               | Acceso a la documentación Swagger UI.              |

**Usuario para login Admin**

- Usa el superusuario creado en el paso 6.
- Admin: `http://127.0.0.1:8000/admin/`

---

## 📡 Kafka con Docker

Requiere Docker instalado y corriendo.

### Terminal 1 – Ver contenedores (opcional)

docker ps -a


### Terminal 2 – Crear red y levantar Zookeeper + Kafka

docker network create kafka-net

docker run -d --name zookeeper --network kafka-net -p 2181:2181 zookeeper:3.7

docker run -d --name kafka --network kafka-net -p 9092:9092 ^
-e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 ^
-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 ^
confluentinc/cp-kafka:7.5.0


Comprobar:

docker ps

### Terminal 3 – Crear tópico `empresas-events` (solo una vez)

docker exec kafka kafka-topics
--create
--topic empresas-events
--bootstrap-server localhost:9092
--partitions 1
--replication-factor 1


Cada vez que se levante Zookeeper y Kafka, NUAM publicará eventos en `empresas-events` al crear o editar empresas.

---

## 🪟 Kafka en Windows sin Docker (solo desarrollo)

Suponiendo Kafka en `C:\kafka\kafka_2.13-3.9.1`:

**Terminal 1 – Zookeeper**

cd C:\kafka\kafka_2.13-3.9.1
bin\windows\zookeeper-server-start.bat config\zookeeper.properties


**Terminal 2 – Kafka broker**

cd C:\kafka\kafka_2.13-3.9.1
bin\windows\kafka-server-start.bat config\server.properties


Kafka quedará disponible en `localhost:9092` y la aplicación NUAM podrá publicar eventos en `empresas-events`.

---

## 🔌 API RESTful NUAM

Construida con **Django REST Framework**:

- `GET /api/empresas/` — Lista paginada con filtros.  
- `GET /api/empresas/{id}/` — Detalle de empresa.  
- `POST /api/empresas/` — Crear empresa (requiere autenticación).  
- `PUT/PATCH /api/empresas/{id}/` — Actualizar empresa.  
- `DELETE /api/empresas/{id}/` — Eliminar empresa.  
- `GET /api/paises/` — Lista de países.  
- `GET /api/top-empresas/?pais=CHL&n=5` — Empresas top por país.

### 📚 Documentación OpenAPI / Swagger

- Swagger UI: `http://127.0.0.1:8000/swagger/`  
- ReDoc: `http://127.0.0.1:8000/redoc/`

---

## 🧩 Modelo Entidad-Relación (M.E.R)

- Imagen: `static/diagramas/MER_NUAM2.0.png`.  
- Vista en: `http://127.0.0.1:8000/mer/` (permite zoom con la rueda del mouse).  
- Entidades principales: País, Empresa, Normativa, Calificación Tributaria, Instrumentos No Inscritos, Historial de Cambios, Valor de Instrumentos.

---

## 🛡️ Manejo de errores, logging y monitoreo

- Páginas personalizadas para errores 404 y 500 en `templates/errors/`.
- Archivo de logs para errores: `logs/django_errors.log`.
- Manejo de errores en vistas críticas (convertidor de moneda, integración con Kafka) con `try/except` y niveles de logging.
- Integración con **Sentry** (`sentry-sdk` + `DjangoIntegration`), configurada vía `SENTRY_DSN` para monitoreo casi en tiempo real.

---

## 🔒 Certificados digitales y HTTPS local

Se incluye configuración básica de HTTPS en entorno local usando certificados autofirmados y `django-sslserver`.

### Windows (PowerShell)

Generar certificado para `localhost`:

New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "Cert:\LocalMachine\My"


### Linux (OpenSSL)

openssl req -x509 -nodes -days 365 -newkey rsa=2048
-keyout nuam-localhost.key -out nuam-localhost.crt
-subj "/CN=localhost"


### Ejecutar con HTTPS (Windows y Linux)

En `requirements.txt`:

django-sslserver


En `settings.py`:

INSTALLED_APPS = [
...
"sslserver",
"mercados",
]


Comando:

python manage.py runsslserver 127.0.0.1:8000


Luego acceder a:

https://127.0.0.1:8000/


y aceptar el certificado autofirmado.

---

## 📡 Integración con Kafka (Pub/Sub)

- Publica mensajes en Kafka al crear o actualizar empresas.
- Mensajes con campos clave (`ticker`, `nombre`, `pais`, `moneda`, `capitalizacion`).

---

## 🧹 Archivos ignorados por Git

`.gitignore` incluye:

*.pyc
pycache/
.env
.venv/
db.sqlite3
*.xlsx
/staticfiles/
logs/

---

## 🎓 Sugerencia de recorrido para la evaluación

1. Mostrar el **dashboard principal** (`/`) con tarjetas y navegación.
2. Navegar el **catálogo** (`/catalogo/`) mostrando importación desde Excel.
3. Mostrar el **panel admin** (`/admin/`) con CRUD de Empresas.
4. Demostrar la **API REST** (`/api/empresas/`, `/api/paises/`, `/api/top-empresas/`).
5. Explorar la documentación (`/swagger/` y `/redoc/`).
6. Ver el diagrama **M.E.R.** (`/mer/`).
7. Probar el **convertidor de moneda** (`/convertir-moneda/`).
8. Mostrar el **dashboard de monedas** (`/dashboard-monedas/`) explicando sus gráficos.
9. Mencionar la integración con **Kafka** y los comandos para levantarlo.
10. Mostrar el **logging** (`logs/django_errors.log`) y el monitoreo con **Sentry**.
11. Ejecutar el proyecto con **HTTPS local** usando `runsslserver`.

---

## 📖 Manual de usuario

El manual de usuario detallado está disponible en formato PDF en este repositorio:

[Manual de usuario NUAM (PDF)](Manual%20de%20usuario%20NUAM.pdf)