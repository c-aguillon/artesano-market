# Artesano Market

Marketplace Django para que artesanos locales publiquen y vendan sus productos.

## Stack

- Backend: Python 3, Django 5.2.5
- Frontend: HTML, CSS y JavaScript con `fetch`
- Base de datos: SQLite por defecto, PostgreSQL opcional
- Pagos: PayPal Sandbox
- PWA: `manifest.webmanifest`, service worker y persistencia de carrito con IndexedDB

## Estructura

```text
artesano-market/
├── .env.example
├── requirements.txt
├── web/
│   ├── manage.py
│   ├── WebApp/
│   │   ├── static/WebApp/js/
│   │   └── templates/WebApp/
│   ├── blog/
│   ├── carro/
│   ├── cuentas/
│   ├── pagos/
│   └── web/
```

## Puesta en marcha

1. Clona el repositorio y entra al proyecto:

```bash
git clone https://github.com/TU_USUARIO/artesano-market.git
cd artesano-market
```

2. Crea y activa el entorno virtual:

```bash
python -m venv venv
```

Windows:

```bash
.\venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Copia `.env.example` a `.env` o exporta variables de entorno.

Notas:
- Si no defines `POSTGRES_DB`, el proyecto usara SQLite automaticamente.
- Para habilitar PayPal en desarrollo, define `PAYPAL_CLIENT_ID` y `PAYPAL_CLIENT_SECRET`.
- Para correo SMTP, rellena `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD`.

5. Entra al proyecto Django:

```bash
cd web
```

6. Ejecuta migraciones:

```bash
python manage.py migrate
```

7. Crea un superusuario:

```bash
python manage.py createsuperuser
```

8. Inicia el servidor:

```bash
python manage.py runserver
```

## Carrito persistente

- El carrito se guarda en sesion, en el perfil del usuario y en IndexedDB del navegador.
- Si el usuario cierra sesion o el navegador, al volver a entrar se intenta restaurar el carrito.
- El checkout sigue leyendo el carrito del servidor para no comprometer el flujo de pago.
