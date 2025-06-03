from db.db import connect
from models.order_items import OrderItem

class Order:
    @staticmethod
    def get_all():
        conn = connect()
        cursor = conn.cursor()
        query = """
        SELECT 
            o.order_id,
            CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
            o.order_date,
            o.status,
            p.name AS product_name,
            pv.size,
            pv.color,
            oi.quantity,
            oi.unit_price,
            ROUND(oi.quantity * oi.unit_price, 2) AS total_price
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        ORDER BY o.order_id
        """
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def update(order_id, customer_id, product_name, variant_id, quantity, status):
        try:
            conn = connect()
            with conn.cursor() as cursor:

                cursor.execute("""
                               SELECT pv.size, pv.color, p.price
                               FROM product_variants pv
                                        JOIN products p ON pv.product_id = p.product_id
                               WHERE pv.variant_id = %s
                                 AND p.name = %s
                               """, (variant_id, product_name))
                variant_row = cursor.fetchone()

                if not variant_row:
                    print("Nie znaleziono wariantu lub produktu.")
                    conn.rollback()
                    return False

                size, color, unit_price = variant_row
                total_price = quantity * float(unit_price)


                cursor.execute("""
                               UPDATE orders
                               SET customer_id = %s,
                                   status      = %s,
                                   total_price = %s
                               WHERE order_id = %s
                               """, (customer_id, status, total_price, order_id))




                OrderItem.update(order_id, variant_id, quantity, unit_price)



            conn.commit()
            return True

        except Exception as e:
            print(f"Order update error: {e}")
            if conn:
                conn.rollback()
            return False

        finally:
            conn.close()

    @staticmethod
    def delete(order_id):
        try:
            OrderItem.delete_by_order(order_id)
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Order delete error: {e}")
            return False

