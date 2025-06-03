from db.db import connect

class Customer:
    @staticmethod
    def get_all():
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT customer_id, first_name, last_name, email FROM customers")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            print(f"Błąd podczas pobierania klientów: {e}")
            return []

    @staticmethod
    def add(first_name, last_name, email):
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO customers (first_name, last_name, email, password_hash, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (first_name, last_name, email, '')
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Błąd podczas dodawania klienta: {e}")
