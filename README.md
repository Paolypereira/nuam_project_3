# 🌐 NUAM – Mantenedor Bursátil y API Regional

**NUAM** es una aplicación desarrollada en **Django + Django REST Framework**, que permite administrar información bursátil de los mercados de **Chile, Colombia y Perú**.  
El proyecto incluye un **panel administrativo**, una **API funcional**, un **catálogo de empresas**, y un **modelo de datos (M.E.R)** accesible desde la interfaz principal.

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
- Manejo de errores 404/500 personalizados y logging a archivo (`logs/django_errors.log`).  
- Integración con Kafka (publicación de eventos cuando se crea/edita una Empresa).  

---

## ⚙️ Requisitos previos

| Herramienta        | Windows                                                             | Linux/Ubuntu                                            |
|--------------------|---------------------------------------------------------------------|---------------------------------------------------------|
| **Python 3.10+**   | ✅ [Descargar desde python.org](https://www.python.org/downloads/)  | `sudo apt install python3 python3-venv python3-pip`     |
| **Git**            | ✅ [Descargar desde git-scm.com](https://git-scm.com/downloads)     | `sudo apt install git`                                  |
| **Docker** (Kafka) | [Docker Desktop](https://www.docker.com/products/docker-desktop/)  | `sudo apt install docker.io docker-compose`             |

---

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio

git clone https://github.com/Paolypereira/nuam_project_3.git
cd nuam_project


## 2️⃣ Crear entorno virtual

**Windows PowerShell:**

python -m venv .venv
.venv\Scripts\Activate.ps1


**Linux / Ubuntu:**

python3 -m venv .venv
source .venv/bin/activate


⚠️ **En Windows, si aparece error al activar el entorno, ejecuta PowerShell como Administrador y usa:**

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


**Error común:** Si falla, elimina `db.sqlite3` y repite el paso.

### 6️⃣ **CREAR SUPERUSUARIO (OBLIGATORIO para Admin)**

python manage.py createsuperuser


Ingresa username, email y password. **Guarda estos datos para login.**

### 7️⃣ Cargar países base (Chile, Colombia, Perú)

python manage.py cargar_paises


### 8️⃣ Cargar datos bursátiles desde Excel

El archivo Excel está en:

cargas/2025/10/Informe_Bursatil_Regional_2025-08.xlsx


**Pasos para importar:**

- Copia la ruta del archivo completo (en Windows clic derecho → "Copiar como ruta").  
- Ejecuta:

python manage.py seed_empresas --file "ruta_completa_a_tu_excel.xlsx"


**Ejemplo Windows:**

python manage.py seed_empresas --file "C:\Users\TuUsuario\proyecto\cargas\2025\10\Informe_Bursatil_Regional_2025-08.xlsx"


El sistema detectará y mostrará resultados como:

✅ Empresas creadas: 0, actualizadas: 159, omitidas: 72

### 9️⃣ Ejecutar el servidor de desarrollo

**Windows:**

python manage.py runserver


**Linux / Ubuntu:**

python3 manage.py runserver


**Verás este mensaje:**

Starting development server at http://127.0.0.1:8000/


### 🔟 **ABRIR EL SITIO EN EL NAVEGADOR**

1. Abre Chrome/Firefox/Edge  
2. Copia y pega: `http://127.0.0.1:8000/`  
3. **Presiona ENTER**  

**¡Listo, ya está funcionando!**

---

## 🖥️ Interfaz principal y usuarios

Al ingresar verás estas opciones:

| Sección                  | Descripción                                      |
|--------------------------|--------------------------------------------------|
| 🏢 Catálogo de Empresas  | Visualiza las empresas cargadas desde Excel.     |
| ⚙️ Panel Admin           | CRUD completo mediante Django Admin.             |
| 🧩 Diagrama NUAM (M.E.R) | Visualización del modelo de datos.               |
| 🔄 Convertidor de moneda | Para convertir entre CLP, COP, PEN y USD.        |
| 🔌 API REST              | Acceso a la documentación Swagger UI.            |

### Usuario para login

- Usa el **superusuario** creado en el **paso 5**
- Admin: `http://127.0.0.1:8000/admin/`

---

## 🔌 Kafka (Abre terminales adicionales)

**Requiere Docker corriendo.**


## 📡 Kafka (abre terminales adicionales)

Requiere Docker instalado y corriendo.

### Terminal 1 – Ver contenedores existentes (opcional)

docker ps -a

## Terminal 2 – Crear red y levantar Zookeeper + Kafka

crear red para Kafka

docker network create kafka-net
levantar Zookeeper

docker run -d --name zookeeper --network kafka-net -p 2181:2181 zookeeper:3.7
levantar Kafka

docker run -d --name kafka --network kafka-net -p 9092:9092
-e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
confluentinc/cp-kafka:7.5.0


Comprobar que están arriba:

docker ps


Debe mostrar algo similar a:

- `zookeeper:3.7` en el puerto `2181`
- `confluentinc/cp-kafka:7.5.0` en el puerto `9092`

### Terminal 3 – Crear el tópico `empresas-events` (solo una vez)

docker exec kafka kafka-topics
--create
--topic empresas-events
--bootstrap-server localhost:9092
--partitions 1
--replication-factor 1


Después de esto, cada vez que se levante Zookeeper y Kafka, la aplicación NUAM publicará eventos en el tópico `empresas-events` al crear o editar empresas.

### 🪟 Kafka en Windows (sin Docker, solo desarrollo)

Si se desea probar Kafka localmente en Windows sin usar Docker, se puede utilizar la
distribución oficial de Kafka instalada en el disco.

Suponiendo que Kafka fue descomprimido en `C:\kafka\kafka_2.13-3.9.1`, los pasos son:

#### Terminal 1 – Zookeeper

cd C:\kafka\kafka_2.13-3.9.1
bin\windows\zookeeper-server-start.bat config\zookeeper.properties


Dejar esta ventana abierta.

#### Terminal 2 – Kafka broker

cd C:\kafka\kafka_2.13-3.9.1
bin\windows\kafka-server-start.bat config\server.properties


Con ambas ventanas ejecutándose, Kafka queda disponible en `localhost:9092` y la
aplicación NUAM puede publicar eventos en el tópico `empresas-events` al crear o
editar empresas.
---

## 🔌 API RESTful NUAM

Construida con **Django REST Framework**, la API es completamente funcional:

- `GET /api/empresas/` — Lista paginada con filtros.  
- `GET /api/empresas/{id}/` — Detalle empresa.  
- `POST /api/empresas/` — Crear empresa (requiere autenticación).  
- `PUT/PATCH /api/empresas/{id}/` — Actualizar empresa.  
- `DELETE /api/empresas/{id}/` — Eliminar empresa.  
- `GET /api/paises/` — Lista de países.  
- `GET /api/top-empresas/?pais=CHL&n=5` — Empresas top por país.  

### 📚 Documentación OpenAPI / Swagger

- Visualiza Swagger UI en: `http://127.0.0.1:8000/swagger/`  
- Documentación ReDoc en: `http://127.0.0.1:8000/redoc/`  

Permite explorar, probar y validar los endpoints directamente.

---

## 🧩 Modelo Entidad-Relación (M.E.R)

- Imagen: `static/diagramas/MER_NUAM2.0.png`  
- Vista dedicada en: `http://127.0.0.1:8000/mer/` (permite zoom con la rueda del mouse).  
- Entidades principales: País, Empresa, Normativa, Calificación Tributaria, Instrumentos No Inscritos, Historial de Cambios, Valor de Instrumentos.

---

## 🛡️ Manejo de errores, logging y seguridad

- Páginas personalizadas para errores 404 y 500 en `templates/errors/`.  
- Archivo de logs para errores: `logs/django_errors.log`.  
- Preparado para https y seguridad avanzada en `settings.py` (cookies seguras, HSTS, XSS, etc.).

---

## 📊 Manejo de errores y monitoreo en tiempo real

Además del logging a archivo (`logs/django_errors.log`), NUAM incluye:

- Manejo de errores en vistas críticas (convertidor de moneda, integración con Kafka) mediante bloques `try/except` y uso de niveles de logging (`INFO`, `WARNING`, `ERROR`), lo que permite registrar tanto errores como situaciones anómalas.
- Integración con **Sentry** (`sentry-sdk` + `DjangoIntegration`), configurada mediante la variable de entorno `SENTRY_DSN`. Las excepciones no controladas y errores críticos se envían automáticamente al panel web de Sentry, donde pueden visualizarse y analizarse en tiempo (casi) real.

De esta forma, el sistema no solo registra errores en archivos locales, sino que cuenta con monitoreo externo y proactivo para la aplicación NUAM.

## 🔒 Certificados digitales (entorno local)

Aunque NUAM se ejecuta principalmente en entorno local (`http://127.0.0.1:8000/`), se incluye un procedimiento para
generar y utilizar certificados digitales autofirmados tanto en Windows como en Linux, con el fin de cumplir
con el criterio de “Certificados digitales” de la rúbrica.

### Windows (PowerShell, certificado para `localhost`)

1. Abrir **Windows PowerShell** como Administrador.  
2. Ejecutar:

New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "Cert:\LocalMachine\My"

3. El certificado se almacena en el contenedor **Equipo local → Personal** del administrador de certificados
de Windows y puede asociarse a un binding HTTPS de `https://localhost/` (por ejemplo mediante IIS o HTTP.SYS),
reenviando el tráfico a la aplicación Django que corre en `http://127.0.0.1:8000/`.

### Linux (OpenSSL, entorno local)

openssl req -x509 -nodes -days 365 -newkey rsa=2048
-keyout nuam-localhost.key -out nuam-localhost.crt
-subj "/CN=localhost"


Estos archivos (`nuam-localhost.crt`, `nuam-localhost.key`) pueden configurarse en un servidor web ligero
(Nginx o Apache) que exponga `https://localhost/` y reenvíe el tráfico a Django (`http://127.0.0.1:8000/`).

> En un despliegue productivo se recomienda reemplazar estos certificados autofirmados por certificados
> válidos emitidos por una autoridad certificadora (por ejemplo, Let’s Encrypt).

---

## 🔐 Ejecución con HTTPS en entorno local (Windows y Linux)

Para demostrar una configuración básica de HTTPS en entorno local, se utiliza un
certificado autofirmado y el comando `runsslserver` de `django-sslserver`.

### Dependencias

En `requirements.txt`:

django-sslserver

undefined

En `settings.py`, dentro de `INSTALLED_APPS`:

INSTALLED_APPS = [
...
"sslserver",
"mercados",
]


### Windows

python manage.py runsslserver 127.0.0.1:8000


Luego abrir en el navegador:

https://127.0.0.1:8000/


Aceptar la advertencia del certificado autofirmado.

### Linux / Ubuntu

python manage.py runsslserver 127.0.0.1:8000


Y acceder igualmente a:

https://127.0.0.1:8000/


Esta ejecución con HTTPS local, más la sección anterior de certificados digitales,
cumple el criterio de configuración básica de SSL de la rúbrica.

---

## 📡 Integración con Kafka (Pub/Sub)

- Publica mensajes en Kafka al crear o actualizar Empresas.  
- Scripts de prueba incluidos para productor y consumidor.  
- Mensajes con campos clave (`ticker`, `nombre`, `pais`, `moneda`, `capitalizacion`).  

---

## 🧹 Archivos ignorados por Git

El `.gitignore` incluye:

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

1. Mostrar el **dashboard** (`/`) con tarjetas activas y el selector de idioma `ES / EN`.
2. Navegar el **catálogo** (`/catalogo/`) mostrando importación desde Excel.
3. Mostrar el **panel admin** (`/admin/`) con CRUD de Empresas (usando el superusuario).
4. Demostrar la **API REST** (`/api/empresas/`, `/api/paises/`, `/api/top-empresas/`).
5. Explorar la documentación en `/swagger/` y `/redoc/`.
6. Ver el diagrama **M.E.R.** (`/mer/`).
7. Probar el **convertidor de moneda** en `/convertir-moneda/`.
8. Mencionar la integración con **Kafka** (productor y comandos para levantarlo).
9. Mostrar el **logging** (`logs/django_errors.log`) y el monitoreo con **Sentry** (evento de error).
10. Ejecutar el proyecto con **HTTPS local** usando `python manage.py runsslserver 127.0.0.1:8000`
    y acceder a `https://127.0.0.1:8000/` aceptando el certificado autofirmado.

---

## 📖 Manual de usuario

El manual de usuario detallado está disponible en formato PDF en este repositorio.  
Puedes descargarlo o visualizarlo aquí:  
[Manual de usuario NUAM (PDF)](Manual%20de%20usuario%20NUAM.pdf)
#   n u a m _ p r o j e c t _ 3 
 
 