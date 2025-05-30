from db.db import connect

class Product:
    @staticmethod
    def get_all():
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, name, price FROM products")
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def add(name, price):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, created_at) VALUES (%s, %s, NOW())", (name, price))
        conn.commit()
        conn.close()