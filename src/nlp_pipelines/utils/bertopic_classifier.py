import re

import numpy as np
from bertopic import BERTopic


class BERTopicClassifier:
    """
    Class to classify the companies into topics using BERTopic
    """

    def __init__(self):
        pass

    def classify_bertopic(self, companies_list_of_dicts: list):
        """
        Classify the companies into topics using BERTopic
        """

        cleaned_descriptions = [
            company["description"] for company in companies_list_of_dicts
        ]

        all_embeddings = [
            company.get("description_embeddings")
            for company in companies_list_of_dicts
            if company.get("description_embeddings") is not None
        ]
        if not all_embeddings:
            print("No embeddings found, embed the descriptions first")
            return None

        all_embeddings_array = np.array(all_embeddings)

        topic_model = BERTopic(
            min_topic_size=10,
            calculate_probabilities=True,
            verbose=True,
            nr_topics="auto",
        )
        topics, probs = topic_model.fit_transform(
            cleaned_descriptions,
            all_embeddings_array,  # or embeddings
        )

        topic_info = topic_model.get_topic_info()
        print(topic_info)

        topic_names = topic_model.get_topic_info()["Name"]
        cleaned_topic_names = [
            clean_topic_name(clean_topic_name(name)) for name in topic_names
        ]

        for i, company in enumerate(companies_list_of_dicts):
            topic_id = topics[i]
            company["derived_topic"] = cleaned_topic_names[topic_id]
            company["derived_topic_probability"] = float(
                probs[i][topic_id]
            )  # Ensure it's a float

        return cleaned_topic_names


def clean_topic_name(topic_name):
    # Remove numbers and underscores
    cleaned_name = re.sub(r"\d+|_", " ", topic_name)
    # Remove articles (a, an, the) and extra spaces
    cleaned_name = re.sub(r"\b(and|a|an|the)\b", "", cleaned_name, flags=re.IGNORECASE)
    # Remove single letters at the beginning
    cleaned_name = re.sub(r"^\b[a-zA-Z]\b\s*", "", cleaned_name)
    # Strip leading/trailing spaces and return
    return cleaned_name.strip()
