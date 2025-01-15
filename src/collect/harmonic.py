import os

import typing
import requests

import sqlalchemy

import numpy as np
import pandas as pd

import src.utils as utils
db = utils.db

BASE_URL = 'https://api.harmonic.ai'

def get_companies(cursor: typing.Optional[str] = None):
  headers = {
    'apikey': os.environ.get('HARMONIC_API_KEY')
  }

  URL = f'{BASE_URL}/savedSearches:results/129627?size=100'

  if cursor:
    URL = f'{URL}&cursor={cursor}'

  response = requests.get(URL, headers=headers)

  if response.status_code >= 400:
    print('Error:', response.status_code)
    return
  
  data = response.json()
  return data

done: bool = False
cursor: str = ''
page = 0

while not done:
    page += 1

    print(f'Page: {page}')
    data = get_companies(cursor)
    
    if not data:
        continue
    
    cursor = data.get('page_info', {}).get('next', '')
    has_next = data.get('page_info', {}).get('has_next', False)

    if not has_next:
        done = True

    results = data.get('results', [])
    companies = []

    for result in results:
        founded_at = None

        try:
            founded_at = result.get('founding_date', {}).get('date')
        except:
            pass
        
        location = None

        try:
            location = result.get('location', {}).get('country')
        except:
            pass
        
        domain = None

        try:
           domain = result.get('website', {}).get('domain')
        except:
            pass
        
        funding_stage = None
        funding_total = None

        try:
            funding_stage = result.get('funding', {}).get('funding_stage')
            funding_total = result.get('funding', {}).get('funding_total')
        except:
            pass
        
        tags = [
           tag.get('display_value') for tag in result.get('tags', [])
        ]
        tags_v2 = [
           tag.get('display_value') for tag in result.get('tags_v2', [])
        ]

        tags = list(set(tags + tags_v2))

        company = {
           'id': result.get('id'),
           'name': result.get('name'),
           'domain': domain,
           'logo_url': result.get('logo_url'),
           'description': result.get('description'),
           'external_description': None,
           'country': location,
           'type': result.get('company_type'),
           'headcount': result.get('headcount'),
           'funding_stage': funding_stage,
           'funding_total': funding_total,
           'founded_at': founded_at,
           'tags': tags,
        }

        companies.append(company)

        data = []

        for key in result.get('traction_metrics', {}).keys():
            timeseries = result.get('traction_metrics', {}).get(key, {}).get('metrics', [])

            for item in timeseries:
                data.append({
                    'company_id': result.get('id'),
                    'type': key,
                    'date': item.get('timestamp'),
                    'value': item.get('metric_value'),
                    'source': 'harmonic'
                }) 
            

    if len(companies) > 0:
        print(f'Upserting {len(companies)} companies')
        upsert_batch = sqlalchemy.dialects.postgresql.insert(db.schema.classes.companies).values(companies)
        upsert_batch = upsert_batch.on_conflict_do_update(
            index_elements=['id'],
            set_={
                key: getattr(upsert_batch.excluded, key)
                for key in companies[0].keys()
            }
        )

        try:
            db.session.execute(upsert_batch)
            db.session.commit()
            companies = []
        except Exception as e:
            print(e)
            db.session.rollback()
            break
        
    if len(data) > 0:
        print(f'Upserting {len(data)} data points')
        data = pd.DataFrame(data)
        data = data.drop_duplicates(subset=['company_id', 'type', 'date', 'source'], keep='first')
        data = data.dropna()
        data = data.to_dict(orient='records')
        

        BATCH_SIZE = 5_000
        batch_count = len(data) // BATCH_SIZE + 1

        for i in range(batch_count):
            print(f'Batch {i + 1}/{batch_count}')
            batch = data[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]

            upsert_batch = sqlalchemy.dialects.postgresql.insert(db.schema.classes.harmonic_data).values(batch)
            upsert_batch = upsert_batch.on_conflict_do_update(
                index_elements=['company_id', 'type', 'date', 'source'],
                set_={
                    key: getattr(upsert_batch.excluded, key)
                    for key in batch[0].keys()
                }
            )

            try:
                db.session.execute(upsert_batch)
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
                break
        
        data = []
      
    