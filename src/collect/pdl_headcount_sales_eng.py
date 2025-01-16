import os
import typing
import requests

import sqlalchemy

import numpy as np
import pandas as pd
import time

import json

import src.utils as utils
db = utils.db

MAX_NUM_RECORDS = 100

PDL_URL = "https://api.peopledatalabs.com/v5/company/search"

metadata = sqlalchemy.MetaData(bind=db.connection)
sqlalchemy.MetaData.reflect(metadata)

peopledatabase = metadata.tables['peopledatabase']

def get_companies_from_supabase_peopledatabase() -> typing.List[typing.Any]:
    return list(db.session.query(peopledatabase))

class RateLimitError(Exception):
    pass

def retry_if_rate_limit_error(func: typing.Callable[[typing.Any], typing.Any]):
    def _wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                print("Rate limit error, retrying in 60 seconds")
                time.sleep(60)
            except Exception as e:
                raise e
        raise Exception('Rate limit error, max retries reached')
    return _wrapper

@retry_if_rate_limit_error
def get_pdl_company_detail(cursor: typing.Optional[str] = None, companies: typing.Any = None):
    headers = {
        'Content-Type': 'application/json',
        'X-api-key': os.environ['API_KEY_PDL']
    }
    
    query = json.dumps({
        "bool": {
            "must": [
                {
                    "terms": {
                        "name": companies
                    }
                }
            ]
        }
    })

    params = {
        "dataset": "all",
        "query": query,
        "size": MAX_NUM_RECORDS,
        "pretty": True,
        "cursor": cursor
    }

    response = requests.post(PDL_URL, headers=headers, json=params)
    
    if response.status_code == 429:
        raise RateLimitError(f'Rate limit Error: {response.status_code} {response.text}')
    
    if response.status_code >= 400:
        print('Error:', response.status_code)
        raise Exception(f'Error: {response.status_code} {response.text}')
    
    if response is None:
        print("None response")

    data = response.json()
    
    return data

def insert_batch_supabase_headcount_sales_eng(company_details: typing.List[dict]):

    if len(company_details) > 0:
        print(f'Upserting {len(company_details)} companies headcount details (sales/eng)')
        upsert_batch = sqlalchemy.dialects.postgresql.insert(db.schema.classes.pdl_headcount_sales_eng).values(company_details)
        upsert_batch = upsert_batch.on_conflict_do_update(
            index_elements=['id'],
            set_={
                key: getattr(upsert_batch.excluded, key)
                for key in company_details[0].keys()
            }
        )

        try:
            db.session.execute(upsert_batch)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e
    
    return company_details

def main():
    
    companies = get_companies_from_supabase_peopledatabase()
    headcount_details = [company.employee_count_by_role for company in companies]
    company_names = [company.name for company in companies]
    company_ids = [company.id for company in companies]
    
    formatted_headcount_details = []
    for i in range(0, len(company_names), MAX_NUM_RECORDS):
        batch_names = company_names[i:i + MAX_NUM_RECORDS]
        batch_ids = company_ids[i:i + MAX_NUM_RECORDS]
        batch_details = headcount_details[i:i + MAX_NUM_RECORDS]
        
        for j in range(len(batch_details)):
            # Retrieve the headcount info for the current company
            info = batch_details[j]
            
            if info is None:
                print(f"Missing 'employee_count_by_role' for company '{batch_names[j]}' (ID: {batch_ids[j]}). Skipping.")
                continue  # Skip this company if info is missing

            # Append the formatted headcount details with default values if keys are missing
            formatted_headcount_details.append({
                "id": batch_ids[j],
                "name": batch_names[j],
                "other_uncategorized": info.get('other_uncategorized', 0),
                "trades": info.get('trades', 0),
                "operations": info.get("operations", 0),
                "customer_service": info.get("customer_service", 0),
                "legal": info.get("legal", 0),
                "public_relations": info.get("public_relations", 0),
                "real_estate": info.get("real_estate", 0),
                "design": info.get("design", 0),
                "education": info.get("education", 0),
                "media": info.get("media", 0),
                "marketing": info.get("marketing", 0),
                "human_resources": info.get("human_resources", 0),
                "sales": info.get("sales", 0),
                "health": info.get("health", 0),
                "finance": info.get("finance", 0),
                "engineering": info.get("engineering", 0),
            })
            
        insert_batch_supabase_headcount_sales_eng(formatted_headcount_details)
        formatted_headcount_details = []  # Clear the list for the next batch
    
    #print(f'company_names = {len(company_names)}')
    #print(f'companies_details = {len(companies_details["data"])}')
    #print(companies_details["data"][0]["name"])
    
   
if __name__ == "__main__":
    main()
