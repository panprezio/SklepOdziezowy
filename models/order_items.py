from db.db import connect

class OrderItem:
    @staticmethod
    def add(order_id, variant_id, quantity, unit_price):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO order_items (order_id, variant_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, variant_id, quantity, unit_price))
        conn.commit()
        conn.close()

    @staticmethod
    def update(order_id, variant_id, quantity, unit_price):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
                       UPDATE order_items
                       SET variant_id = %s,
                           quantity   = %s,
                           unit_price = %s
                       WHERE order_id = %s
                       """, (variant_id, quantity, unit_price, order_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_by_order(order_id):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_order(order_id):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT oi.variant_id, oi.quantity, oi.unit_price, p.name, pv.size, pv.color
            FROM order_items oi
            JOIN product_variants pv ON oi.variant_id = pv.variant_id
            JOIN products p ON pv.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        result = cursor.fetchall()
        conn.close()
        return result
