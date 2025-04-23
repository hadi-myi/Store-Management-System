# Vendor Function

import mysql.connector

from mysql.connector import errorcode



def shipment(store : int, delivery_date : str, reorders : list [int], shipment_items : dict, shipment_no : int, vendor : int, cnx : mysql.connector.connection):
    """This function takes in 7 parameters: 
       an int representing store_id, 
       a string representing expected delivery (for the expected delivery date),
       a list specifying the reorders the vendor is able to fufill, 
       a dictionary representing the items and quantities of items they are able to provide at that time (this is represented by UPC and the quantity_requested attributes), 
       an int representing shipment_number, 
       an int representing vendor_id, 
       and a variable named cnx representing the mySQL connection object.
       
       And adds a number of new shipments (equal to the number of reorder_requests that are valid and the number the shipment_items dictionary is able to fufill)
       to the shipment table in the ghhn database. This function will also print out a shipment manifest, a list of fufilled reorder_requests, the # of reorder_requests that vendor 
       still has for that particular store, and the number of reorder_requests that vendor has still for BMART as a whole """


 # I mostly took this code from Brian / Hadi, since the connection code isn't very unique between the three functions
 # check if connection is open
    if cnx is None or not cnx.is_connected():
        raise ValueError("The connection was not connected")

    try: 
        with cnx.cursor() as cursor:

            # find all of the reorder_requests that are from the given vendor and store
            cursor.execute("SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested, REORDER_REQUEST.reorder_id FROM REORDER_REQUEST WHERE REORDER_REQUEST.store_id = %s AND REORDER_REQUEST.vendor_id = %s", (store, vendor))
            
            # put those results into the product list (this will be a list of tuples)
            products = cursor.fetchall()

            fufilled_orders = []

            # for every reorder_request in products check to see if it's in the reorders list, if the item being requested is in the dictionary of
            # shipment items, and if there is enough of the product (in the shipment items dictionary) to fufill that reorder
            for x in products:
                if x[2] in reorders:

                    # raise an error and stop the shipment function if an item being requested isn't listed in the shipment_items dictionary
                    if shipment_items.get(x[0]) == None: 
                        raise ValueError(x[0] + " is an invalid shipment item!")
                    
                    # find out how many of that item the vendor can sell to the store
                    cur_quantity = shipment_items.get(x[0]) 

                    # see if the vendor has enough of that item to fufill the request
                    if cur_quantity >= x[1]:
                        # update dictionary to new current quantity of that item 
                        shipment_items[x[0]] = x[1] - cur_quantity

                        # add to fufilled orders
                        fufilled_orders.append((x[0], x[1], x[2]))

                    # if the vendor doesn't have enough of that item then give them a warning, and ask them if they'd like to continue the shipping process
                    else:
                        print("WARNING there is not enough of product: ", x[0], " to fufill reorder_request " + str(x[2]))
                        print("Would you like to continue with the current shipment process? \n If you do so not all of your reorder_requests will be fufilled.")
                        pref = input("Enter y for yes or n for no: ")

                        if pref == "n":
                            raise ValueError("CURRENT SHIPMENT HAS BEEN CANCELLED")

            # print out a list of the fufilled orders
            print("The Current Orders are out for delivery: ")           
            for x in fufilled_orders:
               
                print("Order #" + str(x[2]))
                # While this is happening insert the corresponding shipment into the shipment table
                cursor.execute("INSERT INTO SHIPMENT (shipment_no, reorder_id, expected_delivery) VALUES (%s, %s, %s);", (shipment_no, x[2], delivery_date))
                cnx.commit()

            # print out the shipping manifest
            print("Store #" + str(store) + " Manifest:")
            print("Expected Date and Time of Delievery: " + delivery_date)
            print("QUANTITY | ITEM")
         
            # use each product's UPC to find their corresponding product name, so that the manifest can be more readable
            for x in fufilled_orders:
                cursor.execute("SELECT PRODUCT.product_name FROM PRODUCT WHERE PRODUCT.UPC = %s", ([x[0]]))
                item = cursor.fetchall()
                print(" ", x[1], ": " + item[0][0])

            # print the number of orders that vendor has left for that store
            print("\nThere is currently:" + str((len(products) - len(fufilled_orders))) + " order(s) left for store #", store)

            # find the number of orders that vendor has left to fufill for BMART as a whole
            cursor.execute("SELECT REORDER_REQUEST.UPC, REORDER_REQUEST.quantity_requested, REORDER_REQUEST.reorder_id FROM REORDER_REQUEST WHERE REORDER_REQUEST.vendor_id = %s",  ([vendor]))
            selected_vendor = cursor.fetchall()

            # then subtract the already fufilled orders
            print("There is currently:" + str((len(selected_vendor) - len(fufilled_orders))) + " BMART order(s) left for vendor #", vendor)

            

    except  mysql.connector.Error as err:
        print('Error while executing', cursor.statement, '--', str(err))

        # to "reset" the database back to its original state if sql queries fail
        cnx.rollback()
        
