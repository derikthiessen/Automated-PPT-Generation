import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def build_total_fund_AUM_line_chart(weekly_rate: float, data: pd.DataFrame) -> px.line:
    # Get earliest date
    first_year = data['year_established'].min()
    first_day = find_first_friday(first_year)

    # Get number of days between first day and the last day with data
    last_day = datetime(2024, 5, 31)
    num_days = int((last_day - first_day).days)

    portfolio_groups = data.groupby('id')
    portfolio_years_established = data['year_established'].unique().tolist()

    portfolios = []

    # Dictionary to capture the capital added through external funding; 
    # whenever a new portfolio is created, its starting capital will be added as 
    # additional capital along with the year added
    years_capital_added = {year: 0 for year in portfolio_years_established}

    for id, portfolio_holdings in portfolio_groups:
        portfolio_instance = Portfolio(portfolio_holdings)
        
        portfolios.append(portfolio_instance)

        years_capital_added[portfolio_instance.year_established] += portfolio_instance.starting_capital

    portfolio_AUMs_per_date = []
    portfolio_dates = [(first_day + timedelta(days = i)).date() for i in range(0, num_days, 7)]
    portfolio_ids_seen = set()
    
    benchmark_fund_AUMs = []

    for date in portfolio_dates:
        total_fund_AUM_on_current_date = 0
        external_capital = 0

        # Loops through the portfolios, if the current portfolio has an AUM for the current date iteration,
        # then add that AUM to the total fund AUM amount
        for portfolio in portfolios:
            if date in portfolio.dates:
                total_fund_AUM_on_current_date += portfolio.AUMs[date]

                if portfolio.portfolio_id not in portfolio_ids_seen:
                    portfolio_ids_seen.add(portfolio.portfolio_id)
                    total_fund_AUM_on_current_date += portfolio.starting_capital
                    external_capital += portfolio.starting_capital

        total_fund_AUM_on_current_date = round(total_fund_AUM_on_current_date, 2)
        portfolio_AUMs_per_date.append(total_fund_AUM_on_current_date)
        
        if benchmark_fund_AUMs:
            previous_total = benchmark_fund_AUMs[-1]
            new_total = (previous_total + external_capital) * weekly_rate
            benchmark_fund_AUMs.append(new_total)
        else:
            benchmark_fund_AUMs.append(total_fund_AUM_on_current_date)

    df_graph = pd.DataFrame({'Date': portfolio_dates, 'Fund AUM': portfolio_AUMs_per_date, 'Benchmark AUM': benchmark_fund_AUMs})

    figure = px.line(df_graph, x = 'Date', y = ['Fund AUM', 'Benchmark AUM'],
                     labels = {'value': 'AUM', 'variable': 'Series'},
                     title = 'Derik Trading Company Fund AUM vs. Benchmark')
    
    figure.add_traces(px.area(df_graph, x = 'Date', y = 'Fund AUM').data)

    figure.update_yaxes(tickprefix = '$')

    return figure

def find_first_friday(year: int) -> datetime:
        first_day = datetime(year, 1, 1)
        first_day_type = first_day.weekday()
        days_until_friday = (4 - first_day_type) % 7
        days_until_friday = days_until_friday + 7 if days_until_friday < 0 else days_until_friday
        return first_day + timedelta(days = days_until_friday)


class Portfolio:
    def __init__(self, portfolio_holdings: pd.DataFrame):
        self.portfolio_holdings = portfolio_holdings
        self.portfolio_id = self.portfolio_holdings['id'].iloc[0]
        self.year_established = self.portfolio_holdings['year_established'].min()
        self.starting_capital = self.portfolio_holdings['starting_capital'].iloc[0]
        self.date_groups = self.portfolio_holdings.groupby('date')

        self.stocks_purchased = set()
        self.dates = []
        self.AUMs_per_date = []

        self.get_AUMs_per_date()
        self.AUMs = dict(zip(self.dates, self.AUMs_per_date))
        self.dates = set(self.dates)

    def get_AUMs_per_date(self) -> None:
        remaining_uninvested_capital = self.starting_capital
        
        for date, group in self.date_groups:
            group_total_AUM = 0

            for index, row in group.iterrows():
                current_stock_id = row['stock_id']
                current_stock_value = row['price'] * row['shares_purchased']

                if current_stock_id not in self.stocks_purchased:
                    remaining_uninvested_capital -= current_stock_value # Subtracting from uninvested capital because the current stock was just purchased this week
                    self.stocks_purchased.add(current_stock_id)
                
                group_total_AUM += current_stock_value

            group_total_AUM += remaining_uninvested_capital
            group_total_AUM = round(group_total_AUM, 2)
            
            self.dates.append(date)
            self.AUMs_per_date.append(group_total_AUM)