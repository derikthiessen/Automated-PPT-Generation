from sqlalchemy import create_engine
import pandas as pd
import random
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

    query = '''
        SELECT id, name
        FROM portfolio_managers;
    '''

    df = pd.read_sql(query, engine)
    ids = df['id'].tolist()

    strategies = generate_strategies()
    years_established = generate_years_established()
    starting_capitals = generate_starting_capitals()
    names = generate_portfolio_names()

    pm_assignments = assign_all_portfolio_managers(ids)
    primary_pms = pm_assignments[0]
    secondary_pms = pm_assignments[1]
    tertiary_pms = pm_assignments[2]

    portfolios_dictionary = {
        'name': names,
        'year_established': years_established,
        'starting_capital': starting_capitals,
        'strategy': strategies,
        'primary_pm_id': primary_pms,
        'secondary_pm_id': secondary_pms,
        'tertiary_pm_id': tertiary_pms
    }

    portfolios_table = pd.DataFrame(portfolios_dictionary)

    print('Successfully generated all data, beginning loading into postgresql')

    load_into_postgresql(portfolios_table, db_name, user, password, host, port)

    print('Successfully updated postgresql')

def generate_strategies(amount = 200):
    strategies = ['Active', 'Passive', 'Discretionary', 'Non-discretionary']

    selections = []

    for i in range(amount):
        selection = random.choices(strategies)[0]
        selections.append(selection)
    
    return selections

def generate_years_established(amount = 200, first_year = 1991):
    years = [year for year in range(first_year, 2023)]

    selections = []

    for i in range(amount):
        selection = random.choices(years)[0]
        selections.append(selection)
    
    return selections

def generate_portfolio_names(amount = 200):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'.upper()

    selections = []

    for i in range(amount):
        selection = random.choices(alphabet, k = 4)
        selection = ''.join(selection)
        selections.append(selection)
    
    return selections

def generate_starting_capitals(amount = 200):
    starting_amounts = [amount for amount in range(2000000, 20000000, 2000000)]

    selections = []

    for i in range(amount):
        selection = random.choices(starting_amounts)[0]
        selections.append(selection)
    
    return selections

def assign_all_portfolio_managers(pm_ids, amount = 200):
    num_ids = len(pm_ids)
    max_selections = math.ceil(amount / num_ids)

    primary_pms, secondary_pms, tertiary_pms = pm_ids * max_selections, pm_ids * max_selections, pm_ids * max_selections

    random.shuffle(primary_pms)
    random.shuffle(secondary_pms)
    random.shuffle(tertiary_pms)

    final_primary_pms = []
    final_secondary_pms = []
    final_tertiary_pms = []

    for i in range(amount):
        primary = primary_pms[i]
        secondary = secondary_pms[i]
        tertiary = tertiary_pms[i]
        
        while primary == secondary or primary == tertiary or secondary == tertiary:
            random.shuffle(secondary_pms)
            random.shuffle(tertiary_pms)
            secondary = secondary_pms[i]
            tertiary = tertiary_pms[i]
        
        final_primary_pms.append(primary)
        final_secondary_pms.append(secondary)
        final_tertiary_pms.append(tertiary)
    
    return [final_primary_pms, final_secondary_pms, final_tertiary_pms]

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
        current_tuple = (row['name'], row['year_established'], row['starting_capital'], row['strategy'],
                         row['primary_pm_id'], row['secondary_pm_id'], row['tertiary_pm_id'])
        tuples.append(current_tuple)
    
    return tuples

def insert_rows(connection, rows):
    with connection.cursor() as cur:
        insert_query = '''
        INSERT INTO portfolios (name, year_established, starting_capital, strategy, primary_pm_id, secondary_pm_id, tertiary_pm_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        for row in rows:
            cur.execute(insert_query, row)
        connection.commit()

def test_assign_all_portfolio_managers(pm_ids):
    for i in range(1000):
        results = assign_all_portfolio_managers(pm_ids)

        primary, secondary, tertiary = results[0], results[1], results[2]

        for j in range(len(primary)):
            if primary[j] == secondary[j] or primary[j] == tertiary[j] or secondary[j] == tertiary[j]:
                print('Tests failed, duplicate found')
                return
    
    print('Tests passed, no duplicate found')

main()