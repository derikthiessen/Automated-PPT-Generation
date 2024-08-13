import random
import pandas as pd
import numpy as np
import datetime
from sqlalchemy import create_engine 
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    authentication = os.getenv('DATABASE_URL')
    db_name = os.getenv('DB_NAME')
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    port = os.getenv('PORT')

    engine = create_engine(authentication)

    query = '''
    SELECT id, ticker, ipo_date, shares_outstanding
    FROM stocks;
    '''

    df = pd.read_sql(query, engine)

    shares_outstanding = df['shares_outstanding'].tolist()

    ipo_prices = generate_all_ipo_prices(shares_outstanding)

    ids = df['id'].tolist()
    ipo_dates = df['ipo_date'].tolist()
    stocks_info = zip(ids, ipo_dates, ipo_prices)
    stocks_info = {info[0]: [info[1], info[2]] for info in stocks_info}

    price_tables = generate_all_following_prices(stocks_info)
    
    results = add_all_ids(price_tables)
    all_dfs = []

    for df in results.values():
        all_dfs.append(df)
    
    table = pd.concat(all_dfs, ignore_index = True)
    
    load_into_postgresql(table, db_name, user, password, host, port)

def generate_ipo_price(shares_outstanding):
    max_market_cap = 250000000
    min_market_cap = 10000000
    min_percentage = min_market_cap / max_market_cap

    percentage = random.random()
    percentage = percentage if percentage >= min_percentage else min_percentage

    rounded_percentage = round(percentage, 8)

    market_cap = rounded_percentage * max_market_cap

    share_price = round(market_cap / shares_outstanding, 2)
    
    return share_price

def generate_all_ipo_prices(all_shares_outstanding):
    results = []

    for shares_outstanding in all_shares_outstanding:
        results.append(generate_ipo_price(shares_outstanding))
    
    return results

def find_next_friday(date):
    if date.weekday() == 4:
        return date
    
    days_ahead = 4 - date.weekday()  
    if days_ahead <= 0:
        days_ahead += 7

    return date + datetime.timedelta(days = days_ahead)

def generate_all_following_prices(stocks_info):
    results = dict()
    for key, value in stocks_info.items():
        results[key] = generate_following_prices(value[0], value[1])
    
    return results

def generate_following_prices(ipo_date, ipo_price):
    days = get_fridays(ipo_date)

    price_changes = [1 + (change / 100) for change in np.arange(-2.0, 2.5, 0.2)]
    last_price = ipo_price
    prices = [round(last_price, 2)]

    for i in range(len(days) - 1):
        current_change = random.choices(price_changes)[0]
        next_price = round(last_price * current_change, 2)
        prices.append(next_price)
        last_price = next_price
    
    return pd.DataFrame({'days' : days, 'prices' : prices})   

def get_fridays(ipo_date, end_date = datetime.date(2024, 5, 31)):
    next_friday = find_next_friday(ipo_date)
    
    fridays = []

    while next_friday <= end_date:
        fridays.append(next_friday)
        next_friday += datetime.timedelta(days = 7)
    
    return fridays

def add_all_ids(price_tables):
    results = dict()

    for key, value in price_tables.items():
        df = value
        df['id'] = key
        results[key] = df

    return results

def create_sql_tuples(table):
    tuples = []
    
    for index, row in table.iterrows():
        current_tuple = (row['id'], f'{row['days']}', row['prices'])
        tuples.append(current_tuple)

    return tuples

def load_into_postgresql(table, dbname, user, password, host, port):
    params = {
        'dbname': dbname,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }
    connection = psycopg2.connect(**params)
    rows = create_sql_tuples(table)

    print('Beginning row insertion')
    
    insert_rows(connection, rows)
    connection.close()

    print('Loading of all rows complete')

def insert_rows(connection, rows):
    with connection.cursor() as cur:
        insert_query = '''
        INSERT INTO stock_prices (stock_id, date, price)
        VALUES (%s, %s, %s);
        '''
        for row in rows:
            cur.execute(insert_query, row)
        connection.commit()

main()
