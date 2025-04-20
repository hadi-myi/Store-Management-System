import mysql.connector
from mysql.connector import errorcode
# Code from Brian Law and the MySQL Connector/Python documentation

def get_connection() -> mysql.connector.connection:
    """ A helper function to connect to the database. This lets you put the connection code in ONE place, rather than
    scattered throughout your program.

    :return: A connection to our SQL server, that should hopefully be open, but who knows, double-check on use!
    """
    # Try to open the SQL connection...
    try:
        cnx =  mysql.connector.connect(user='ghhn', password='Bmart4ever', host='cs314.iwu.edu', database='ghhn')
    # Connection errors handled here, with explicit handling for different types of errors.
    except mysql.connector.Error as err:

        # Basically just intercepting the MySQL error message and replacing it with something more user friendly.
        # In this model, we still want this to error out, so that the entire program halts (or someone can catch it).
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise mysql.connector.Error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise mysql.connector.Error("Database does not exist")
        else:
            raise mysql.connector.Error(err)

    return cnx