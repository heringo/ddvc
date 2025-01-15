import os
import time
import json
import tqdm

import typing
import github
import requests

import sqlalchemy

import numpy as np
import pandas as pd

import src.utils as utils
db = utils.db

BASE_URL = f'https://predictleads.com/api/v3'

query = (
  sqlalchemy.select(db.schema.classes.companies)
)

companies = pd.read_sql(query, db.connection)
companies = companies.to_dict(orient='records')

g = github.Github(os.environ.get('GITHUB_TOKEN'))

def get_github(domain: str):
    headers = {
        'X-Api-Key': os.environ.get('PREDICTLEADS_API_KEY'),
        'X-Api-Token': os.environ.get('PREDICTLEADS_API_TOKEN')
    }

    URL = f'{BASE_URL}/companies/{domain}/github_repositories'
    response = requests.get(URL, headers=headers) 

    if response.status_code >= 400:
        print('Error:', response.status_code)
        return

    data = response.json()
    return data

for company in companies:
    print(f'Trying to find Github for {company.get("domain")}')

    company_github = get_github(company.get('domain'))
    company_github = [
        repository.get('attributes', {}).get('url').replace('https://github.com/', '')
        for repository in company_github.get('data', [])
    ]

    owners = list(set([repository.split('/')[0] for repository in company_github]))

    organizations = []
    repositories = []

    for owner in owners:
        org = g.get_organization(owner).raw_data

        organization = {
            'name': org.get('name'),
            'url': org.get('url'),
            'homepage_url': org.get('blog'),
            'followers': org.get('followers'),
            'company_id': company.get('id'),
            'id': org.get('id'),
        }

        organizations.append(organization)
        time.sleep(1)

        for repo in g.get_user(owner).get_repos():
            time.sleep(1)
            print(f'Processing {repo.full_name}')
            license = repo.__dict__.get('_rawData', {}).get('license', {})

            if license is None:
                license = {}

            readme = None

            try:
                time.sleep(1)
                readme = repo.get_readme().decoded_content
                readme = readme.decode('utf-8')
            except:
                pass
            
            repository = {
                'id': repo.id,
                'full_name': repo.full_name,
                'name': repo.name,
                'url': repo.html_url,
                'description': repo.description,
                'readme': readme,
                'fork': repo.fork,
                'pushed_at': repo.pushed_at,
                'homepage_url': repo.homepage,
                'size': repo.size,
                'stargazers_count': repo.stargazers_count,
                'watchers_count': repo.watchers_count,
                'forks_count': repo.forks_count,
                'language': repo.language,
                'archived': repo.archived,
                'disabled': repo.__dict__.get('_rawData', {}).get('disabled', None),
                'license_key': license.get('key', None),
                'license_name': license.get('name', None),
                'license_url': license.get('url', None),
                'topics': repo.raw_data.get('topics', []),
                'organization_id': org.get('id'),
            }

            repositories.append(repository)
    
    if len(organizations) > 0:
        upsert_orgs = sqlalchemy.dialects.postgresql.insert(db.schema.classes.github_organizations).values(organizations)
        upsert_orgs = upsert_orgs.on_conflict_do_update(
            index_elements=['id'],
            set_={
                    key: getattr(upsert_orgs.excluded, key)
                    for key in organizations[0].keys()
            }
        )

        try:
            db.session.execute(upsert_orgs)
            db.session.commit()
            organizations = []
        except Exception as e:
            print(e)

    if len(repositories) > 0:
        upsert_repos = sqlalchemy.dialects.postgresql.insert(db.schema.classes.github_repositories).values(repositories)
        upsert_repos = upsert_repos.on_conflict_do_update(
            index_elements=['id'],
            set_={
                    key: getattr(upsert_repos.excluded, key)
                    for key in repositories[0].keys()
            }
        )

        try:
            db.session.execute(upsert_repos)
            db.session.commit()
            repositories = []
        except Exception as e:
            print(e)