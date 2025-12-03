# 🌐 NUAM – Mantenedor Bursátil y API Regional

**NUAM** es una aplicación desarrollada en **Django + Django REST Framework**, que permite administrar información bursátil de los mercados de **Chile, Colombia y Perú**.  
El proyecto incluye un **panel administrativo**, una **API funcional**, un **catálogo de empresas**, y un **modelo de datos (M.E.R)** accesible desde la interfaz principal.

---Comentario del Profe:

## 📁 Estructura general del proyecto


---

## ⚙️ Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

| Herramienta | Windows | Linux/Ubuntu |
|--------------|----------|--------------|
| **Python 3.10+** | ✅ [Descargar desde python.org](https://www.python.org/downloads/) | `sudo apt install python3 python3-venv python3-pip` |
| **Git** | ✅ [Descargar desde git-scm.com](https://git-scm.com/downloads) | `sudo apt install git` |

---

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/Paolypereira/nuam_project.git

cd nuam_project

2️⃣ Crear entorno virtual
🪟 En Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

🐧 En Linux / Ubuntu
python3 -m venv .venv
source .venv/bin/activate

⚠️ Nota:
En Windows, si aparece un error de permisos al activar el entorno virtual, ejecuta PowerShell como **Administrador** una sola vez y usa el comando:
`Set-ExecutionPolicy RemoteSigned`
Luego puedes seguir los pasos normalmente.

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Aplicar migraciones de base de datos
python manage.py migrate

5️⃣ Cargar países base (Chile, Colombia, Perú)
python manage.py cargar_paises

6️⃣ Cargar datos bursátiles desde Excel

El archivo de datos bursátiles se encuentra dentro del proyecto, en la carpeta:

nuam_project\cargas\2025\10\Informe_Bursátil_Regional_2025-08.xlsx

🧩 Paso a paso

    1️⃣ Abre la carpeta del proyecto en Visual Studio Code o en la terminal.

    2️⃣ Confirma que la ruta del archivo existe. En Windows, puedes copiar la ruta completa desde el Explorador de Archivos:

    Haz clic derecho sobre el archivo → “Copiar como ruta”

    Pégala entre comillas en el siguiente comando.

    3️⃣ Ejecuta el comando en la terminal (reemplazando si es necesario la ruta según tu usuario):

    python manage.py seed_empresas --file "C:\Users\alumnosnunoa\nuam_project\cargas\2025\10\Informe_Bursátil_Regional_2025-08.xlsx"

    4️⃣ Si el archivo está en una ruta distinta, usa la ruta que copiaste en el paso 2.

    5️⃣ El sistema detectará automáticamente la hoja Nemo-Cap. Bur|Ticker-Market Cap y mostrará un resultado similar a:

    ✅ Empresas creadas: 0, actualizadas: 159, omitidas: 72

    Esto significa que los datos fueron importados correctamente a la base de datos.

    

7️⃣ Ejecutar el servidor de desarrollo
Windows:
python manage.py runserver

Linux / Ubuntu:
python3 manage.py runserver

8️⃣ Luego abre tu navegador en:
👉 http://127.0.0.1:8000/

🧩 Usuario sugerido 
usuario: profe
contraseña: profe1234

🖥️ Interfaz principal

Al acceder al sitio verá tres opciones:

Sección	Descripción
🏢 Catálogo de Empresas	Visualiza las empresas cargadas desde el Excel.
⚙️ Panel Admin	CRUD completo mediante Django Admin.
🧩 Diagrama NUAM (M.E.R)	Visualización del modelo de datos.
🔗 Enlaces importantes
URL	Descripción
/	Página principal con enlaces
/admin/	Panel administrativo
/api/	API Django REST Framework
/api/empresas/	Listado y CRUD vía API
/api/paises/	Consulta de países
/api/top-empresas/?pais=CHL&n=5	Empresas con mayor capitalización
/static/diagramas/ERD_NUAM.png	Diagrama Entidad–Relación
/api/demo/empresas/	Catálogo visual (HTML + JS)


🧱 Tecnologías utilizadas

Django 5.2.7

Django REST Framework

drf-spectacular (documentación OpenAPI)

django-filter

SQLite3

HTML + CSS + JS

🧩 Modelo Entidad-Relación (M.E.R)

Ubicado en:

/static/diagramas/ERD_NUAM.png


Representa las entidades principales:

País

Empresa

Normativa

Calificación Tributaria

Instrumentos No Inscritos

Historial de Cambios

Valor de Instrumentos

🧹 Archivos ignorados por Git

El archivo .gitignore incluye:

*.pyc
__pycache__/
.env
.venv/
db.sqlite3
*.xlsx
/staticfiles/

✅ Autores

Proyecto académico NUAM
Desarrollado por el equipo de estudiantes de Analista Programador - INACAP
    -   Jenny Latorre
    -   Yamilet Maldonado
    -   Paola Pereira


🧾 Ejemplo de ejecución rápida (Linux)
git clone https://github.com/Paolypereira/nuam_project.git
cd nuam_project/nuam_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py cargar_paises
python3 manage.py seed_empresas --file "Informe_Bursátil_Regional_2025-08.xlsx"
python3 manage.py runserver
Luego abrir:
👉 http://127.0.0.1:8000/

🧠 Recomendación para evaluación en máquina virtual (Linux/Ubuntu)

Si ejecuta en un entorno limpio:

Clonar el repositorio y seguir las instrucciones desde el paso 2.

Verificar que el entorno tiene permisos de lectura/escritura en la carpeta del proyecto.

Asegurar que el archivo Excel esté en la raíz del proyecto antes de ejecutar seed_empresas.

Acceder desde el navegador interno o externo a http://127.0.0.1:8000/

Ingresar al panel admin con:

usuario: profe
contraseña: profe1234
