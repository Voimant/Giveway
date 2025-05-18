import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

with psycopg2.connect(user=os.getenv('USER'),
                      password=os.getenv('PASSWORD'),
                      port=os.getenv('PORT'),
                      database=os.getenv('DATABASE')) as conn:
    def create_db():
        """
        Функция, создающая структуру БД (таблицы)
        :return: База данных создана
        """
        with conn.cursor() as cur:
            create_query = """CREATE TABLE IF NOT EXISTS groups(
            groups_id BIGINT PRIMARY KEY,
            name VARCHAR(255));
            CREATE TABLE IF NOT EXISTS users(
            chat_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            fio TEXT,
            group_id BIGINT REFERENCES groups(groups_id));
            """
            cur.execute(create_query)
            conn.commit()
            return 'База данных создана'



print(create_db())
