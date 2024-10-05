from flask import Flask, jsonify, request, Response, abort,send_file, make_response
import httpx
from Manager import STAC_API_URL, RASTER_API_URL, collections_to_itemId, collections_to_function,studeyname_to_collection_name
import time
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import io
import os
def Egypt_vs_world(study_name,asset_name):
    #egypt_data
    egypt="Egypt"
    data_path = os.path.join(f'Statistics/{study_name}/{egypt}' , f'{study_name}_{asset_name}_{egypt}).xlsx')
    df_egypt = pd.read_excel(data_path, usecols=["start_datetime", "max","min","mean"])
    #world_data
    world="world"
    data_path = os.path.join(f'Statistics/{study_name}/{world}' , f'{study_name}_{asset_name}_{world}).xlsx')
    df_world = pd.read_excel(data_path, usecols=["start_datetime", "max","min","mean"])
    if list(df_egypt.columns).__contains__("start_datetime"):
        df_world['datetime'] = pd.to_datetime(df_world['start_datetime'])
        df_egypt['datetime'] = pd.to_datetime(df_egypt['start_datetime'])
    elif list(df_egypt.columns).__contains__("datetime"):
        df_world['datetime'] = pd.to_datetime(df_world['datetime'])
        df_egypt['datetime'] = pd.to_datetime(df_egypt['datetime'])
    fig_title="Compare between Maxmim of Egypt and World"
    fig = go.Figure()
    fig.add_trace(go.Line(x=df_egypt["datetime"][:10],y=df_egypt['mean'],mode='lines+markers',
                        line = dict(color='darkgreen', width=3,),name='max jkwfrbwehk'))
    fig.add_trace(go.Line(x=df_egypt["datetime"][:10],y=df_world['mean'],mode='lines+markers',
                        line = dict(color='tomato', width=3,),name='max'))


    fig.update_layout(legend_title="Plot legend",
        title={
                'text': f"{fig_title} {egypt} and {world}",
                'font_size':30,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
    fig.update_xaxes(title={'text':'Year','font_size':20})
    fig.update_yaxes(title={'text':f'CO2 produced','font_size':20})
    return Response(fig._repr_html_(), content_type='text/html')
def min_vs_max(study_name,asset_name,location)->Response:
    # Check if the collection exists
    start_time = time.time()
    print("Requesting data for", study_name)
    path=f"./Statistics/{study_name}/{location}/{study_name}_{asset_name}_{location}).xlsx"
    print(path)
    # Load data from Excel file
    try:
        if(not os.path.exists(path)):
            abort(400, description="Study doesn't exist")
        df = pd.read_excel(path, usecols=["start_datetime", "max","min","mean"])
        df['datetime'] = pd.to_datetime(df['start_datetime'])
    except Exception as e:
        abort(500, description="Failed to load data: " + str(e))
    if(df.empty):
        return jsonify("No data found"), 200
    print(df.columns)
    # Generate the plot
    # Create traces for the min and max values
    trace_min = go.Scatter(
        x=df['datetime'], 
        y=df['min'], 
        mode='lines', 
        name='Min Value',
        line=dict(color='red')  # Customize line style (optional)
    )

    trace_max = go.Scatter(
        x=df['datetime'], 
        y=df['max'], 
        mode='lines', 
        name='Max Value',
        line=dict(color='green')  # Customize line style (optional)
    )
    trace_mean = go.Scatter(
        x=df['datetime'], 
        y=df['mean'], 
        mode='lines', 
        name='mean Value',
        line=dict(color='blue')  # Customize line style (optional)
    )

    # Combine the traces in a list
    data = [trace_min, trace_max,trace_mean]
    # Define the layout
    layout = go.Layout(
        title='Min and Max and mean Values Over Time',
        xaxis_title='Datetime',
        yaxis_title='Values',
        xaxis=dict(type='date'),  # Ensures x-axis is treated as datetime
        showlegend=True
    )

    # Create the figure
    # fig = go.Figure(data=data, layout=layout)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['max'], mode='lines+markers',
                             line=dict(color='darkgreen', width=3,dash='dash'), name='max'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['min'], mode='lines+markers',
                             line=dict(color='tomato', width=3,dash='dash'), name='min',fill='tonexty'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['mean'], mode='lines+markers',
                             line=dict(color='tomato', width=3), name='mean'))


    fig.update_layout(legend_title="Line name",
                      title={
                          'text': f"The average and min and max {asset_name} production",
                          'font_size': 30,
                          'x': 0.5,
                          'xanchor': 'center',
                          'yanchor': 'top'})
    fig.update_xaxes(title={'text': 'Year', 'font_size': 20})
    fig.update_yaxes(title={'text': f'{asset_name} produced in ', 'font_size': 20})

    # fig = px.line(df, x='datetime', y='max', title='CO₂ concentrations')
    # fig = px.line(df, x='datetime', y='max', title='CO₂ concentrations')
    # Convert plotly figure to an in-memory image (PNG)
    # img = io.BytesIO()
    # website=fig._repr_html_()
    # img.seek(0)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Request completed in {elapsed_time:.4f} seconds")
    # Return the image as a response
    return Response(fig._repr_html_(), content_type='text/html')