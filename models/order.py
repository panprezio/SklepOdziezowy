from db.db import connect

class Order:
    @staticmethod
    def get_all():
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, customer_id, order_date, total_price FROM orders")
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def add(customer_id, total_price):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (customer_id, order_date, total_price, status) VALUES (%s, NOW(), %s, 'nowe')", (customer_id, total_price))
        conn.commit()
        conn.close()