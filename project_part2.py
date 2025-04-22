# Vendor Function

import mysql.connector

from mysql.connector import errorcode

def shipment(store : int, delivery_date : str, reorders : list [int], shipment_items : dict, shipment_no : int, vendor : int, cnx : mysql.connector.connection):

 # check if connection is open
    if cnx is None or not cnx.is_connected():
        raise ValueError("The connection was not connected")

    try: 
        with cnx.cursor() as cursor:

            # This line of code was taken from https://www.thecoderscamp.com/mysql-connector-mysqlinterfaceerror-python-type-list-cannot-be-converted/. 
            # This is used to reformat the reorder list into a string so that the mysql execute function can read it properly

            #reorder_string = ",".join(str(x) for x in reorders)
            #reorder_placeholder = ', '.join("%s" for x in reorders)
            #print(reorder_string, reorder_placeholder)
            #store_placeholder = "%s"

            # This query selects all of the reorder_requests for the given store, only including the ones the shipment is fufilling AND REORDER_REQUEST.reorder_id IN %s
           # first_query = "SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested, REORDER_REQUEST.reorder_id FROM REORDER_REQUEST WHERE REORDER_REQUEST.store_id = {} AND REORDER_REQUEST.reorder_id IN ({});".format(store, reorder_string)
            #cursor.execute(first_query)

            cursor.execute("SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested, REORDER_REQUEST.reorder_id FROM REORDER_REQUEST WHERE REORDER_REQUEST.store_id = %s AND REORDER_REQUEST.vendor_id = %s", (store, vendor))
            products = cursor.fetchall()

            fufilled_orders = []

            for x in products:
                if x[2] in reorders:
                    if shipment_items.get(x[0]) == None: 
                        raise ValueError(x[0] + " is an invalid shipment item!")
                    
                    cur_quantity = shipment_items.get(x[0]) 

                    if cur_quantity >= x[1]:
                        # update dictionary to new current quantity of that item x[1] - cur_quantity
                        shipment_items[x[0]] = x[1] - cur_quantity
                        fufilled_orders.append((x[0], x[1], x[2]))


                    else:
                        print("WARNING there is not enough of product: ", x[0], " to fufill reorder_request " + str(x[2]))
                        print("Would you like to continue with the current shipment process? \n If you do so not all of your reorder_requests will be fufilled.")
                        pref = input("Enter y for yes or n for no: ")

                        if pref == "n":
                            raise ValueError("CURRENT SHIPMENT HAS BEEN CANCELLED")

            print("The Current Orders are out for delivery: ")           
            for x in fufilled_orders:
                print("Order #" + str(x[2]))
                cursor.execute("INSERT INTO SHIPMENT (shipment_no, reorder_id, expected_delivery) VALUES (%s, %s, %s);", (shipment_no, x[2], delivery_date))
                cnx.commit()

            print("Store #" + str(store) + " Manifest:")
            print("Expected Date and Time of Delievery: " + delivery_date)
            print("QUANTITY | ITEM")
         
            for x in fufilled_orders:
                print(x[0])
                cursor.execute("SELECT PRODUCT.product_name FROM PRODUCT WHERE PRODUCT.UPC = %s", ([x[0]]))
                item = cursor.fetchall()
                print(" ", x[1], ": " + item[0][0])

            print("\nThere is currently:" + str((len(products) - len(fufilled_orders))) + " order(s) left for store #", store)
            cursor.execute("SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested, REORDER_REQUEST.reorder_id FROM REORDER_REQUEST WHERE REORDER_REQUEST.vendor_id = %s",  ([vendor]))
            selected_vendor = cursor.fetchall()
            print("There is currently:" + str((len(selected_vendor) - len(fufilled_orders))) + " BMART order(s) left for vendor #", vendor)

            

    except  mysql.connector.Error as err:
        print('Error while executing', cursor.statement, '--', str(err))

        # to "reset" the database back to its original state if sql queries fail
        cnx.rollback()
        
