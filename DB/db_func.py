import logging

import psycopg2.extras
from pandas.tseries.holiday import after_nearest_workday

from DB.db import conn
import csv
import pandas as pd



def db_insert_new_group(groups_id, name):
    with conn.cursor() as cur:
        insert_query = "INSERT INTO groups (groups_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        cur.execute(insert_query, (groups_id, name))
        conn.commit()
        logging.info(f'группа {groups_id} с названием {name} добавлена')


def db_select_all_group():
    with conn.cursor() as cur:
        select_query = "select groups_id from groups"
        cur.execute(select_query)
        ret = cur.fetchall()
        group_id_list = []
        for group_id in ret:
            group_id_list.append(group_id[0])
        logging.info(group_id_list)
        return group_id_list


def db_select_group():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        select_query = "select groups_id, name from groups"
        cur.execute(select_query)
        res = cur.fetchall()
        res_list = [dict(row) for row in res]
        return res_list


def db_insert_new_user(user_id, username, fio, group_id):
    with conn.cursor() as cur:
        insert_query = "INSERT INTO users (chat_id, username, fio, group_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        cur.execute(insert_query,(int(user_id), username, fio, group_id))
        conn.commit()


def db_select_name_group(group_id):
    with conn.cursor() as cur:
        select_query = "select name from groups where groups_id = %s"
        cur.execute(select_query, (int(group_id), ))
        ret = cur.fetchone()
        return ret[0]


def db_select_users_in_group(group_id):
    with conn.cursor() as cur:
        select_query = "SELECT chat_id from users where group_id = %s"
        cur.execute(select_query, (group_id, ))
        ret = cur.fetchall()
        list_id = []
        for x in ret:
            list_id.append(x[0])
        return list_id





def export_csv():
    file = pd.read_sql("""SELECT 
    users.chat_id,
    users.username,
    users.fio,
    users.group_id,
    groups.name from users
    LEFT JOIN groups
    ON groups.groups_id = users.group_id""", conn)
    file.to_excel('reports/report.xlsx', index=False)
    return 'отчет загружен exel'

# export_csv()

def export_one_csv(id_group):
    name = db_select_name_group(id_group)
    new_name = name.replace(" ", "_")
    select_query = "SELECT * from users where group_id = {}".format(id_group)
    file = pd.read_sql(select_query, conn)
    file.to_excel(f'reports/{str(new_name)}.xlsx', index=False)
    return 'отчет загружен exel'