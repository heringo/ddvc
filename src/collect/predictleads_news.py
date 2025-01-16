import os
from typing import Any, Dict

import pandas as pd
import requests
import sqlalchemy
from sqlalchemy.dialects import postgresql

import src.utils as utils

db = utils.db

BASE_URL = "https://predictleads.com/api/v3"

# Get companies
query = sqlalchemy.select(db.schema.classes.companies).where(
    db.schema.classes.companies.topic_id != 14
)

companies = pd.read_sql(query, db.connection)
companies = companies.to_dict(orient="records")


def get_news(domain: str):
    headers = {
        "X-Api-Key": os.environ.get("PREDICTLEADS_API_KEY"),
        "X-Api-Token": os.environ.get("PREDICTLEADS_API_TOKEN"),
    }

    URL = f"{BASE_URL}/companies/{domain}/news_events"
    response = requests.get(URL, headers=headers)

    if response.status_code >= 400:
        print("Error:", response.status_code)
        return

    data = response.json()
    return data


def transform_raw_data(company_id: str, raw_data: Dict[str, Any]) -> list:
    """Transform raw JSON data into a list of dicts ready for SQLAlchemy"""
    if not raw_data:
        return []

    events = []

    # Create a lookup for articles
    articles = {
        article["id"]: article["attributes"]
        for article in raw_data.get("included", [])
        if article["type"] == "news_article"
    }

    for event in raw_data.get("data", []):
        attrs = event["attributes"]

        # Get related article data
        article_id = (
            event["relationships"]
            .get("most_relevant_source", {})
            .get("data", {})
            .get("id")
        )
        article_data = articles.get(article_id, {})

        transformed_event = {
            "id": event["id"],
            "company_id": company_id,
            "summary": attrs.get("summary"),
            "category": attrs.get("category"),
            "found_at": attrs.get("found_at"),
            "confidence": attrs.get("confidence"),
            "article_sentence": attrs.get("article_sentence"),
            "human_approved": attrs.get("human_approved"),
            "planning": attrs.get("planning"),
            # Article data
            "article_id": article_id,
            "article_author": article_data.get("author"),
            "article_body": article_data.get("body"),
            "article_image_url": article_data.get("image_url"),
            "article_url": article_data.get("url"),
            "article_published_at": article_data.get("published_at"),
            "article_title": article_data.get("title"),
            # Financial data
            "amount": attrs.get("amount"),
            "amount_normalized": attrs.get("amount_normalized"),
            # Product data
            "product": attrs.get("product"),
            "product_data": attrs.get("product_data"),
            # Various fields
            "effective_date": attrs.get("effective_date"),
            "event": attrs.get("event"),
            "financing_type": attrs.get("financing_type"),
            "financing_type_normalized": attrs.get("financing_type_normalized"),
            "headcount": attrs.get("headcount"),
            "job_title": attrs.get("job_title"),
            "recognition": attrs.get("recognition"),
            "vulnerability": attrs.get("vulnerability"),
            # Tags
            "asset_tags": attrs.get("assets_tags", []),
            "financing_type_tags": attrs.get("financing_type_tags", []),
            "job_title_tags": attrs.get("job_title_tags", []),
            "product_tags": attrs.get("product_tags", []),
        }
        events.append(transformed_event)

    return events


all_events = []
seen_ids = set()

for company in companies:
    print(f"Getting news for {company.get('domain')}")
    company_news = get_news(company.get("domain"))
    events = transform_raw_data(company.get("id"), company_news)
    # Deduplicate events based on id
    events = {event["id"]: event for event in events}.values()

    for event in events:
        if event["id"] not in seen_ids:
            all_events.append(event)
            seen_ids.add(event["id"])

    # Batch upsert when we have enough events
    if len(all_events) >= 100:
        upsert_events = postgresql.insert(db.schema.classes.predict_leads_news).values(
            all_events
        )
        upsert_events = upsert_events.on_conflict_do_update(
            index_elements=["id"],
            set_={
                key: getattr(upsert_events.excluded, key)
                for key in all_events[0].keys()
            },
        )

        try:
            db.session.execute(upsert_events)
            db.session.commit()
            all_events = []  # Clear the batch
            print("Successfully upserted batch of events")
        except Exception as e:
            print(f"Error upserting batch: {e}")
            db.session.rollback()

# Upsert any remaining events
if all_events:
    upsert_events = postgresql.insert(db.schema.classes.predict_leads_news).values(
        all_events
    )
    upsert_events = upsert_events.on_conflict_do_update(
        index_elements=["id"],
        set_={
            key: getattr(upsert_events.excluded, key) for key in all_events[0].keys()
        },
    )

    try:
        db.session.execute(upsert_events)
        db.session.commit()
        print("Successfully upserted final batch of events")
    except Exception as e:
        print(f"Error upserting final batch: {e}")
        db.session.rollback()
