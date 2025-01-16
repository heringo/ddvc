import json
import os
import time
import typing

import requests
import sqlalchemy

import src.utils as utils

db = utils.db

MAX_NUM_RECORDS = 100

PDL_URL = "https://api.peopledatalabs.com/v5/company/search"

metadata = sqlalchemy.MetaData(bind=db.connection)
sqlalchemy.MetaData.reflect(metadata)

companies = metadata.tables["companies"]


def get_companies_from_supabase() -> typing.List[typing.Any]:
    return list(db.session.query(companies))


class RateLimitError(Exception):
    pass


def retry_if_rate_limit_error(func: typing.Callable[[typing.Any], typing.Any]):
    def _wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except RateLimitError:
                print("Rate limit error, retrying in 60 seconds")
                time.sleep(60)
            except Exception as e:
                raise e
        raise Exception("Rate limit error, max retries reached")

    return _wrapper


@retry_if_rate_limit_error
def get_pdl_company_detail(
    cursor: typing.Optional[str] = None, companies: typing.Any = None
):
    headers = {
        "Content-Type": "application/json",
        "X-api-key": os.environ["API_KEY_PDL"],
    }

    query = json.dumps({"bool": {"must": [{"terms": {"name": companies}}]}})

    params = {
        "dataset": "all",
        "query": query,
        "size": MAX_NUM_RECORDS,
        "pretty": True,
        "cursor": cursor,
    }

    response = requests.post(PDL_URL, headers=headers, json=params)

    if response.status_code == 429:
        raise RateLimitError(
            f"Rate limit Error: {response.status_code} {response.text}"
        )

    if response.status_code >= 400:
        print("Error:", response.status_code)
        raise Exception(f"Error: {response.status_code} {response.text}")

    data = response.json()

    return data


def insert_batch_supabase_details(company_details: typing.List[dict]):
    if len(company_details) > 0:
        print(f"Upserting {len(company_details)} companies details")
        upsert_batch = sqlalchemy.dialects.postgresql.insert(
            db.schema.classes.peopledatabase_enriched
        ).values(company_details)
        upsert_batch = upsert_batch.on_conflict_do_update(
            index_elements=["id"],
            set_={
                key: getattr(upsert_batch.excluded, key)
                for key in company_details[0].keys()
            },
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
    companies = get_companies_from_supabase()
    company_names = [company.name for company in companies]
    company_ids = [company.id for company in companies]

    company_details = []
    for i in range(0, len(company_names), MAX_NUM_RECORDS):
        batch_names = company_names[i : i + MAX_NUM_RECORDS]
        batch_ids = company_ids[i : i + MAX_NUM_RECORDS]

        companies_details = get_pdl_company_detail(companies=batch_names)

        for j in range(len(batch_names)):
            info = companies_details["data"][j]
            company_details.append(
                {
                    "id": batch_ids[j],
                    "name": batch_names[j],
                    "founded": info.get("founded", None),
                    "country": info.get("location", None),
                    "industry": info.get("industry", None),
                    "number_funding_rounds": info.get("number_funding_rounds", None),
                    "total_funding_raised": info.get("total_funding_raised", None),
                    "last_funding_date": info.get("last_funding_date", None),
                    "latest_funding_stage": info.get("latest_funding_stage", None),
                    "linkedin_follower_count": info.get(
                        "linkedin_follower_count", None
                    ),
                    "employee_count_by_role": info.get("employee_count_by_role", None),
                    "average_employee_tenure": info.get(
                        "average_employee_tenure", None
                    ),
                    "employee_churn_rate": info.get("employee_churn_rate", None),
                    "employee_growth_rate": info.get("employee_growth_rate", None),
                    "tags": info.get("tags", None),
                }
            )

        insert_batch_supabase_details(company_details)
        company_details = []  # Clear the list for the next batch

    # print(f'company_names = {len(company_names)}')
    # print(f'companies_details = {len(companies_details["data"])}')
    # print(companies_details["data"][0]["name"])


if __name__ == "__main__":
    main()
