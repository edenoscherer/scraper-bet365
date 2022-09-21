from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv


def get_database():
    load_dotenv('../.env')

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://user123:pass123@bet365.nthsuw2.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['bet365-test']


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":

    # Get the database
    dbname = get_database()
    res = dbname.get_collection('virtual-soccer').find_one(
        {'event': 'Euro Cup - 19.32', 'date': datetime.strptime('2022-08-04T19:32:00', "%Y-%m-%dT%H:%M:%S")})
    print(res)
