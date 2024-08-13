from sqlalchemy import create_engine
import pandas as pd
import random
from datetime import datetime, timedelta
import math
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

    portfolios_query = '''
        SELECT id, name, year_established, starting_capital
        FROM portfolios;
    '''

    portfolios_df = pd.read_sql(portfolios_query, engine)
    portfolios_df['day_established'] = portfolios_df['year_established'].apply(get_first_friday)

    stocks_query = '''
        SELECT s.id, s.shares_outstanding, s.ipo_date, p.price, p.date
        FROM stocks s
        LEFT JOIN stock_prices p
        ON s.id = p.stock_id;
    '''

    stocks_df = pd.read_sql(stocks_query, engine)

    stocks_ids_query = '''
        SELECT id
        FROM stocks;
    '''

    stocks_ids_df = pd.read_sql(stocks_ids_query, engine)

    portfolio_ids = portfolios_df['id'].tolist()
    portfolio_starting_capitals = portfolios_df['starting_capital'].tolist()
    portfolio_days_established = portfolios_df['day_established'].tolist()
    stock_ids = stocks_ids_df['id'].tolist()

    amount = len(portfolio_ids)

    stock_purchases = generate_all_stocks_purchased(stock_ids, amount)
    num_transactions = sum([len(purchases) for purchases in stock_purchases])

    first_dates_query = '''
        SELECT stock_id, date
        FROM stock_prices
        WHERE (stock_id, date) IN (
            SELECT stock_id, MIN(date)
            FROM stock_prices
            GROUP BY stock_id
        );
    '''

    first_dates_df = pd.read_sql(first_dates_query, engine)
    first_date_map = create_first_date_map(first_dates_df)

    transactions = create_transactions(first_date_map, portfolio_ids, portfolio_starting_capitals, portfolio_days_established, stocks_df, stock_purchases)
    
    print('Beginning loading into database')
    load_into_postgresql(transactions, db_name, user, password, host, port)
    print('Loading into database was successful')

def generate_num_different_stocks_purchased():
    choices = [num for num in range(5, 51, 5)]

    return random.choices(choices)[0]

def generate_all_num_different_stocks_purchased(amount = 200):
    return [generate_num_different_stocks_purchased() for i in range(amount)]

def generate_stocks_purchased(amount, stock_ids):
    return random.sample(stock_ids, k = amount)

def generate_all_stocks_purchased(stock_ids, amount = 200):
    num_purchases_per_portfolio = generate_all_num_different_stocks_purchased(amount)
    purchases_per_portfolio = []

    for num_purchases in num_purchases_per_portfolio:
        purchases = generate_stocks_purchased(num_purchases, stock_ids)
        purchases_per_portfolio.append(purchases)
    
    return purchases_per_portfolio

def create_first_date_map(stocks_df):
    return stocks_df.set_index('stock_id')['date'].to_dict()

def get_first_friday(year):
    first_day = datetime(year, 1, 1)
    days_to_friday = (4 - first_day.weekday()) % 7
    return first_day + timedelta(days = days_to_friday)

def create_transactions(first_date_map, portfolio_ids, portfolio_starting_capitals, portfolio_days_established, stocks_df, stock_purchases):
    df_portfolio_id = []
    df_stock_id = []
    df_shares = []
    df_date = []

    for i in range(len(portfolio_ids)):
        print(f'Starting on portfolio #{i + 1}')
        
        current_portfolio_id = portfolio_ids[i]
        current_portfolio_day_established = portfolio_days_established[i].date()
        current_portfolio_purchases = stock_purchases[i]
        num_purchases = len(current_portfolio_purchases)
        current_starting_capital = portfolio_starting_capitals[i]
        max_investment_per_stock = current_starting_capital / num_purchases

        for stock in current_portfolio_purchases:
            first_price_date = first_date_map[stock]
            purchase_date = first_price_date if first_price_date > current_portfolio_day_established else current_portfolio_day_established
            price_on_purchase_date = stocks_df.loc[(stocks_df['id'] == stock) & (stocks_df['date'] == purchase_date), 'price'].iat[0]
            shares_purchased = math.floor(max_investment_per_stock / price_on_purchase_date)

            df_portfolio_id.append(current_portfolio_id)
            df_stock_id.append(stock)
            df_shares.append(shares_purchased)
            df_date.append(purchase_date)

        df = {
            'portfolio_id': df_portfolio_id,
            'stock_id': df_stock_id,
            'shares': df_shares,
            'date': df_date
        }

    return pd.DataFrame(df)

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

def create_sql_tuples(table):
    tuples = []

    for index, row in table.iterrows():
        current_tuple = (row['portfolio_id'], row['stock_id'], row['shares'], row['date'])
        tuples.append(current_tuple)
    
    return tuples

def insert_rows(connection, rows):
    with connection.cursor() as cur:
        insert_query = '''
        INSERT INTO portfolio_holdings (portfolio_id, stock_id, shares, date)
        VALUES (%s, %s, %s, %s);
        '''
        for row in rows:
            cur.execute(insert_query, row)
        connection.commit()

main()