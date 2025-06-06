BMart Inventory & Order Management - CS314 Final Project.
Hadi Imtiaz, Harsh Patel, Nawvatin Azhar & Grace Poulton

This system manages store inventory, reorder requests, vendor shipments, stocking, and online orders for BMart stores.
Key Functions

    reorder(store_id)
    Checks store inventory, accounts for outstanding orders and shipments, then places reorder requests.

    shipment(store_id, delivery_date, reorders, shipment_items)
    Vendors log shipments fulfilling reorder requests with expected delivery details.

    stock(store_id, shipment_id, shipment_items)
    Store staff record actual received shipment quantities and update inventory.

    online_order(store_id, customer_id, order_items)
    Processes online orders, verifying inventory and updating stock.

Files

    data.sql — Initial data inserts for the database

    tables.sql — Database schema and table definitions

    db_connection.py — Database connection setup

    project_part1.py — Implementation of reorder function

    project_part2.py — Implementation of shipment function

    project_part3.py — Implementation of stock function

    project_part4.py — Implementation of online_order function

    main.py — Main script to run or test functions

    group_project_report.txt — Project report and design documentation
