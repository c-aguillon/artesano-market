## Stack Tecnológico

* **Backend:** Python 3.12, Django 5.2.5.
* **Base de Datos:** PostgreSQL (Relacional).
* **Frontend:** HTML5, CSS3 (Custom Properties), Bootstrap 4, JavaScript Vanilla.
* **Control de Versiones:** Git.

## Instalación y Configuración Local

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/TU_USUARIO/artesano-market.git](https://github.com/TU_USUARIO/artesano-market.git)
cd artesano-market

2. Crear y activar entorno virtual
Windows:

python -m venv venv
.\venv\Scripts\activate

Mac/Linux:

python3 -m venv venv
source venv/bin/activate

3. Instalar dependencias

pip install -r requirements.txt

4. Configuración de Base de Datos (PostgreSQL)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'artesano_db',
        'USER': 'postgres',      # Tu usuario
        'PASSWORD': 'tu_password', # Tu contraseña
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

5. Aplicar Migraciones

python manage.py migrate

6. Crear Superusuario (Administrador)

python manage.py createsuperuser

7. Ejecutar el servidor

python manage.py runserver

