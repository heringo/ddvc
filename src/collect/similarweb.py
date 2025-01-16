import os
import sys

import requests
import sqlalchemy

from utils import db

sql_library = sqlalchemy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


# Function to fetch domain names from the `companies` table
def fetch_domains_from_companies():
    """
    Fetches domains and IDs from the `companies` table.
    Returns:
        list: List of dictionaries containing company IDs and domains.
    """
    try:
        query = sql_library.text(
            "SELECT id, domain FROM companies WHERE domain IS NOT NULL"
        )
        result = db.session.execute(query).fetchall()
        domains = [{"id": row[0], "domain": row[1]} for row in result]
        print(f"Fetched {len(domains)} domains from the companies table.")
        return domains
    except Exception as e:
        print(f"Error fetching domains: {e}")
        return []


# Function to fetch general website data from the SimilarWeb API
def get_website_data(domain: str):
    """
    Fetches general data for a specific domain from the SimilarWeb API.
    Args:
        domain (str): The domain to fetch data for.
    Returns:
        dict: The API response as a dictionary, or None if there's an error.
    """
    api_key = os.environ.get("SIMILAR_API_KEY")
    if not api_key:
        raise ValueError("SIMILAR_API_KEY not found in environment variables")

    url = f"https://api.similarweb.com/v1/website/{domain}/general-data/all"
    params = {"api_key": api_key, "format": "json"}
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 404:
        print(f"Domain {domain} not found (404). Skipping...")
        return None
    elif response.status_code >= 400:
        print(f"Error fetching data for domain {domain}: {response.status_code}")
        return None

    return response.json()


# Function to fetch total traffic and engagement data
def get_total_traffic_and_engagement(domain: str):
    """
    Fetches total traffic and engagement data for a domain using a broader date range.
    Args:
        domain (str): The domain to fetch data for.
    Returns:
        dict: Total traffic and engagement data.
    """
    api_key = os.environ.get("SIMILAR_API_KEY")
    if not api_key:
        raise ValueError("SIMILAR_API_KEY not found in environment variables")

    url = f"https://api.similarweb.com/v1/website/{domain}/total-traffic-and-engagement/visits"
    params = {
        "api_key": api_key,
        "start_date": "2023-01",
        "end_date": "2024-12",
        "country": "us",
        "granularity": "monthly",
        "main_domain_only": "false",
        "format": "json",
        "show_verified": "false",
        "mtd": "false",
        "engaged_only": "false",
    }
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 404:
        print(f"Traffic data not found for {domain} (404). Skipping...")
        return None
    elif response.status_code >= 400:
        print(f"Error fetching total traffic data for {domain}: {response.status_code}")
        return None

    return response.json()


# Function to process domains and store data
def process_domains(domain_records):
    """
    Processes domains to retrieve SimilarWeb data, upserts scalar fields, and creates records for traffic data.
    Args:
        domain_records (list): List of dictionaries with `id` and `domain`.
    """
    all_data = []  # List to store scalar records
    traffic_data = []  # List to store traffic records

    for record in domain_records:
        company_id = record["id"]
        domain = record["domain"]
        print(f"Fetching data for domain: {domain} (ID: {company_id})")

        # Fetch general website data
        data = get_website_data(domain)

        if data:
            # Scalar fields
            company_record = {
                "company_id": company_id,
                "domain": domain,
                "category": data.get("category"),
                "global_rank": data.get("global_rank", {}).get("rank"),
                "category_rank": data.get("category_rank", {}).get("rank"),
                "country_rank": data.get("country_rank", {}).get("rank"),
            }
            all_data.append(company_record)

        # Fetch traffic data
        traffic_response = get_total_traffic_and_engagement(domain)
        if traffic_response and "visits" in traffic_response:
            visits = traffic_response["visits"]
            for visit_record in visits:
                traffic_record = {
                    "company_id": company_id,
                    "domain": domain,
                    "type": "total_traffic",
                    "visit_date": visit_record["date"],
                    "visit_count": visit_record["visits"],
                }
                traffic_data.append(traffic_record)

    # Upsert scalar data
    if all_data:
        print(f"Upserting {len(all_data)} scalar records...")
        upsert_array_data(
            all_data,
            "similarweb_data",
            ["company_id", "domain"],
        )

    # Upsert traffic data
    if traffic_data:
        print(f"Upserting {len(traffic_data)} traffic records...")
        upsert_array_data(
            traffic_data,
            "similarweb_data_timeperiod",
            ["company_id", "type", "visit_date", "domain"],
        )


# Function to upsert data into a specified table
def upsert_array_data(data, table_name, unique_keys):
    """
    Generalized function to upsert array data into a specified table.

    Args:
        data (list): List of dictionaries containing data to upsert.
        table_name (str): Name of the database table to upsert into.
        unique_keys (list): List of column names that form the unique constraint.
    """
    if not data:
        print(f"No data to upsert into {table_name}.")
        return

    try:
        # Create an insert statement
        upsert_batch = sqlalchemy.dialects.postgresql.insert(
            getattr(db.schema.classes, table_name),
        ).values(data)

        # Configure the ON CONFLICT clause
        upsert_batch = upsert_batch.on_conflict_do_update(
            index_elements=unique_keys,
            set_={key: getattr(upsert_batch.excluded, key) for key in data[0].keys()},
        )

        # Execute the query
        db.session.execute(upsert_batch)
        db.session.commit()
        print(f"Upserted {len(data)} records into {table_name}.")
    except Exception as e:
        print(f"Error upserting data into {table_name}: {e}")
        db.session.rollback()


# Main script execution
domains = fetch_domains_from_companies()

if domains:
    process_domains(domains)
else:
    print("No domains found in the companies table.")
