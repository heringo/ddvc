# NLP Pipeline Documentation

## Overview

The NLP Pipeline is designed to process company data by extracting descriptions, generating embeddings, classifying topics using BERTopic, and storing the results in a database. This pipeline leverages OpenAI's embedding capabilities and BERTopic's topic modeling to provide insightful classifications and descriptions of company topics.

## Table of Contents

- [Architecture](#architecture)
- [Components](#components)
  - [Embedding Pipeline](#embedding-pipeline)
  - [BERTopic Classifier](#bertopic-classifier)
  - [Topic Descriptor](#topic-descriptor)
- [Workflow](#workflow)
- [Database Schema](#database-schema)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

## Architecture

The NLP Pipeline consists of several interconnected modules that handle different aspects of data processing:

1. **Data Extraction**: Fetches company data from the database.
2. **Preprocessing**: Cleans and prepares text data for embedding.
3. **Embedding Generation**: Creates vector representations of company descriptions using OpenAI's API.
4. **Topic Classification**: Classifies embeddings into topics using BERTopic.
5. **Topic Description**: Generates concise descriptions for each topic.
6. **Database Update**: Stores the classified topics and their descriptions back into the database.

## Components

### Embedding Pipeline

**File:** `ddvc/src/nlp_pipelines/utils/embedder.py`

The `EmbeddingPipeline` class is responsible for generating embeddings for company descriptions. It performs the following tasks:

- **Preprocessing**: Cleans the company descriptions by removing HTML tags, URLs, and extra whitespace.
- **Embedding Generation**: Utilizes OpenAI's API to generate embeddings in batches, respecting token limits and rate limits.
- **Integration**: Associates the generated embeddings back to the respective companies in the dataset.

**Key Functions:**

- `get_embeddings_from_objects`: Processes a list of company dictionaries to generate and attach embeddings.
- `get_embeddings_from_list_of_texts_with_rate_limit`: Handles batching and rate limiting for embedding requests.
- `count_tokens`: Counts the number of tokens in a text string based on the specified model.
- `minimal_text_preprocessing`: Cleans text data by removing unwanted elements while preserving meaningful content.

### BERTopic Classifier

**File:** `ddvc/src/nlp_pipelines/utils/bertopic_classifier.py`

The `BERTopicClassifier` class leverages the BERTopic library to classify company descriptions into meaningful topics.

**Key Functions:**

- `classify_bertopic`: Takes in a list of companies with embeddings and assigns topics using BERTopic.
- `clean_topic_name`: Cleans and refines topic names by removing unwanted characters and words.

### Topic Descriptor

**File:** `ddvc/src/nlp_pipelines/utils/topic_descriptor.py`

The `TopicDescriptor` class is responsible for generating concise descriptions for each identified topic and updating the database accordingly.

**Key Functions:**

- `get_topic_descriptions_and_upsert_in_db`: Orchestrates the retrieval of companies with topics, generates descriptions, and updates the database.
- `retrieve_companies_with_topics`: Fetches companies and their associated topics from the database.
- `build_topic_description_input`: Prepares input data for the description generation model by grouping and selecting top descriptions.
- `get_topic_description`: Uses OpenAI's ChatGPT to generate one-line descriptions for each topic.
- `batch_update_topics_with_descriptions_by_id`: Updates the database in batches with the new topic descriptions.

## Workflow

1. **Data Retrieval**: The pipeline begins by fetching company data from the database using SQLAlchemy.

2. **Preprocessing and Embedding**:
   - Company descriptions are preprocessed to remove noise.
   - Cleaned descriptions are split into manageable chunks.
   - Embeddings are generated using OpenAI's API, ensuring rate limits and token constraints are respected.

3. **Topic Classification**:
   - Generated embeddings are fed into BERTopic to classify each company into relevant topics.
   - Topic names are cleaned for clarity and consistency.

4. **Topic Description Generation**:
   - For each identified topic, the pipeline gathers top company descriptions.
   - OpenAI's ChatGPT generates concise one-line descriptions for each topic.
   
5. **Database Update**:
   - New topic names and descriptions are upserted into the database in batches to ensure efficiency and reliability.

## Database Schema

The pipeline interacts with the following database tables:

- **Companies**: Stores company information, including descriptions and associated topic IDs.
- **Topics**: Contains topic information, including names and descriptions.

**Schema Details:**

- **Companies Table**:
  - `id`: Primary key.
  - `description`: Text description of the company.
  - `description_embeddings`: Vector representation of the description.
  - `topic_id`: Foreign key linking to the Topics table.
  - `derived_topic`: Name of the derived topic.
  - `derived_topic_probability`: Probability score of the topic classification.

- **Topics Table**:
  - `id`: Primary key.
  - `topic_name`: Name of the topic.
  - `topic_description`: Concise description of the topic.

## Setup and Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repo/ddvc.git
   cd ddvc
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   - Rename `.env.example` to `.env` and update the necessary variables.

   ```bash
   cp ddvc/.env.example ddvc/.env
   ```

   - Edit `.env` with your OpenAI API key and database URL.

## Usage

To execute the NLP pipeline and classify companies into topics:

```bash
python -m src.nlp_pipelines.classifier_pipeline
```

This script will:

1. Fetch companies from the database.
2. Generate embeddings for each company's description.
3. Classify companies into topics using BERTopic.
4. Generate descriptions for each topic.
5. Update the database with the new topic information.

## Environment Variables

Ensure the following environment variables are set in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key for generating embeddings and topic descriptions.
- `DATABASE_URL`: The URL for your database (e.g., PostgreSQL, MySQL).

**Example `.env` File:**

```env
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Open a pull request detailing your changes.

## License

This project is licensed under the [MIT License](LICENSE).

---




