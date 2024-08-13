import pandas as pd
import plotly.express as px

def build_all_stock_returns_scatter_chart(data: pd.DataFrame) -> px.scatter:
    ticker_groups = data.groupby('id')

    # Key is the ticker, value will be a list with index 0 holding the ipo_date and index 1 holding the annualized return
    returns = dict()

    for id, group in ticker_groups:
        ticker = group.iloc[0]['ticker']
        ipo_date = group.iloc[0]['ipo_date']

        first_price = group.iloc[0]['price']
        last_price = group.iloc[1]['price']

        first_date = group.iloc[0]['date']
        last_date = group.iloc[1]['date']
        num_days = (last_date - first_date).days
        num_years  = num_days / 365

        annualized_return = round(((last_price / first_price) ** (1 / num_years) - 1) * 100, 2)

        returns[ticker] = [ipo_date, annualized_return]
    
    df = pd.DataFrame.from_dict(returns, orient = 'index', columns = ['ipo_date', 'annualized_return'])
    df['ticker'] = df.index

    average = df['annualized_return'].mean()

    figure = px.scatter(df, x='ipo_date', y='annualized_return', 
                 hover_data=['ticker'],  
                 title='IPO Date vs Annualized Return of All Stocks',
                 labels={'ipo_date': 'IPO Date', 'annualized_return': 'Annualized Return (%)'})

    figure.add_shape(
        type='line',
        x0=df['ipo_date'].min(),  
        y0=average,  
        x1=df['ipo_date'].max(),  
        y1=average,  
        line=dict(color='Red'),
        name='Average Return'
    )

    figure.add_annotation(
        x=df['ipo_date'].max() + pd.Timedelta(days=30), 
        y=average,
        text=f"Average Return: {average:.2f}%",
        showarrow=False,
        font=dict(color='Black'),
        xanchor='left' 
    )

    return figure