import mysql.connector
from mysql.connector import errorcode
# Lots code here is from from thr safe connection with helper functions shared connections file from class

def online_order(store_id: int, customer_id: int, order_items: dict, cnx: mysql.connector.connection):
    """ Function responsible for placing an online order. This function is a bit of a mess, but it works, so whatever.
    : param store_id: The ID of the store to order from.
    : param customer_id: The ID of the customer placing the order.
    : param order_items: A dictionary of items to order, where the key is the UPC and the value is the quantity.
    : param cnx: An open SQL connection.
    : raises ValueError: If the SQL connection is not open. IDK if a ValueError is the right type of error here for a
    bad SQL connection but it is an argument with an invalid value, so technically?
    """

    # Since the connection is passed in as an argument, we might want to double-check that it's actually open
    if cnx is None or not cnx.is_connected():
        raise ValueError("The connection wasn't connected, baka!")

    # Same, but now with a cursor for your SQL work
    try:
        # Open a cursor for SQL work
        with cnx.cursor() as cursor:
             # check if store exists
            cursor.execute("SELECT store_id FROM STORE WHERE store_id = %s;", (store_id,))
            if not cursor.fetchall():
                print(f"Invalid store {store_id}")
                return

            # check if customer exists
            cursor.execute("SELECT customer_id FROM CUSTOMER WHERE customer_id = %s;", (customer_id,))
            if not cursor.fetchall():
                print(f"Invalid customer {customer_id}")
                return
            
            insufficient_inventory = []
            total_price = 0
            items_to_add = []

            # loop through the order items
            # check if the item exists in the store
            for upc, qty in order_items.items():
                # Check if the item is in stock
                cursor.execute("""SELECT s.current_inventory, s.overriden__price, p.product_name 
                               FROM SELL AS s JOIN PRODUCT AS p ON s.upc = p.upc 
                               WHERE s.store_id = %s AND s.upc = %s;""", 
                               (store_id, upc))
                # get the result
                result = cursor.fetchall()

                if not result:
                    print(f"Item {upc} not found in store {store_id}.")
                    continue
                # Access info from result
                row = result[0]
                current_inventory = row[0]
                overridden_price = row[1]
                product_name = row[2]

                # Check if the quantity is available
                if current_inventory < qty:
                    print(f"Insufficient inventory for item {product_name} (UPC: {upc}), requested: {qty}, in stock: {current_inventory}")
                    insufficient_inventory.append((upc, qty))

                    #Check the stores state
                    cursor.execute("SELECT store_region FROM STORE WHERE store_id = %s;", (store_id,))
                    region_result = cursor.fetchall()

                    if not region_result:
                        print(f"Could not find a store in {store_id}. ")
                        return
                    region = region_result[0][0]
                    print(f"Store {store_id} is located in region: {region}")

                    cursor.execute("""
                        SELECT s.store_id, s.current_inventory
                        FROM SELL AS s
                        JOIN STORE AS st ON s.store_id = st.store_id
                        WHERE s.upc = %s AND s.current_inventory >= %s AND st.store_region = %s AND s.store_id != %s
                    """, (upc, qty, region, store_id))

                    other_store_results = cursor.fetchall()

                    if other_store_results:
                        for other_store_id, inv in other_store_results:
                            print(f"Store {other_store_id} in region {region} has enough stock {inv} of item {upc}")
                    else:
                        print(f"No other stores in region {region} have enough stock for item {upc}")

                else:
                    # Calculate the total price
                    total_price += overridden_price * qty
                    items_to_add.append((store_id, customer_id, upc, qty))
            if insufficient_inventory:
                print("Some items could not be ordered because of insufficient inventory:")
                for upc, qty in insufficient_inventory:
                    print(f"UPC: {upc}, Quantity: {qty}")
                 # Log failed order in the ORDERS table with order_status = 0
                cursor.execute("""
                    INSERT INTO ORDERS (order_type, order_status, order_date, total_order_price, store_id, customer_id)
                    VALUES (%s, %s, NOW(), %s, %s, %s);
                """, (1, 0, 0.00, store_id, customer_id))
                cnx.commit()  # Save this failed order attempt to the database

                return
            
            print("Inventory verified. Ready to place order.")
            print("Total price:", total_price)
            print("Items:")
            for _, _, upc, qty in items_to_add:
                print(f"UPC: {upc}, Quantity: {qty}")
            # Insert the order into ORDERS
            cursor.execute(
                "INSERT INTO ORDERS (order_type, order_status, order_date, total_order_price, store_id, customer_id) VALUES (%s, %s, NOW(), %s, %s, %s);",
                (1, 1, total_price, store_id, customer_id)
            )

            # Get the most recent order_id for this customer at this store
            cursor.execute(
                "SELECT MAX(order_id) FROM ORDERS WHERE customer_id = %s AND store_id = %s;",
                (customer_id, store_id)
            )
            order_id = cursor.fetchall()[0][0]

            # Insert each item into ORDER_INCLUDES and update inventory
            for store_id, customer_id, upc, qty in items_to_add:
                cursor.execute(
                    "INSERT INTO ORDER_INCLUDES (order_id, UPC, buying_quantity) VALUES (%s, %s, %s);",
                    (order_id, upc, qty)
                )
                cursor.execute(
                    "UPDATE SELL SET current_inventory = current_inventory - %s WHERE store_id = %s AND UPC = %s;",
                    (qty, store_id, upc)
                )

            # Commit changes
            cnx.commit()

            # Confirmation
            print(f"Order {order_id} placed successfully for customer {customer_id} at store {store_id}")
            print("Items Ordered:")
            for _, _, upc, qty in items_to_add:
                print(f"UPC: {upc}, Quantity: {qty}")
            print("Total price:", total_price)

    # This code should handle any issues DURING SQL work.
    except mysql.connector.Error as err:
        print('Error while executing', cursor.statement, '--', str(err))

        # If some part of our SQL queries errored, explicitly rollback all of them
        # to "reset" the database back to its original state. Only needed for SQL
        # queries that alter the database.
        cnx.rollback()