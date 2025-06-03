from db.db import connect

class Product:
    @staticmethod
    def get_all():
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT p.product_id, p.name, p.description, p.price,
                   c.name AS category, b.name AS brand, p.created_at
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            ORDER BY p.product_id
        """
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def add(name, price, description=None, category_id=None, brand_id=None):
        conn = connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO products (name, price, description, category_id, brand_id, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (name, price, description, category_id, brand_id))
        conn.commit()
        conn.close()
