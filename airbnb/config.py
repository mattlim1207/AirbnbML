DEV_DB = 'sqlite:///airbnb.db'

pg_user = 'admin'
pg_pw = 'password'
pg_db = 'airbnb'
pg_host = 'localhost'
pg_port = 5000

PROD_DB = f'postgresql://{pg_user}:{pg_pw}@{pg_host}:{pg_port}/{pg_db}'