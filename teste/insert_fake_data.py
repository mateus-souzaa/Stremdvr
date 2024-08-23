from pymongo import MongoClient
from faker import Faker
from bson.objectid import ObjectId
import random

# Configuração do MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client['stream_dvr']

# Coleções
users_collection = db['users']
groups_collection = db['groups']
companies_collection = db['companies']

# Criar instância do Faker
fake = Faker()

# Função para gerar dados fictícios de usuários
def generate_fake_users(num_users):
    users = []
    company_ids = [company['_id'] for company in companies_collection.find()]
    for _ in range(num_users):
        user = {
            "email": fake.email(),
            "senha": fake.password(length=12),
            "company_id": random.choice(company_ids)
        }
        users.append(user)
    return users

# Função para gerar dados fictícios de grupos
def generate_fake_groups(num_groups):
    groups = []
    for _ in range(num_groups):
        group = {
            "nome_grupo": fake.word()
        }
        groups.append(group)
    return groups

# Função para gerar dados fictícios de empresas
def generate_fake_companies(num_companies):
    companies = []
    for _ in range(num_companies):
        company = {
            "name": fake.company()
        }
        companies.append(company)
    return companies

# Inserir dados fictícios no MongoDB
def insert_fake_data():
    # Gerar e inserir empresas
    num_companies = 5
    companies = generate_fake_companies(num_companies)
    companies_collection.insert_many(companies)
    
    # Gerar e inserir grupos
    num_groups = 3
    groups = generate_fake_groups(num_groups)
    groups_collection.insert_many(groups)
    
    # Atualizar os IDs das empresas para uso dos usuários
    companies = list(companies_collection.find())
    
    # Gerar e inserir usuários
    num_users = 10
    users = generate_fake_users(num_users)
    users_collection.insert_many(users)

    print("Dados fictícios inseridos com sucesso!")

if __name__ == "__main__":
    insert_fake_data()
