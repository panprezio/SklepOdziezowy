from db.db import connect

class Customer:
    @staticmethod
    def get_all():
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, first_name, last_name, email FROM customers")
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def add(first_name, last_name, email):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (first_name, last_name, email, password_hash, created_at) VALUES (%s, %s, %s, '', NOW())",
                       (first_name, last_name, email))
        conn.commit()
        conn.close()