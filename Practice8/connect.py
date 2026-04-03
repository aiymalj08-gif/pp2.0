import psycopg2
from config import DB_CONFIG

def connect():
    return psycopg2.connect(**DB_CONFIG)#connects the created DB dictionary and connects it with psycopg2