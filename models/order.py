from db.db import connect

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
    def add(customer_name, product_name, quantity):

        pass

    @staticmethod
    def update(order_id, new_customer_name, new_product_name, new_qty):

        pass

    @staticmethod
    def delete(order_id):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
        conn.close()
