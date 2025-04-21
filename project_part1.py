import mysql.connector
from datetime import datetime
from mysql.connector import errorcode
""" A lot of the connection stuff here is adapted from teh safe connection with helper functions shared connections file from class"""

def reorder(store: int, cnx: mysql.connector.connection):

    # check if connection is open
    if cnx is None or not cnx.is_connected():
        raise ValueError("The connection was not connected")

    # use cursor for sql queries
    try: 

        # run a select query that gets us the products that store sells, its inventory, the brand, and vendor id and the vendor's price for each product.
        with cnx.cursor() as cursor:
            cursor.execute("""SELECT SELL.upc, SELL.max_inventory, SELL.current_inventory,  PRODUCT.brand_id, VENDOR.vendor_id, VENDOR_PRODUCTS.unit_price 
                           FROM SELL JOIN PRODUCT ON SELL.UPC = PRODUCT.UPC 
                           JOIN BRAND ON PRODUCT.brand_id = BRAND.brand_id 
                           JOIN VENDOR ON VENDOR.vendor_id = BRAND.vendor_id 
                           JOIN VENDOR_PRODUCTS ON VENDOR.vendor_id = VENDOR_PRODUCTS.vendor_id AND PRODUCT.UPC = VENDOR_PRODUCTS.UPC 
                           WHERE SELL.store_id = %s;""", (store,))
            rows = cursor.fetchall()

    
            # find the difference between max and current inventory, and append that to a list as a tuple with the vendor id and the unit price
            differences = []
            for row in rows:
                upc = row[0]
                max_inv = row[1]
                current_inv = row[2]
                vendor_id = row[4]
                unit_price = row[5]
                # calculate difference
                diff = max_inv - current_inv
                # append as a tuple
                if diff > 0:
                    differences.append((upc, diff, vendor_id, unit_price))
            
            # sort just because
            differences.sort()
            
            # get all the current reorders
            cursor.execute("""SELECT UPC, SUM(quantity_requested) 
                           FROM REORDER_REQUEST WHERE store_id = %s 
                           GROUP BY UPC;""", (store,))

            rows2 = cursor.fetchall()

            # append reorder info to dict
            ordered = {}
            for row in rows2:
                upc = row[0]
                qty = row[1]
                ordered[upc] = qty

            # check the shipments
            cursor.execute("""SELECT REORDER_REQUEST.UPC, SUM(REORDER_REQUEST.quantity_requested)
                FROM SHIPMENT
                JOIN REORDER_REQUEST ON SHIPMENT.reorder_id = REORDER_REQUEST.reorder_id
                WHERE SHIPMENT.received_date IS NULL AND REORDER_REQUEST.store_id = %s
                GROUP BY REORDER_REQUEST.UPC;""", (store,))

            rows3 = cursor.fetchall()
           
            # store info in a dict
            shipped = {}
            for row in rows3:
                upc = row[0]
                qty = row[1]
                shipped[upc] = qty

            # variables to track stats for printing at the end
            reorders_vendor = {}
            new_reorders = []
            total_cost = 0
            # loop over the 1ist result of the first select query to see which which items need to be reordered and what qty
            for upc, diff, vendor_id, unit_price in differences:
                
                # return 0 if UPC not in ordered or shipped
                already_ordered = ordered.get(upc, 0)
                already_shipped = shipped.get(upc, 0)
                to_order = diff - already_ordered - already_shipped
                
                if to_order > 0:
                    #insert our new values 
                    try:
                        # insert the new reorder request, with the current time and total cost
                        cost = unit_price * to_order
                        cursor.execute("""INSERT INTO REORDER_REQUEST 
                                       (reorder_date, quantity_requested, total_cost, seen_status, vendor_id, UPC, store_id)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s);""", (datetime.now(), to_order, cost, False, vendor_id, upc, store))
                        
                        # update these variables to print later.
                        total_cost += cost
                        vendors_reorders = reorders_vendor.get(vendor_id, 0)
                        reorders_vendor[vendor_id] = vendors_reorders + 1
                        new_reorders.append((upc, to_order))
                    except mysql.connector.Error:
                        raise ValueError("something went wrong adding order to reorder requests")
            
            cnx.commit()
            if total_cost > 0:
                # print the info as instructed in the project doc
                print(f"Summary for store {store}")
                print("-" * 10)
                
                print(f"total cost of this batch of reorders = {total_cost}")
                
                print("-" * 10)

                for upc, qty in new_reorders:
                    print(f"ordered {qty} of item {upc}")
                print("-" * 10)
                for vid, i in reorders_vendor.items():
                    print(f"vendor {vid} has to fullful {i} order(s)")
            else:
                print(f"Inventory is up to date for store {store}")

    
    except mysql.connector.Error as err:
        print('Error while executing', cursor.statement, '--', str(err))

        # to "reset" the database back to its original state if sql queries fail
        cnx.rollback()

""""
Summary for store 1
----------
total cost of this batch of reorders = 5599.82
----------
ordered 44 of item 0000000000000002
ordered 127 of item 0000000000000003
ordered 24 of item 0000000000000005
ordered 46 of item 0000000000000006
ordered 3 of item 0000000000000008
ordered 2 of item 0000000000000010
ordered 82 of item 0000000000000011
----------
vendor 1 has to fullful 5 order(s)
vendor 2 has to fullful 2 order(s)


"""


"""
Summary for store 2
----------
total cost of this batch of reorders = 8370.53
----------
ordered 33 of item 0000000000000001
ordered 31 of item 0000000000000002
ordered 27 of item 0000000000000003
ordered 36 of item 0000000000000004
ordered 46 of item 0000000000000005
ordered 14 of item 0000000000000006
ordered 77 of item 0000000000000007
ordered 17 of item 0000000000000008
ordered 55 of item 0000000000000009
ordered 115 of item 0000000000000010
ordered 40 of item 0000000000000011
ordered 116 of item 0000000000000012
----------
vendor 1 has to fullful 7 order(s)
vendor 2 has to fullful 5 order(s)
True


"""
