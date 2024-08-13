import plotly.graph_objects as go

def build_single_portfolio_AUM_bar_chart(portfolio_value: float, benchmark_value: float, name: str, id_num: str) -> go.Figure:
    categories = ['Portfolio Value', 'Benchmark Value']
    values = [portfolio_value, benchmark_value]

    figure = go.Figure()

    # Add bars with data markers
    figure.add_trace(go.Bar(
        x = categories,
        y = values,
        name = 'Values',
        marker_color = ['blue', 'lightgrey'],
        width = 0.3,
        text = [f'${value:,.0f}' for value in values],  # Display whole dollar amounts
        textposition = 'outside',
        textfont = dict(size = 16),  # Increase the font size of the data markers
    ))

    # Update layout for better visualization
    figure.update_layout(
        title = f'Portfolio {name} (ID #{id_num}) Current AUM vs. Benchmark',
        xaxis_title = '',
        yaxis_title = 'AUM',
        yaxis = dict(
            tickformat = '$,.0s',  # Display values in millions
            range = [0, max(values) * 1.1]
        ),
        showlegend = False,
        width = 600,
        height = 400
    )

    return figure