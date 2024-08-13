import pandas as pd
import plotly.express as px

def build_strategy_comparison_chart(data: pd.DataFrame) -> px.bar:
    chart_title = 'Comparison of Different Portfolio Strategies'

    data.rename(columns = {'strategy': 'Strategy', 'total': 'Total'}, inplace = True)

    figure = px.bar(data, x = 'Strategy', y = 'Total', title = chart_title)

    return figure