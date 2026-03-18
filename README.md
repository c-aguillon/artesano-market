# Tecnologías Utilizadas

* **Backend:** Python 3, Django 5.2.5
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API, Handlebars.js)
* **Base de Datos:** SQLite / PostgreSQL
* **Otros:** Pillow (Gestión de imágenes)

---

## Guía de Instalación y Ejecución Local

Para ejecutar este proyecto en tu entorno local, sigue estos pasos al pie de la letra. Las instrucciones cubren tanto entornos Windows como Linux/macOS.

### 1. Clonar el repositorio
Abre tu terminal y ejecuta:
```
git clone [https://github.com/TU_USUARIO/artesano-market.git](https://github.com/TU_USUARIO/artesano-market.git)
cd artesano-market
``` 

## 2. Crear y activar entorno virtual
_Windows:_

```
python -m venv venv
.\venv\Scripts\activate
```

_Mac/Linux:_

```
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar dependencias

```
pip install -r requirements.txt
```

## 4. Configuración de Base de Datos (PostgreSQL)
Entrar a <ins>settings.py</ins> 

```
cd/web/web
```
Editar la siguiente linea:
```
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
```

### 4.5. **Entrar a la carpeta del proyecto (¡IMPORTANTE!)**

```
cd web
```

## 5. Aplicar Migraciones

```
python manage.py migrate
```

## 6. Crear Superusuario (Administrador)

```
python manage.py createsuperuser
```

## 7. Ejecutar el servidor

```
python manage.py runserver
```