import mysql.connector
from datetime import datetime

def stock(store_id: int, shipment_no: int, shipment_items: dict, cnx: mysql.connector.connection):
  """
  Parameters:
  - store_id (int): ID of the store receiving the shipment
  - shipment_no (int): Shipment number uniquely identifies a shipment used to fulfil multiple reorder requests
  - shipment_items (dict): {UPC (str): quantity_received (int)} based on what the shipment consists
  - cnx (mysql.connector.connection): Active database connection

  If any error occurs, all operations are rolled back and an error is printed
  """
  try:
    # Establishing connection
    if cnx is None or not cnx.is_connected():
      raise ValueError("Database connection is not active.")
    
  except:
    # If connection isn't established
    # Rather than having the program crash, the function will print the statement below
    print("Connection wasn't established")

  else: 
    # If the connection is established
    try:
      with cnx.cursor() as cursor:

        # -----------------------------------------------------STEP_1--------------------------------------------------------- 
        # Fetching all reorder requests to be fulfiled by the shipment: shipment_no for the store: store_id

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
        # If no reorders were found for shipment_no then error is raised
        # For example if shipment_data is empty
        if not shipment_data:
          raise ValueError(f"No matching reorder requests found for shipment {shipment_no} and store {store_id}.")


        #------------------------------------------------------STEP_3---------------------------------------------------------
        # Storing items requested from vendor in a dictionary with upc as key and quantity requested as value
        # Since these are items requested by the store, the store is expecting them so the dictionary is expected_items
        expected_items = {}
        # list of reorder_ids to be fulfilled by shimpment (shipment_no) is stored in the set reorder_ids
        reorder_ids = set()

        # Populating expected_items 
        for reorder_id, upc, qty in shipment_data:
          expected_items[upc] = qty
          reorder_ids.add(reorder_id)

        #-----------------------------------------------------STEP_4----------------------------------------------------------
        # All items in the shipment_no should be expected from vendor
        # In other words a shipment can't just have items that the store never expected/requested from the vendor
        # If it does have items the store wasn't expecting then a value error is raised
        for upc in shipment_items:
          if upc not in expected_items:
            raise ValueError(f"Invalid shipment item {upc}!")

        #-----------------------------------------------------STEP_5----------------------------------------------------------
        # All the rows of the SHIPMENT table with the shipment: shipment_no should be marked as received
        # In other words recieved_data should be updated and therefore shoudn't be null
        cursor.execute("""
            UPDATE SHIPMENT SET received_date = %s
            WHERE shipment_no = %s;
        """, (datetime.now(), shipment_no))

        #-----------------------------------------------------STEP_6---------------------------------------------------------
        # Now we update the inventory for each item received in the shipment: shipment_no
        # We must make sure that current_inventory doesn't exceed max_inventory
        for upc, qty_received in shipment_items.items():
          # Getting the current and max inventory for each product in the shipment: shipment_no
          cursor.execute("""
              SELECT current_inventory, max_inventory
              FROM SELL
              WHERE store_id = %s AND UPC = %s;
          """, (store_id, upc))

          # fetchone as there is one inventory for a specific product in one store: store_id
          # Raise an error if we didn't find the inventory at the store: store_id for a specific product received
          result = cursor.fetchone()
          if not result:
            raise ValueError(f"SELL entry not found for store {store_id} and UPC {upc}.")

          current_inv, max_inv = result
          new_inventory = current_inv + qty_received

          # Warning is printed if new_inventory exceeds max inventory
          # New_inventory is current inventory after attempting to stock
          if new_inventory > max_inv:
            print(f"Warning: Stocking {upc} would exceed max_inventory. Capping at {max_inv}.")
            new_inventory = max_inv

          # Updating current inventory
          # If current inventory exceeds max inventory, 
          # then current inventory is stocked to max inventry 
          # as new_inventory is updated to be max inventory 
          # when current inventory exceeds max inventory
          cursor.execute("""
              UPDATE SELL
              SET current_inventory = %s
              WHERE store_id = %s AND UPC = %s;
          """, (new_inventory, store_id, upc))

        #-------------------------------------------------------sSTEP_7------------------------------------------------------------
        # Committing all operations to database
        cnx.commit()

        #--------------------------------------------------------STEP_8------------------------------------------------------------
        # For Stocker's usefulness 
        # I am printing the items and it's quantity expected from vendor in shipment_no
        print(f"\n--- Shipment #{shipment_no} Processed for Store {store_id} ---")
        print("Expected from Vendor:")
        for upc, qty in expected_items.items():
          print(f"  UPC: {upc} - Qty: {qty}")

        # Then printing the items and the corresponding quantity recieved in shipment_no
        print("\nReceived by Stocker:")
        for upc, qty in shipment_items.items():
          print(f"  UPC: {upc} - Qty: {qty}")

        # Then printing descrepencies of there is any
        print("\nDiscrepancies:")
        has_discrepancy = False
        for upc, expected_qty in expected_items.items():
          received_qty = shipment_items.get(upc, 0)
          if received_qty != expected_qty:
            print(f"  UPC: {upc} - Expected: {expected_qty}, Received: {received_qty}")
            has_discrepancy = True
        if not has_discrepancy:
          print("  No discrepencies")

    #------------------------------------------------------------STEP_9-----------------------------------------------------------
    # Handling both types of error the function is capable of raising
    except mysql.connector.Error as err:
          print('Error while executing', cursor.statement, '--', str(err))
          # to "reset" the database back to its original state if sql queries fail
          cnx.rollback()

    except ValueError as verr:
      print(f"Error: {verr}")
      cnx.rollback()

    """
    Citation:
    -I was getting an error for being in a wrong directory so asked GPT to help me fix the error
    -Didn't solve it but gave a helpful insight which I thought I should incorporate
    -It asked me to include the last except block in my code
    -Earlier I thought One try can only have one except, but I was wrong
    -It is crucial for me to include this error except as my function is capable of raising value error
    -Instead of causing the program to crash when a value error is raised, an error message is printed.
    """