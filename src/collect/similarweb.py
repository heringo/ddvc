import os
import sys

import github
import pandas as pd
import requests
import sqlalchemy
import tqdm

import src.utils as utils

db = utils.db

BASE_URL = "https://predictleads.com/api/v3"

query = sqlalchemy.select(db.schema.classes.companies)

companies = pd.read_sql(query, db.connection)
companies = companies[companies["topic_id"] != 14]
companies = companies.to_dict(orient="records")


def get_similarweb(domain: str):
    headers = {
        "X-Api-Key": os.environ.get("PREDICTLEADS_API_KEY"),
    }

    URL = f'https://api.similarweb.com/v1/website/{domain}/total-traffic-and-engagement/visits?api_key=5145365ab2a741a794892d13ec3ce7ea&start_date=2022-12&end_date=2024-12&country=world&granularity=monthly&main_domain_only=false&format=json'
    response = requests.get(URL, headers=headers)

    if response.status_code >= 400:
        print("Error:", response.status_code)
        print(response.text)
        return response.json()

    data = response.json()
    return data


organizations = []
repositories = []

for company in tqdm.tqdm(companies):
    data = get_similarweb(company.get("domain"))

    print(f'Getting data for domain: {company.get("domain")}')
    
    if data.get('meta', {}).get('error_code', None):
        print(f"Error for {company.get('domain')}")
        continue
    
    rows = []

    for row in data.get('visits', []):
        item = {
            'company_id': company.get('id'),
            'source': 'similarweb',
            'type': 'similarweb_visits',
            'date': row.get('date'),
            'value': row.get('visits'),
        }

        rows.append(item)

   
    if len(rows) > 0:
        upsert_orgs = sqlalchemy.dialects.postgresql.insert(
            db.schema.classes.harmonic_data
        ).values(rows)
        upsert_orgs = upsert_orgs.on_conflict_do_update(
            index_elements=["source", "type", "company_id", "date"],
            set_={
                key: getattr(upsert_orgs.excluded, key)
                for key in rows[0].keys()
            },
        )

        try:
            db.session.execute(upsert_orgs)
            db.session.commit()
            rows = []
        except Exception as e:
            print(e)
