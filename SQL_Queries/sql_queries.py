import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

authentication = os.getenv('DATABASE_URL')
engine = create_engine(authentication)

max_market_cap_query = '''
    WITH stock_results AS (
        SELECT s.id, s.shares_outstanding, p.date, p.price, p.price * s.shares_outstanding AS market_cap
        FROM stocks s
        LEFT JOIN stock_prices p
        ON s.id = p.stock_id
    )
    SELECT id, shares_outstanding, date, price, market_cap
    FROM stock_results
    WHERE market_cap = (SELECT MAX(market_cap) FROM stock_results);
'''
avg_market_cap_query = '''
    WITH stock_results AS (
        SELECT p.price * s.shares_outstanding AS market_cap
        FROM stocks s
        LEFT JOIN stock_prices p
        ON s.id = p.stock_id
    )
    SELECT AVG(market_cap)
    FROM stock_results;
'''

min_pm_assignments_query = '''
    WITH assignment_results AS (
        SELECT secondary_pm_id, COUNT(secondary_pm_id) AS total
        FROM portfolios
        GROUP BY secondary_pm_id
    )
    SELECT secondary_pm_id, total
    FROM assignment_results
    WHERE total = (SELECT MIN(total) FROM assignment_results);
'''

results = pd.read_sql(min_pm_assignments_query, engine)

print(results)