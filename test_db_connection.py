import psycopg2
try:
    conn = psycopg2.connect(
        dbname="artesano_db",
        user="postgres",
        password="123456789", # Asegúrate de que esta sea la contraseña correcta
        host="127.0.0.1",
        port="5432",
        client_encoding="UTF8"
    )
    print("Conexión exitosa a PostgreSQL!")
    conn.close()
except Exception as e:
    print(f"Error al conectar: {e}")