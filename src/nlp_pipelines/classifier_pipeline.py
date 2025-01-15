import re
import nltk
#from nltk.corpus import satopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from openai import OpenAI
from math import sqrt  # Importing sqrt from the math module
from bertopic import BERTopic
import random
from supabase import create_client
import time
import tiktoken
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker

from bertopic_classifier import BERTopicClassifier
from embedder import EmbeddingPipeline

# Import the database session and schema from db.py
from utils.db import session, schema

def classify_companies():
    """
    Classify the companies into topics using BERTopic
    """

    # If no companies are provided, fetch them from the database
    companies_table = schema.classes.companies  # Adjust the table name as per your schema
    stmt = select(companies_table)
    result = session.execute(stmt).fetchall()
    companies_list_of_dicts = [dict(row) for row in result]
    if not companies_list_of_dicts:
        print("No companies found in the database.")
        return None

    embedding_pipeline = EmbeddingPipeline()

    companies_with_embeddings = embedding_pipeline.get_embeddings_from_objects(companies_list_of_dicts)

    if not companies_with_embeddings:
        print("No embeddings found, embed the descriptions first")
        return None

    bertopic_classifier = BERTopicClassifier()
    companies_with_topics = bertopic_classifier.classify_bertopic(companies_with_embeddings)

    return companies_with_topics

if __name__ == "__main__":
    classify_companies()