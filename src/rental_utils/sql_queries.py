from sqlalchemy import create_engine
from sqlalchemy import inspect, text
import logging
import os
import sys

#Getting the engine

logging.info('Finding current Path')
__file__ = "sql_queries.py"
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(current_dir, '..'))


# Connect to local database
def get_sql_engine(data_path):
    """
    Returns a SQLAlchemy engine object for connecting to a SQLite database.

    If the engine object has not been created yet, it will be created and stored
    as a static attribute of the `get_sql_engine` function.

    Returns:
        sqlalchemy.engine.Engine: The SQLAlchemy engine object.
    """
    if not hasattr(get_sql_engine, 'engine'):
        get_sql_engine.engine = create_engine('sqlite:///' + data_path)
    return get_sql_engine.engine

# Connect to cloud engine in supabase
def get_supabase_engine(user, password, host, port, database):
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    return engine



# Create a table with Pandas
def make_table(df, name, engine, if_exists='append'):
    with engine.connect() as conn:
        pass
    df.to_sql(name, engine, if_exists=if_exists, index=False)

#SQL QUERIES
# create a table if it doesn't exist
CREATE_TABLE_SQL_QUERY = """
CREATE TABLE IF NOT EXISTS properties_data (
    id INTEGER PRIMARY KEY,
    price_per_bed REAL,
    predicted_price_per_bed REAL,
    travel_time INTEGER,
    distance INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    "numberOfImages" INTEGER,
    "displayAddress" TEXT,
    latitude REAL,
    longitude REAL,
    "propertySubType" TEXT,
    "listingUpdateReason" TEXT,
    "listingUpdateDate" TEXT,
    "priceAmount" INTEGER,
    "priceFrequency" TEXT,
    "premiumListing" INTEGER,
    "featuredProperty" INTEGER,
    "transactionType" TEXT,
    students INTEGER,
    "displaySize" TEXT,
    "propertyUrl" TEXT,
    "firstVisibleDate" TEXT,
    "addedOrReduced" TEXT,
    "propertyTypeFullDescription" TEXT
);
"""

# drop the table if needed
DROP_PROPERTIES_TABLE_SQL_QUERY = "DROP TABLE IF EXISTS properties_data;"

# get the standalone rightmove data
GET_RIGHTMOVE_DATA_SQL_QUERY = """
SELECT  
    *
FROM rightmove_data
"""

# get the properties data with additional data like travel times etc
GET_PROPERTIES_DATA_SQL_QUERY = """
SELECT  
    *
FROM properties_data
"""
## Update existing table with new data

### Update travel time and distance
UPDATE_DIST_AND_TRAVEL_TIME = """
UPDATE properties_data
SET
    travel_time = (
        SELECT temp.travel_time FROM temp_updates temp
        WHERE temp.id = properties_data.id
    ),
    distance = (
        SELECT temp.distance FROM temp_updates temp
        WHERE temp.id = properties_data.id
    )
WHERE id IN (SELECT id FROM temp_updates)
  AND (travel_time IS NULL OR distance IS NULL);
"""

# Update the predicted price/rent per month
UPDATE_PREDICTED_PRICE = """
UPDATE properties_data
SET
    predicted_price_per_bed = (
        SELECT temp.predicted_price_per_bed FROM temp_updates temp
        WHERE temp.id = properties_data.id
    )
WHERE id IN (SELECT id FROM temp_updates)
  AND predicted_price_per_bed IS NULL;
"""

# Insert data with new rows