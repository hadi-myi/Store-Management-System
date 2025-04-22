import mysql.connector
from datetime import datetime

def stock(store_id: int, shipment_no: int, shipment_items: dict, cnx: mysql.connector.connection):
  try:
    # Establishing connection
    if cnx is None or not cnx.is_connected():
      raise ValueError("Database connection is not active.")
    
  except:
    # If connection isn't established
    # Rather than having the program crash we print the statement below
    print("Connection wasn't established")

  else: 
    # If the connection is established
    try:
      with cnx.cursor() as cursor:

        # -----------------------------------------------------STEP_1--------------------------------------------------------- 
        # Fetching all reorder requests being fulfiled by a the shipment: shipment_no for the store: store_id

        """
        SQL Query: 
        The query is listing the reorders (reorder_id) from the REORDER_REQUEST table along with the upc 
        requested and the quantity of the upc requested in that reorder. The reorders being listed are reorders
        being fulfilled by the shipment (shipment_no) for the store (store_id).
        """
        cursor.execute("""
            SELECT RR.reorder_id, RR.UPC, RR.quantity_requested
            FROM SHIPMENT AS S
            JOIN REORDER_REQUEST AS RR ON S.reorder_id = RR.reorder_id
            WHERE S.shipment_no = %s AND RR.store_id = %s;
        """, (shipment_no, store_id))
        
        # Stores all the reorders along with corresponding upc and quantity requested, listed by the SQL query
        shipment_data = cursor.fetchall()


        #------------------------------------------------------STEP_2--------------------------------------------------------
        #  If no shipment was found for shipment_no then error is raised
        if not shipment_data:
          raise ValueError(f"No matching reorder requests found for shipment {shipment_no} and store {store_id}.")


        #------------------------------------------------------STEP_3---------------------------------------------------------
        # Storing items requested from vendor in a dictionary with upc as key and quantity requested as value
        # Since these are items requested by the store, the store is expecting them so the dictionary is expected_items
        expected_items = {}
        # list of reorder_ids being fulfilled by shimpment (shipment_no) is stored in the set reorder_ids
        reorder_ids = set()

        # Populating the expected item with all the listed reorders 
        for reorder_id, upc, qty in shipment_data:
          expected_items[upc] = qty
          reorder_ids.add(reorder_id)

        # 4 All items in the shipment_no should be expected from vendor
        # In other words a shipment can't just have items that the store never expected/requested from the vendor
        for upc in shipment_items:
          if upc not in expected_items:
            raise ValueError(f"Invalid shipment item {upc}!")

        # 5 All the rows of SHIPMENT table with this shipment_no should be marked as received
        # In other words recieved_data should be updated
        cursor.execute("""
            UPDATE SHIPMENT SET received_date = %s
            WHERE shipment_no = %s;
        """, (datetime.now(), shipment_no))

        # 6 Update inventory for each item received
        ################ How do I make sure current doesn't exceed max???
        for upc, qty_received in shipment_items.items():
          cursor.execute("""
              UPDATE SELL
              SET current_inventory = current_inventory + %s
              WHERE store_id = %s AND UPC = %s;
          """, (qty_received, store_id, upc))

        # 7 Committing all operations to database
        cnx.commit()

        # 8 Printing expected shipment from vendor 
        print(f"\n--- Shipment #{shipment_no} Processed for Store {store_id} ---")
        print("Expected from Vendor:")
        for upc, qty in expected_items.items():
          print(f"  UPC: {upc} - Qty: {qty}")

        # 9 Printing what stocker received
        print("\nReceived by Stocker:")
        for upc, qty in shipment_items.items():
          print(f"  UPC: {upc} - Qty: {qty}")

        # 10 Printing wether descrepencies exist or not
        print("\nDiscrepancies:")
        has_discrepancy = False
        for upc, expected_qty in expected_items.items():
          received_qty = shipment_items.get(upc, 0)
          if received_qty != expected_qty:
            print(f"  UPC: {upc} - Expected: {expected_qty}, Received: {received_qty}")
            has_discrepancy = True
        if not has_discrepancy:
          print("  No discrepencies")

    # 11 On any SQL or logic error, rollback and notify the user
    except mysql.connector.Error as err:
          print('Error while executing', cursor.statement, '--', str(err))
          # to "reset" the database back to its original state if sql queries fail
          cnx.rollback()
    # On value erro, rollback and notify the user
    except ValueError as verr:
      print(f"Error: {verr}")
      cnx.rollback()


  """
  Working on doc string
  Process an incoming shipment for a store.

  Parameters:
  - store_id (int): ID of the store receiving the shipment
  - shipment_no (int): Shipment number used to group multiple reorder requests
  - shipment_items (dict): {UPC (str): quantity_received (int)} based on what stockers counted
  - cnx (mysql.connector.connection): Active database connection

  If any error occurs, all operations are rolled back and an error is printed.
  """