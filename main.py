import mysql.connector
from mysql.connector import errorcode
from db_connection import get_connection
from project_part1 import reorder
from project_part2 import shipment
from project_part3 import stock
from project_part4 import online_order

def main():
    # Try to open the SQL connection...
    try:

        with get_connection() as cnx:

            # Use / pass the same connection around to multiple subroutines, so they don't have to each open and close
            # separate connections

            # Python Function: please feel free to comment and uncomment things as needed
            
            # reorder function
            #reorder(2,cnx)

            # shipment function (Should return a list of one fufilled order (order seven) and a shipping manifest containing one laptop stand
            #shipment(1, "2025-04-13 09:15:00", [7], {"0000000000000008" : 6}, 7, 2, cnx)

            # stock function
            stock(1, 5, {'0000000000000012': 3}, cnx=cnx)

            # online_order function
            #test_order = {
                '0000000000000001': 2,
                '0000000000000003': 5,
                '0000000000000005': 1,
            }
             #online_order(store_id=1, customer_id=1, order_items=test_order, cnx=cnx)
            
            """Test 1:
            
            test_order = {
                '0000000000000001': 2,
                '0000000000000003': 5,
                '0000000000000005': 1,
            }
            online_order(store_id=1, customer_id=1, order_items=test_order, cnx=cnx)
            
            Output:
            Order 20 placed successfully for customer 1 at store 1
            Items Ordered:
            UPC: 0000000000000001, Quantity: 2
            UPC: 0000000000000003, Quantity: 5
            UPC: 0000000000000005, Quantity: 1
            Total price: 579.31
            True
            
            Test 2:
            test_order = {
                            '0000000000000004': 20,
                        }
                        online_order(store_id=1, customer_id=1, order_items=test_order, cnx=cnx)
            
            Output:
            Insufficient inventory for item Energy Drink, requested:20, in stock:1
            Store 1 is located in region: IL
            Store 3 in region IL has enough stock 31 of item 0000000000000004
            Some items could not be ordered due to insufficient inventory:
            UPC: 0000000000000004, Quantity: 20
            True
            """
            pass

    # Connection errors handled here, with explicit handling for different types of errors.
    except mysql.connector.Error as err:

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    print(cnx is None or not cnx.is_connected())
if __name__ == "__main__":
    main()
