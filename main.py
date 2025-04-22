import mysql.connector
from mysql.connector import errorcode
from db_connection import get_connection
from project_part1 import reorder
from project_part3 import stock

def main():
    # Try to open the SQL connection...
    try:

        with get_connection() as cnx:

            # Use / pass the same connection around to multiple subroutines, so they don't have to each open and close
            # separate connections
            #reorder(2,cnx)

            stock(1, 3, {'0000000000000009': 24}, cnx=cnx)
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
