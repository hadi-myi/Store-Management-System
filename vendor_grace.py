# Vendor Function

import mysql.connector

from mysql.connector import errorcode

def shipment(store : int, delivery_date : str, reorders : list [int], shipment_items : dict, cnx : mysql.connector.connection):

 # check if connection is open
    if cnx is None or not cnx.is_connected():
        raise ValueError("The connection was not connected")

    try: 
        with cnx.cursor() as cursor:

            # This query selects all of the reorder_requests for the given store, only including the ones the shipment is fufilling
            cursor.execute("SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested, REORDER_REQUEST.reorder_id FROM REORDER_REQUEST WHERE REORDER_REQUEST.store_id = %s AND REORDER_REQUEST.reorder_id IN %s", (store, reorders))
            products = cursor.fetchall()

            for x in products:
                if shipment_items.get(x[0]) == None: 
                    raise ValueError(x, " is an invalid shipment item!")
                
                cur_quantity = shipment_items.get(x[0]) 
                fufilled_orders = []

                if cur_quantity >= x[1]:
                    # update dictionary to new current quantity of that item x[1] - cur_quantity
                    fufilled_orders.append(x[2])

                else:
                    print("WARNING there is not enough of product: ", x[0], " to fufill reorder_request " + x[2])
                    print("Would you like to continue with the current shipment process? \n If you do so not all of your reorder_requests will be fufilled.")
                    pref = input("Enter y for yes or n for no")

                    if pref == "n":
                        raise ValueError("CURRENT SHIPMENT HAS BEEN CANCELLED")

    except  mysql.connector.Error as err:
        print('Error while executing', cursor.statement, '--', str(err))

        # to "reset" the database back to its original state if sql queries fail
        cnx.rollback()
