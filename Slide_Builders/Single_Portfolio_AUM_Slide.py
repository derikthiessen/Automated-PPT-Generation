import pandas as pd
import os

from Chart_Builders.single_portfolio_AUM_line_chart import build_single_portfolio_AUM_line_chart as build_spAUM_line_chart
from Chart_Builders.single_portfolio_AUM_bar_chart import build_single_portfolio_AUM_bar_chart as build_spAUM_bar_chart

class Single_Portfolio_AUM_Slide:
    NUM_DAYS_PER_YEAR = 365.25 # .25 to account for leap years
    
    def __init__(self, 
                 data: pd.DataFrame,
                 benchmark_rate: float, 
                 benchmark_series: list, 
                 image_directory: str
                 ) -> None:
        
        self.image_directory = image_directory
        
        self.data = data
        self.portfolio_name = self.data.loc[0, 'name']
        self.portfolio_id = self.data.loc[0, 'id']
        self.num_years = self.get_num_years(self.data)
        self.annualized_portfolio_return = self.get_annualized_portfolio_return(self.data)
        self.benchmark_rate = benchmark_rate
        self.benchmark_series = benchmark_series
        self.starting_capital = self.data.loc[0, 'starting_capital']
        self.final_portfolio_value = self.get_portfolio_value(self.data)
        self.benchmark_portfolio_value = self.get_benchmark_value()
        self.year_established = self.data.loc[0, 'year_established']
        self.num_stocks_held = len(self.data['stock_id'].unique())

        self.title = f'Portfolio {self.portfolio_name} Performance'

        self.line_chart_path = self.build_line_chart(self.data, self.benchmark_series)
        self.bar_chart_path = self.build_bar_chart()
    
    def get_num_years(self, data: pd.DataFrame):
        first_date = data['date'].min()
        last_date = data['date'].max()

        return ((last_date - first_date).days) / Single_Portfolio_AUM_Slide.NUM_DAYS_PER_YEAR

    def get_annualized_portfolio_return(self, data: pd.DataFrame):
        initial_value = data.loc[0, 'starting_capital']

        final_portfolio_value = self.get_portfolio_value(data)
        
        cagr = (final_portfolio_value / initial_value) ** (1 / self.num_years) - 1

        return cagr
    
    def get_portfolio_value(self, data: pd.DataFrame):
        last_date = data['date'].max()

        groups = data.groupby('date')
        portfolio_holdings = groups.get_group(last_date)

        final_portfolio_value = 0
        
        for index, row in portfolio_holdings.iterrows():
            final_portfolio_value += row['shares_purchased'] * row['price']
        
        return round(final_portfolio_value, 2)

    def get_benchmark_value(self):
        return round(self.starting_capital * ((1 + self.benchmark_rate) ** self.num_years), 2)

    def build_line_chart(self, data: pd.DataFrame, benchmark_series: list):
        figure = build_spAUM_line_chart(benchmark_series, data)

        png_file = f'portfolio_{self.portfolio_name}_id_{self.portfolio_id}_AUM_line.png'
        path = os.path.join(self.image_directory, png_file)

        print('Beginning to save the single portfolio AUM line chart image')
        figure.write_image(path)
        print('Successfully saved the image')

        return path

    def build_bar_chart(self):
        figure = build_spAUM_bar_chart(self.final_portfolio_value, self.benchmark_portfolio_value, self.portfolio_name, self.portfolio_id)

        png_file = f'portfolio_{self.portfolio_name}_id_{self.portfolio_id}_AUM_bar.png'
        path = os.path.join(self.image_directory, png_file)

        print('Beginning to save the single portfolio AUM bar chart image')
        figure.write_image(path)
        print('Successfully saved the image')

        return path