import mysql.connector
from datetime import datetime

def stock(store_id: int, shipment_no: int, shipment_items: dict, cnx: mysql.connector.connection):

  if cnx is None or not cnx.is_connected():
    raise ValueError("Database connection is not active.")

  try:
    with cnx.cursor() as cursor:

      # Step 1: Fetch all reorder requests linked to this shipment number and store
      cursor.execute("""
          SELECT RR.reorder_id, RR.UPC, RR.quantity_requested
          FROM SHIPMENT S
          JOIN REORDER_REQUEST RR ON S.reorder_id = RR.reorder_id
          WHERE S.shipment_no = %s AND RR.store_id = %s;
      """, (shipment_no, store_id))

      shipment_data = cursor.fetchall()

      # Step 2: If no such shipment was found, raise an error
      if not shipment_data:
        raise ValueError(f"No matching reorder requests found for shipment {shipment_no} and store {store_id}.")

      # Step 3: Prepare a dictionary of expected items and a set of reorder_ids involved
      expected_items = {}
      reorder_ids = set()
      for reorder_id, upc, qty in shipment_data:
        expected_items[upc] = qty
        reorder_ids.add(reorder_id)

      # Step 4: Validate that all items in the stocker's report are expected
      for upc in shipment_items:
        if upc not in expected_items:
          raise ValueError(f"Invalid shipment item {upc}!")

      # Step 5: Mark all SHIPMENT rows with this shipment_no as received now
      cursor.execute("""
          UPDATE SHIPMENT SET received_date = %s
          WHERE shipment_no = %s;
      """, (datetime.now(), shipment_no))

      # Step 6: Update inventory for each item received
      for upc, qty_received in shipment_items.items():
        cursor.execute("""
            UPDATE SELL
            SET current_inventory = current_inventory + %s
            WHERE store_id = %s AND UPC = %s;
        """, (qty_received, store_id, upc))

      # Step 7: All operations successful, commit to database
      cnx.commit()

      # Step 8: Print vendor’s expected shipment
      print(f"\n--- Shipment #{shipment_no} Processed for Store {store_id} ---")
      print("Expected from Vendor:")
      for upc, qty in expected_items.items():
        print(f"  UPC: {upc} - Qty: {qty}")

      # Step 9: Print what the stocker actually received
      print("\nReceived by Stocker:")
      for upc, qty in shipment_items.items():
        print(f"  UPC: {upc} - Qty: {qty}")

      # Step 10: Compare and report discrepancies
      print("\nDiscrepancies:")
      has_discrepancy = False
      for upc, expected_qty in expected_items.items():
        received_qty = shipment_items.get(upc, 0)
        if received_qty != expected_qty:
          print(f"  UPC: {upc} - Expected: {expected_qty}, Received: {received_qty}")
          has_discrepancy = True
      if not has_discrepancy:
        print("  None")

  # Step 11: On any SQL or logic error, rollback and notify the user
  except mysql.connector.Error as err:
    print(f"MySQL Error: {err}")
    cnx.rollback()
  except ValueError as verr:
    print(f"Error: {verr}")
    cnx.rollback()


  """
  For late use
  Process an incoming shipment for a store.

  Parameters:
  - store_id (int): ID of the store receiving the shipment
  - shipment_no (int): Shipment number used to group multiple reorder requests
  - shipment_items (dict): {UPC (str): quantity_received (int)} based on what stockers counted
  - cnx (mysql.connector.connection): Active database connection

  If any error occurs, all operations are rolled back and an error is printed.
  """