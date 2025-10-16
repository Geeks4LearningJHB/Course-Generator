
#Astradb Connection for Vector_Database
secure_path=""
astradb_app_token=""
client_ID = ""
client_Secret=""
openAI_Key = ""
Astra_keyspace = ""
#langchain imports
from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings


#Cassandra Imports
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

#Dataset Import(s)
from datasets import load_dataset

#Configurations

Cloud_Config ={
    'Secure_connect_bundle': secure_path
}
# Auth Provider
auth_provider = PlainTextAuthProvider(client_ID, client_Secret)

# Cluster setup
cluster = Cluster(cloud=Cloud_Config, auth_provider=auth_provider)
astra_sess = cluster.connect()

#OpenAI
llm = OpenAI(open_Api_Key = openAI_Key)
myEmbedding = OpenAIEmbeddings(open_Api_Key = openAI_Key)

#Cassandra_Table_Creation_Tool for Astra

CassandrVstore = Cassandra(
    embedding=myEmbedding,
    session=astra_sess,
    table_name="qa_min_test"
)

print("loading data from hugging face")
myDataset = load_dataset("Biddls/Onion_News",split="train")
headlines = myDataset["text"][:50]

print("\nGenerating Embeddings & storing in astraDB")
CassandrVstore.add_texts(headlines)

print(f"inserted {len(headlines)} headlines.\n ")
