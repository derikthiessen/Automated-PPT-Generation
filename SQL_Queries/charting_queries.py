queries = dict()

single_portfolio_AUM_query = '''
    SELECT  
        p.id, 
        p.name,
        p.year_established, 
        p.starting_capital, 
        ph.stock_id, 
        ph.shares AS shares_purchased, 
        ph.date AS purchase_date,
        sp.price, 
        sp.date
    FROM portfolios p
    LEFT JOIN portfolio_holdings ph
    ON p.id = ph.portfolio_id
    LEFT JOIN stock_prices sp
    ON ph.stock_id = sp.stock_id AND sp.date >= ph.date
    WHERE p.id = 1
    ORDER BY sp.date;
'''
queries['single_portfolio_AUM_query'] = single_portfolio_AUM_query

total_fund_AUM_query = '''
    SELECT 
        p.id, 
        p.year_established, 
        p.starting_capital,
        ph.stock_id,
        ph.shares AS shares_purchased, 
        ph.date AS purchase_date,
        sp.price,
        sp.date
    FROM portfolios p
    LEFT JOIN portfolio_holdings ph
    ON p.id = ph.portfolio_id
    LEFT JOIN stock_prices sp
    ON ph.stock_id = sp.stock_id AND sp.date >= ph.date
    ORDER BY p.id, sp.date;
'''

queries['total_fund_AUM_query'] = total_fund_AUM_query

strategy_comparison_query = '''
    SELECT strategy, COUNT(strategy) AS total
    FROM portfolios
    GROUP BY strategy
    ORDER BY COUNT(strategy) DESC;
'''
queries['strategy_comparison_query'] = strategy_comparison_query

all_stock_returns_query = '''
    WITH joined AS (
        SELECT s.id, s.ticker, s.ipo_date, sp.date, sp.price, RANK() OVER (PARTITION BY s.id ORDER BY sp.date) AS rn
        FROM stocks s
        LEFT JOIN stock_prices sp
        ON s.id = sp.stock_id
    )

    SELECT id, ticker, ipo_date, date, price
    FROM joined
    WHERE rn = 1 OR date = '2024-05-31';
'''

queries['all_stock_returns_query'] = all_stock_returns_query