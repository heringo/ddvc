import re, os, json

from openai                             import OpenAI
from dotenv                             import load_dotenv
from utils.db                           import session, schema  # Import session and schema from db.py
from collections                        import defaultdict
from sqlalchemy.ext.declarative         import declarative_base
from sqlalchemy                         import Column, Integer, String, Float
from sqlalchemy.orm                     import sessionmaker
from sqlalchemy                         import create_engine


load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


openAI_client = OpenAI(api_key=openai_api_key,)


class TopicDescriptor:
    """
    Class to get the topic descriptions and upsert in the database
    """
    def __init__(self):
        pass

    def get_topic_descriptions_and_upsert_in_db(self):
        """
        Get the topic descriptions and upsert in the database
        """
        companies_with_topics_dicts = retrieve_companies_with_topics()
        topic_descriptions = build_topic_description_input(companies_with_topics_dicts)
        result_descriptions = get_topic_description(topic_descriptions)
        if result_descriptions.get('result'):
            final_topics= topic_descriptions['result']
            Base = declarative_base()

            engine = create_engine(DATABASE_URL, echo=False)  # Ensure DATABASE_URL is defined
            Session = sessionmaker(bind=engine)

            class Topic(Base):
                __tablename__ = 'topics'  # Ensure this matches your actual table name
                
                id = Column(Integer, primary_key=True)
                topic_name = Column(String, unique=True, nullable=False)  # Ensure topic_name is unique
                #topic_probability = Column(Float)  # Changed from Integer to Float
                topic_description = Column(String)  # Added topic_description

            # Perform the batch update by id
            with Session() as session:
                batch_update_topics_with_descriptions_by_id(session, final_topics, Topic, chunk_size=200)



def retrieve_companies_with_topics():
    """
    Retrieve the companies with topics from the database
    """
    # Map the tables to Python classes using schema from db.py
    Companies = schema.classes.companies
    Topics = schema.classes.topics

    # Query to join companies and topics based on topic_id
    def get_companies_with_topics():
        return session.query(Companies, Topics).filter(Companies.topic_id == Topics.id).all()

    # Example usage
    companies_with_topics = get_companies_with_topics()

    companies_with_topics_dicts = []
    for company, topic in companies_with_topics:
        company_dict = {column.name: getattr(company, column.name) for column in company.__table__.columns}
        company_dict['topic_name'] = topic.topic_name
        companies_with_topics_dicts.append(company_dict)

    return companies_with_topics_dicts


def build_topic_description_input(companies_with_topics_dicts:list):
    """
    Build the input for the topic description model
    """

    # 1. Group by topic_name
    """
    Given a list of companies, each with a topic_id, topic_name, topic_probability,
    and description, return a list of dicts. Each dict will contain the topic_id,
    topic_name, and up to two highest-probability descriptions.
    """
    # 1. Group companies by (topic_id, topic_name)
    topic_groups = defaultdict(list)
    for company in companies_with_topics_dicts:
        key = (company['topic_id'], company['topic_name'])
        topic_groups[key].append(company)
    
    # 2. For each group, sort companies by topic_probability (descending)
    results = []
    for (topic_id, topic_name), group_companies in topic_groups.items():
        # sort the group by topic_probability desc
        sorted_group = sorted(
            group_companies,
            key=lambda c: c['topic_probability'],
            reverse=True
        )
        
        # pick top two (or fewer if the group has less than 2)
        top_two = sorted_group[:5]
        
        # we’ll store None if there is only one company in this topic
        desc1 = top_two[0]['description'] if len(top_two) > 0 else None
        desc2 = top_two[1]['description'] if len(top_two) > 1 else None
        desc3 = top_two[2]['description'] if len(top_two) > 2 else None
        desc4 = top_two[3]['description'] if len(top_two) > 3 else None
        desc5 = top_two[4]['description'] if len(top_two) > 4 else None
        
        results.append({
            'topic_id': topic_id,
            'topic_name': topic_name,
            'company_description_1': desc1,
            'company_description_2': desc2,
            'company_description_3': desc3,
            'company_description_4': desc4,
            'company_description_5': desc5
        })
    
    return results


def get_topic_description(topics_dicts:list, model = "chatgpt-4o-latest", max_tokens=3000, temperature=0.3):

    system_prompt = f"You will be provided with a list of dicts with a topic_id, topic title and up to 5 companies descriptions that regard that topic.\n"
    system_prompt += "Your task is to give a one line max description of the topic and in case rename the topic title based on the descriptions.\n"
    system_prompt += "Please return a json with the following format: [{'topic_id': 'given_topic_id', 'new_topic_title': 'cleaned_topic_title', 'topic_description': 'description'}, {...}]"


    prompt = f" This is the list of dicts with the topic title and the company descriptions from where you need to extrapolate a topic one line max description and clean  or rename the topic title: \n\n{topics_dicts}\n\n"
    prompt +=  "Return a json with the following format:[{'topic_id': 'given_topic_id', 'new_topic_title': 'new_or_cleaned_topic_title', 'topic_description': 'description'}, {...}]\n"


    response = openAI_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format= { "type": "json_object" },
        #top_p=1
    )

    try:

        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print(f'Error decoding JSON')
        return {'classified_thesis':None, 'confidence_score':None}
    except Exception as e:
        print(f'Error processing response: {e}')
        return {'classified_thesis':None, 'confidence_score':None}




def batch_update_topics_with_descriptions_by_id(session, final_topics: list, TopicModel, chunk_size: int = 200):
    """
    Batch update topic_name and topic_description for multiple topics in chunks by matching id.

    :param session: SQLAlchemy session object.
    :param final_topics: List of dictionaries with 'topic_id', 'topic_title', and 'topic_description'.
    :param TopicModel: SQLAlchemy ORM model representing the topics table.
    :param chunk_size: Number of topics to update in each chunk.
    """
    
    # Add other columns as needed
    # Create a mapping from topic_id to topic_title and topic_description
    topic_map = {int(item['topic_id']): {
                    'topic_name': item['new_topic_title'],
                    'topic_description': item['topic_description']
                } for item in final_topics}
    
    # Query all topics with their id
    topics = session.query(TopicModel.id).all()
    
    # Prepare update mappings with id, topic_name, and topic_description
    update_mappings = []
    for topic in topics:
        topic_details = topic_map.get(topic.id)
        if topic_details:
            update_mappings.append({
                "id": topic.id,
                "topic_name": topic_details['topic_name'],
                "topic_description": topic_details['topic_description']
            })
    
    # Iterate in chunks and perform updates
    for i in range(0, len(update_mappings), chunk_size):
        chunk = update_mappings[i:i + chunk_size]
        try:
            for mapping in chunk:
                session.query(TopicModel).filter(TopicModel.id == mapping['id']).update({
                    "topic_name": mapping['topic_name'],
                    "topic_description": mapping['topic_description']
                })
            session.commit()
            print(f"Successfully updated {len(chunk)} topics in chunk {i // chunk_size + 1}.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred during bulk update in chunk {i // chunk_size + 1}: {e}")




