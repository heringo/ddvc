from sqlalchemy                                                 import select

from ddvc.src.nlp_pipelines.utils.bertopic_classifier           import BERTopicClassifier
from ddvc.src.nlp_pipelines.utils.embedder                      import EmbeddingPipeline
from ddvc.src.nlp_pipelines.utils.topic_descriptor              import TopicDescriptor

# Import the database session and schema from db.py
from utils.db                                                   import session, schema

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

    topic_descriptor = TopicDescriptor()
    topic_descriptor.get_topic_descriptions_and_upsert_in_db()

    return companies_with_topics

if __name__ == "__main__":
    classify_companies()