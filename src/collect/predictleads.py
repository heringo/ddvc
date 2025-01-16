import os

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
companies = companies.to_dict(orient="records")

g = github.Github(os.environ.get("GITHUB_API_KEY"))


def get_github(domain: str):
    headers = {
        "X-Api-Key": os.environ.get("PREDICTLEADS_API_KEY"),
        "X-Api-Token": os.environ.get("PREDICTLEADS_API_TOKEN"),
    }

    URL = f"{BASE_URL}/companies/{domain}/github_repositories"
    response = requests.get(URL, headers=headers)

    if response.status_code >= 400:
        print("Error:", response.status_code)
        return

    data = response.json()
    return data


organizations = []
repositories = []

for company in tqdm.tqdm(companies):
    print(f"Trying to find Github for {company.get('domain')}")

    company_github = get_github(company.get("domain"))

    if company_github is None:
        print(f"No Github found for {company.get('domain')}")
        continue

    company_github = [
        repository.get("attributes", {}).get("url").replace("https://github.com/", "")
        for repository in company_github.get("data", [])
    ]

    owners = list(set([repository.split("/")[0] for repository in company_github]))

    for owner in owners:
        org = None

        try:
            org = g.get_organization(owner).raw_data
        except:
            pass

        if org is None:
            continue

        organization = {
            "name": org.get("name"),
            "url": org.get("url"),
            "homepage_url": org.get("blog"),
            "followers": org.get("followers"),
            "company_id": company.get("id"),
            "id": org.get("id"),
        }

        organizations.append(organization)

        repo_count = 0
        for repo in g.get_user(owner).get_repos(
            sort="stargazers_count", direction="desc"
        ):
            repo_count += 1

            if repo_count > 3:
                break

            print(f"Processing {repo.full_name}")
            license = repo.__dict__.get("_rawData", {}).get("license", {})

            if license is None:
                license = {}

            readme = None

            try:
                readme = repo.get_readme().decoded_content
                readme = readme.decode("utf-8")
            except:
                pass

            repository = {
                "id": repo.id,
                "full_name": repo.full_name,
                "name": repo.name,
                "url": repo.html_url,
                "description": repo.description,
                "readme": readme,
                "fork": repo.fork,
                "pushed_at": repo.pushed_at,
                "homepage_url": repo.homepage,
                "size": repo.size,
                "stargazers_count": repo.stargazers_count,
                "watchers_count": repo.watchers_count,
                "forks_count": repo.forks_count,
                "language": repo.language,
                "archived": repo.archived,
                "disabled": repo.__dict__.get("_rawData", {}).get("disabled", None),
                "license_key": license.get("key", None),
                "license_name": license.get("name", None),
                "license_url": license.get("url", None),
                "topics": repo.raw_data.get("topics", []),
                "organization_id": org.get("id"),
            }

            repositories.append(repository)

    if len(organizations) > 0:
        upsert_orgs = sqlalchemy.dialects.postgresql.insert(
            db.schema.classes.github_organizations
        ).values(organizations)
        upsert_orgs = upsert_orgs.on_conflict_do_update(
            index_elements=["id"],
            set_={
                key: getattr(upsert_orgs.excluded, key)
                for key in organizations[0].keys()
            },
        )

        try:
            db.session.execute(upsert_orgs)
            db.session.commit()
            # organizations = []
        except Exception as e:
            print(e)

    if len(repositories) > 0:
        upsert_repos = sqlalchemy.dialects.postgresql.insert(
            db.schema.classes.github_repositories
        ).values(repositories)
        upsert_repos = upsert_repos.on_conflict_do_update(
            index_elements=["id"],
            set_={
                key: getattr(upsert_repos.excluded, key)
                for key in repositories[0].keys()
            },
        )

        try:
            db.session.execute(upsert_repos)
            db.session.commit()
            # repositories = []
        except Exception as e:
            print(e)
