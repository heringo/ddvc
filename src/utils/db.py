import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Ensure the database URL is set
if not DATABASE_URL:
    raise ValueError(
        'Could not find DATABASE_URL in environment variables')

# Connect to the database
connection = sqlalchemy.create_engine(
    DATABASE_URL, echo=False)

# Reflect the database schema
schema = automap_base()
schema.prepare(autoload_with=connection, engine=connection)

session = sqlalchemy.orm.Session(connection)

