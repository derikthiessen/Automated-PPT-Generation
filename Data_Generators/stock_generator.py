import random
from datetime import datetime as dt

def main():
    amount = 1000

    tickers = get_tickers(amount)
    dates = get_dates(amount)
    shares = get_shares_outstanding(amount)
    continents = get_continents(amount)

    print(create_sql_insert(tickers, dates, shares, continents))

def get_tickers(amount = 500):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'.upper()

    tickers = set()

    while len(tickers) < amount:
        ticker = random.choices(alphabet, k = 4)

        ticker = ''.join(ticker)

        if ticker not in tickers:
            tickers.add(ticker)
    
    return list(tickers)

def get_dates(amount = 500):
    years = [year for year in range(1990, 2024)]
    months = [month for month in range(1, 13)]
    days = [day for day in range(1, 32)]
    dates = []

    for i in range(amount):

        while True:
            current_year = random.choices(years)[0]
            current_month = random.choices(months)[0]
            current_day = random.choices(days)[0]

            if not is_weekend(current_year, current_month, current_day): 
                date = dt(current_year, current_month, current_day)
                formatted_date = date.strftime('%Y-%m-%d')
                dates.append(formatted_date)
                break
    
    return dates

def is_weekend(year, month, day):
    try:
        date = dt(year, month, day)
    except ValueError:
        return True

    return date.weekday() >= 5

def get_shares_outstanding(amount = 500):
    totals = [total for total in range(50000, 1000000, 10000)]

    shares_outstanding_totals = []

    for i in range(amount):
        total = random.choices(totals)[0]
        shares_outstanding_totals.append(total)
    
    return shares_outstanding_totals

def get_continents(amount = 500):
    continents = ['NA', 'SA', 'EU', 'AF', 'AS', 'AU']

    continent_choices = []

    for i in range(amount):
        continent = random.choices(continents)[0]
        continent_choices.append(continent)
    
    return continent_choices

def create_sql_insert(tickers, ipo_dates, shares_outstanding_totals, continents):
    string = 'INSERT INTO stocks (ticker, ipo_date, shares_outstanding, continent) VALUES '
    string_lst = []

    for i in range(len(tickers)):
        current_ticker = tickers[i]
        current_ipo_date = ipo_dates[i]
        current_shares_oustanding = shares_outstanding_totals[i]
        current_continent = continents[i]

        current_string = f"('{current_ticker}', '{current_ipo_date}', {current_shares_oustanding}, '{current_continent}')"
        string_lst.append(current_string)
    
    return string + ', '.join(string_lst)

main()