import re, time, tiktoken, os
from openai                 import OpenAI
from dotenv                 import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openAI_client = OpenAI(api_key=openai_api_key,)


class EmbeddingPipeline:
    """
    Class to get the embeddings from the companies
    """
    def __init__(self):
        pass

    def get_embeddings_from_objetcs(self, companies_list_of_dicts:list):


        for company in companies_list_of_dicts:
            if not company['description']:
                company['description'] = 'no description'

            company['description'] = minimal_text_preprocessing(company['description'])

        cleaned_descriptions = [company['description'] for company in companies_list_of_dicts]
        chunk_size = 500

        # Initialize an empty list to store all embeddings
        all_embeddings = []

        # Process the cleaned descriptions in chunks
        for i in range(0, len(cleaned_descriptions), chunk_size):
            # Get the current chunk of descriptions
            chunk = cleaned_descriptions[i:i + chunk_size]
            
            # Get embeddings for the current chunk
            chunk_embeddings = get_embeddings_from_list_of_texts(chunk)
            
            # Append the chunk embeddings to the all_embeddings list
            all_embeddings.extend(chunk_embeddings)

        if not all_embeddings : 
            print("No embeddings found")
            return None
        all_embeddings = [embedding.embedding for embedding in all_embeddings]
        for company, embedding in zip(companies_list_of_dicts, all_embeddings):
            company['description_embeddings'] = embedding
        
        return companies_list_of_dicts


def get_embeddings_from_list_of_texts_with_rate_limit(
    texts: list,
    model_name: str = "text-embedding-3-large",
    token_limit: int = 3500,
    wait_time: int = 63
):
    """
    Retrieves embeddings for a list of texts, ensuring we do not exceed 'token_limit'
    tokens in each batch/chunk. Once the batch is processed, waits 'wait_time' seconds
    before processing the next batch.

    :param texts: A list of text strings.
    :param model_name: Name of the embedding model (e.g., "text-embedding-3-large").
    :param token_limit: Maximum tokens allowed per chunk.
    :param wait_time: Number of seconds to wait after processing a chunk.
    :return: A list of embeddings (same order as input texts).
    """
    all_embeddings = []
    
    # Temporary storage for a batch
    current_batch_texts = []
    current_batch_tokens = 0
    
    for text in texts:
        # Count tokens for the current string
        tokens_for_text = count_tokens(text, model_name)
        
        # If a single text alone exceeds the token_limit, you can decide how to handle it:
        #   - Skip
        #   - Truncate
        #   - Or process individually, ignoring chunk
        if tokens_for_text > token_limit:
            print(f"Warning: A single text exceeded the token limit ({tokens_for_text} tokens). Skipping.")
            continue
        
        # If adding this text exceeds the chunk token limit, process the current batch first
        if current_batch_tokens + tokens_for_text > token_limit and current_batch_texts:
            try:
                response = openAI_client.embeddings.create(
                    model=model_name,
                    input=current_batch_texts,
                    encoding_format="float"
                )
                all_embeddings.extend(response.data)
            except Exception as e:
                print(f"An error occurred while fetching embeddings: {e}")
            
            # Reset the batch
            current_batch_texts = []
            current_batch_tokens = 0
            
            # Wait before processing the next chunk to respect rate limits
            time.sleep(wait_time)
        
        # Add this text to the current batch
        current_batch_texts.append(text)
        current_batch_tokens += tokens_for_text
    
    # Process any leftover texts in the final batch
    if current_batch_texts:
        try:
            response = openAI_client.embeddings.create(
                model=model_name,
                input=current_batch_texts,
                encoding_format="float"
            )
            all_embeddings.extend(response.data)
        except Exception as e:
            print(f"An error occurred while fetching embeddings: {e}")
    
    return all_embeddings

def count_tokens(text: str, model_name: str = "text-embedding-3-large") -> int:
    """Return the approximate number of tokens for the given text."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback if a direct encoding isn't found for the model
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))



def minimal_text_preprocessing(text):
    """
    Remove disruptive noise without losing context:
    1. Remove HTML tags
    2. Remove URLs
    3. Strip extra whitespace
    We preserve:
    - Punctuation
    - Case (upper/lower)
    - Most textual context
    """
    if text is None:
        return 'no description'
    # 1. Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # 2. Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # 3. Replace multiple spaces/tabs/newlines with a single space
    text = ' '.join(text.split())

    return text

def get_embeddings_from_list_of_texts(text:list):
    try:
        embeddings = openAI_client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
            encoding_format="float"
        )
        return embeddings.data
    except Exception as e:
        print(f"An error occurred while fetching embeddings: {e}")
        return None