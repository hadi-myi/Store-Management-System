import mysql.connector

from mysql.connector import errorcode
""" A lot of the connection stuff here is adapted from teh safe connection with helper functions shared connections file from class"""

def reorder(store: int, cnx: mysql.connector.connection):

    # check if connection is open
    if cnx is None or not cnx.is_connected():
        raise ValueError("The connection was not connected")

    # use cursor for sql queries
    try: 
        with cnx.cursor() as cursor:
            cursor.execute("SELECT SELL.upc, SELL.max_inventory, SELL.current_inventory, PRODUCT.product_name,  PRODUCT.brand_id, VENDOR.vendor_id FROM SELL JOIN PRODUCT ON SELL.UPC = PRODUCT.UPC JOIN BRAND ON PRODUCT.brand_id = BRAND.brand_id JOIN VENDOR ON VENDOR.vendor_id = BRAND.vendor_id WHERE SELL.store_id = 1;")
            rows = cursor.fetchall()

            # print header
            print("UPC | Max Inventory | Current Inventory | Product Name | Brand ID | Vendor ID")
            print("-" * 80)

            for row in rows:
                print(" | ".join(str(value) for value in row))

            # find the difference between max and current inventory, and append that to a list as a tuple
            differences = []
            for row in rows:
                upc = row[0]
                max_inv = row[1]
                current_inv = row[2]
                # calculate difference
                diff = max_inv - current_inv
                # append as a tuple
                differences.append((upc, diff))
            differences.sort()
            print(differences)

            cursor.execute("SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested FROM REORDER_REQUEST JOIN PRODUCT ON REORDER_REQUEST.UPC = PRODUCT.UPC JOIN BRAND ON PRODUCT.brand_id = BRAND.brand_id JOIN VENDOR ON BRAND.vendor_id = VENDOR.vendor_id;")

            rows2 = cursor.fetchall()

            reorders = []
            for row in rows2:
                reorders.append(row)
            reorders.sort()
            print(reorders)
            
            # source: https://stackoverflow.com/questions/1663807/how-do-i-iterate-through-two-lists-in-parallel

            for a, b in zip(differences, reorders):
                print(a,b)
            
            
    
    except mysql.connector.Error as err:
        print('Error while executing', cursor.statement, '--', str(err))

        # to "reset" the database back to its original state if sql queries fail
        cnx.rollback()