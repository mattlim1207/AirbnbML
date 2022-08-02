DEV_DB = 'sqlite:///airbnb.db'

pg_user = 'postgres'
pg_pw = 'postgres'
pg_db = 'postgres'
pg_host = 'db'
pg_port = 5432

PROD_DB = f'postgresql://{pg_user}:{pg_pw}@{pg_host}:{pg_port}/{pg_db}'