import pandas as pd
import os

from Chart_Builders.total_fund_AUM_line_chart import find_first_friday, Portfolio, build_total_fund_AUM_line_chart as build_chart

class Total_Fund_AUM_Slide:
    def __init__(self, 
                 data: pd.DataFrame, 
                 image_directory: str,
                 benchmark_rate: float = 0.08 
                 ):
        
        self.data = data
        self.image_directory = image_directory
        self.title = 'Derik Trading Company AUM vs. Benchmark'
        
        self.benchmark_rate = benchmark_rate
        self.weekly_rate = self.get_weekly_rate()

        self.line_chart_path = self.build_line_chart()

    def get_weekly_rate(self):
        weekly_rate = (1 + self.benchmark_rate) ** (1 / 52)
        return weekly_rate

    
    def build_line_chart(self):
        figure = build_chart(self.weekly_rate, self.data)

        png_file = 'total_fund_AUM_line_chart.png'
        path = os.path.join(self.image_directory, png_file)

        print('Beginning to save the total fund AUM line chart image')
        figure.write_image(path)
        print('Successfully saved the image')

        return path