import os, json
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import PGVector
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from kubernetes import client, config


topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT',"broyal-llama-demo"),
    topic='kubernetes_concepts',
)

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT',"broyal-llama-demo"),
    sub='kubernetes_concepts_subscription_client',
)



#loads document from url
def process_data(urls):
    loader = WebBaseLoader(urls)
    documents = loader.load()

    # Chunk all the kubernetes concept documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)
    print("%s chunks in %s pages" % (len(docs), len(documents)))
    return docs


# Load sentence transformer embeddings
def load_embeddings():
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device":"cpu"} # use {"device":"cuda"} for distributed embeddings

    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)


def get_connection_string():
    return PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=os.environ.get("PGVECTOR_HOST", "localhost"),
        port=int(os.environ.get("PGVECTOR_PORT", "5432")),
        database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
        user=os.environ.get("PGVECTOR_USER", "postgres"),
        password=os.environ.get("PGVECTOR_PASSWORD", "secretpassword"),
    )

def callback(message):
    print(message.data)
    # urls = ["https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"]
    urls = message.data.split(",")
    print("starting index of {urls}".format(urls=urls))
    docs = process_data(urls)
    embeddings = load_embeddings()

    db = PGVector(
        collection_name="kubernetes_concepts",
        connection_string=get_connection_string(),
        embedding_function=embeddings,
    )

    db.add_documents(docs)
    message.ack()

if os.getenv("DEBUG"):
    f = open("./../.svc", "r")
    secret = json.loads(f.read())
else:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    secret_str = v1.read_namespaced_secret("pubsub-svc", "default")

credentials = service_account.Credentials.from_service_account_info(secret)
with pubsub_v1.SubscriberClient(credentials=credentials) as subscriber:
    print("subscribing to {subscription_name}".format(subscription_name=subscription_name))
    subscriber.create_subscription(name=subscription_name, topic=topic_name)
    future = subscriber.subscribe(subscription_name, callback)