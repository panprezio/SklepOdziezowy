from db.db import connect

class OrderItem:
    @staticmethod
    def add(order_id, variant_id, quantity, unit_price):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO order_items (order_id, variant_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                       (order_id, variant_id, quantity, unit_price))
        conn.commit()
        conn.close()