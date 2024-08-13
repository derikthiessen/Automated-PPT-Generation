import pandas as pd
import os

from Chart_Builders.all_stock_returns_scatter_chart import build_all_stock_returns_scatter_chart as build_chart

class All_Stock_Returns_Slide:
    def __init__(self, 
                 data: pd.DataFrame,
                 image_directory: str
                 ):
        self.data = data
        self.image_directory = image_directory
        
        self.title = 'Performance of All Portfolio Stocks from IPO Dates'
        self.scatter_chart_path = self.build_scatter_chart()
    
    def build_scatter_chart(self) -> str:
        figure = build_chart(self.data)

        png_file = 'all_stock_returns_scatter_chart.png'
        path = os.path.join(self.image_directory, png_file)

        print('Beginning to save the all stock returns scatter chart')
        figure.write_image(path)
        print('Successfully saved the image')

        return path