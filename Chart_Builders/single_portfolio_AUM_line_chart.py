import pandas as pd
import plotly.express as px

def build_single_portfolio_AUM_line_chart(benchmark_series: list[int], data: pd.DataFrame) -> px.line:    
    # Get portfolio ID
    portfolio_id = data.loc[0, 'id']

    # Get portfolio name
    portfolio_name = data.loc[0, 'name']
    
    # Initialize a variable to hold the remaining starting capital
    remaining_uninvested_capital = data.loc[0, 'starting_capital']

    # Initialize another variable to calculate the benchmark data off
    starting_capital = data.loc[0, 'starting_capital']

    # Initialize a set to hold the stocks already seen and purchased
    stocks_purchased = set()

    # Initialize lists to carry the dates, portfolio AUMs, and benchmark AUMs for each date
    dates = []
    AUMs_per_date = []
    benchmark_AUMs = []

    # Group the df by date
    date_groups = data.groupby('date')

    benchmark_counter = 0
    for date, group in date_groups:
        group_total_AUM = 0

        for index, row in group.iterrows():
            current_stock_id = row['stock_id']
            current_stock_value = row['price'] * row['shares_purchased']

            if current_stock_id not in stocks_purchased:
                remaining_uninvested_capital -= current_stock_value # Subtracting from uninvested capital because the current stock was just purchased this week
                stocks_purchased.add(current_stock_id)
            
            group_total_AUM += current_stock_value

        group_total_AUM += remaining_uninvested_capital
        group_total_AUM = round(group_total_AUM, 2)
        
        dates.append(date)
        AUMs_per_date.append(group_total_AUM)

        benchmark_value = starting_capital * benchmark_series[benchmark_counter]
        benchmark_AUMs.append(benchmark_value)
        benchmark_counter += 1

    df_AUM = pd.DataFrame({'Date': dates, 'Portfolio AUM': AUMs_per_date, 'Benchmark AUM': benchmark_AUMs})

    figure = px.line(df_AUM, x = 'Date', y = ['Portfolio AUM', 'Benchmark AUM'],
                     labels = {'value': 'AUM', 'variable': 'Series'},
                     title = f'Portfolio {portfolio_name} (ID #{portfolio_id}) AUM vs. Benchmark')

    figure.add_traces(px.area(df_AUM, x = 'Date', y = 'Portfolio AUM').data)

    figure.update_layout(
    yaxis=dict(
        tickvals=[0, 5000000, 10000000, 15000000, 20000000, 25000000, 30000000, 35000000, 40000000],  # Set specific tick values
        ticktext=['$0M', '$5M', '$10M', '$15M', '$20M', '$25M', '$30M', '$35M', '$40M']  # Corresponding labels
        )
    )

    return figure