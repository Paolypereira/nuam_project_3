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

| Herramienta        | Windows                                                             | Linux/Ubuntu                                        |
|--------------------|---------------------------------------------------------------------|-----------------------------------------------------|
| **Python 3.10+**   | ✅ [Descargar desde python.org](https://www.python.org/downloads/)  | `sudo apt install python3 python3-venv python3-pip` |
| **Git**            | ✅ [Descargar desde git-scm.com](https://git-scm.com/downloads)     | `sudo apt install git`                              |

---

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio

git clone https://github.com/Paolypereira/nuam_project2.git
cd nuam_project

text

### 2️⃣ Crear entorno virtual

**Windows PowerShell:**

python -m venv .venv
..venv\Scripts\Activate.ps1

text

**Linux / Ubuntu:**

python3 -m venv .venv
source .venv/bin/activate

text

⚠️ En Windows, si aparece error al activar el entorno, ejecuta PowerShell como Administrador y usa:

Set-ExecutionPolicy RemoteSigned

text

### 3️⃣ Instalar dependencias

pip install -r requirements.txt

text

### 4️⃣ Aplicar migraciones de base de datos

python manage.py migrate

text

### 5️⃣ Cargar países base (Chile, Colombia, Perú)

python manage.py cargar_paises

text

### 6️⃣ Cargar datos bursátiles desde Excel

El archivo Excel está en:

cargas/2025/10/Informe_Bursatil_Regional_2025-08.xlsx

text

Pasos para importar:

- Copia la ruta del archivo completo (en Windows clic derecho → “Copiar como ruta”).  
- Ejecuta:

python manage.py seed_empresas --file "ruta_completa_a_tu_excel.xlsx"

text

El sistema detectará y mostrará resultados como:

✅ Empresas creadas: 0, actualizadas: 159, omitidas: 72

text

### 7️⃣ Ejecutar el servidor de desarrollo

**Windows:**

python manage.py runserver

text

**Linux / Ubuntu:**

python3 manage.py runserver

text

### 8️⃣ Abrir el sitio en el navegador

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🖥️ Interfaz principal y usuarios

Al ingresar verás estas opciones:

| Sección                 | Descripción                                        |
|-------------------------|----------------------------------------------------|
| 🏢 Catálogo de Empresas   | Visualiza las empresas cargadas desde Excel.     |
| ⚙️ Panel Admin           | CRUD completo mediante Django Admin.              |
| 🧩 Diagrama NUAM (M.E.R) | Visualización del modelo de datos.               |
| 🔄 Convertidor de moneda  | Para convertir entre CLP, COP, PEN y USD.       |
| 🔌 API REST              | Acceso a la API REST y documentación Swagger UI. |

### Usuario para login

- Crear su propio superusuario 

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

- Visualiza Swagger UI en: `/swagger/`  
- Documentación ReDoc en: `/redoc/`  

Permite explorar, probar y validar los endpoints directamente.

---

## 🧩 Modelo Entidad-Relación (M.E.R)

- Imagen: `static/diagramas/MER_NUAM2.0.png`  
- Vista dedicada en: `/mer/` (permite zoom con la rueda del mouse).  
- Entidades principales: País, Empresa, Normativa, Calificación Tributaria, Instrumentos No Inscritos, Historial de Cambios, Valor de Instrumentos.

---

## 🛡️ Manejo de errores, logging y seguridad

- Páginas personalizadas para errores 404 y 500 en `templates/errors/`.  
- Archivo de logs para errores: `logs/django_errors.log`.  
- Preparado para https y seguridad avanzada en `settings.py` (cookies seguras, HSTS, XSS, etc.).

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

text

---

## 🎓 Sugerencia de recorrido para la evaluación

1. Mostrar el **dashboard** (`/`) con tarjetas activas.  
2. Navegar el **catálogo** (`/catalogo/`) mostrando importación desde Excel.  
3. Mostrar el **panel admin** (`/admin/`) con CRUD de Empresas.  
4. Demostrar la **API** (`/api/empresas/`, `/api/paises/`).  
5. Explorar la documentación en `/swagger/` y `/redoc/`.  
6. Ver el diagrama **M.E.R.** (`/mer/`).  
7. Probar el convertidor en `/convertir-moneda/`.  
8. Mencionar la integración con Kafka y manejo de logs.