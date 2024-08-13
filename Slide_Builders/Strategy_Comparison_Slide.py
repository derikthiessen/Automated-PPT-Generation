import pandas as pd
import os

from Chart_Builders.strategy_comparison_bar_chart import build_strategy_comparison_chart as build_chart

class Strategy_Comparison_Slide:
    def __init__(self,
                 data: pd.DataFrame,
                 image_directory: str
                 ):
        
        self.data = data
        self.image_directory = image_directory

        self.title = 'Portfolio Strategy Comparison'

        self.bar_chart_path = self.build_bar_chart()
    
    def build_bar_chart(self) -> str:
        figure = build_chart(self.data)

        png_file = 'strategy_comparison_bar_chart.png'
        path = os.path.join(self.image_directory, png_file)

        print('Beginning to save strategy comparison chart')
        figure.write_image(path)
        print('Successfully saved image')

        return path