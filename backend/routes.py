from flask import jsonify, abort, render_template_string, request
import time
import httpx
from Manager import collections_to_itemId, collections_to_function, collection_name_to_study_name
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"
def init_routes(app):

    @app.route('/')
    def read_root():
        return jsonify({"message": "Welcome to the Flask example!"})

    @app.route('/GetItem/<collectionName>/<assetName>/<datetime>/<color>')
    async def GetItem(collectionName, assetName, datetime, color):
        if collectionName not in collections_to_itemId:
            abort(400, description="Collection doesn't exist")
        
        start_time = time.time()
        item_id = collections_to_itemId.get(collectionName) + datetime
        
        try:
            async with httpx.AsyncClient() as client:
                items_response = await client.get(f"{STAC_API_URL}/collections/{collectionName}/items/{item_id}")
            
            elapsed_time = time.time() - start_time
            print(f"Request completed in {elapsed_time:.4f} seconds")

            if items_response.status_code != 200:
                abort(items_response.status_code, description="Error fetching items")
            
            items_response_json = items_response.json()
            func = collections_to_function.get(collectionName)
            if func:
                data = await func(items_response_json, assetName, collectionName, item_id, color)
                return data
            
        except Exception as e:
            abort(500, description=str(e))

        return jsonify("No data found"), 200

    @app.route('/Get_statistics/<collection_name>/<gas_type>/<asset_name>')
    def Get_statistics(collection_name,gas_type, asset_name):
        if collection_name not in collection_name_to_study_name:
            abort(400, description="Study doesn't exist")
        
        start_time = time.time()
        if collection_name=="lpjeosim-wetlandch4-daygrid-v2":
            return jsonify("There is no states for land area"),200
        egypt="Egypt"
        data_path = os.path.join(f'Statistics/{collection_name}/{egypt}' , f'{collection_name}_{asset_name}_{egypt}).xlsx')
        df_egypt = pd.read_excel(data_path)
        #world_data
        world="world"
        data_path = os.path.join(f'Statistics/{collection_name}/{world}' , f'{collection_name}_{asset_name}_{world}).xlsx')
        df_world = pd.read_excel(data_path)
        if list(df_egypt.columns).__contains__("start_datetime"):
            df_world['datetime'] = pd.to_datetime(df_world['start_datetime'])
            df_egypt['datetime'] = pd.to_datetime(df_egypt['start_datetime'])
        elif list(df_egypt.columns).__contains__("datetime"):
            df_world['datetime'] = pd.to_datetime(df_world['datetime'])
            df_egypt['datetime'] = pd.to_datetime(df_egypt['datetime'])
        sorted_df_egypt=df_world.sort_values(by='datetime')
        sorted_df_world=df_egypt.sort_values(by='datetime')
        fig_title="Compare between"
        fig_min = go.Figure()
        fig_max = go.Figure()
        fig_mean = go.Figure()
        fig_min.add_trace(go.Scatter(x=sorted_df_egypt["datetime"][:10],y=sorted_df_egypt['min'],mode='lines+markers',
                    line = dict(color='red', width=3,),name='min egypt'))
        fig_min.add_trace(go.Scatter(x=sorted_df_world["datetime"][:10],y=sorted_df_world['min'],mode='lines+markers',
                    line = dict(color='blue', width=3,),name=' min world'))
        fig_max.add_trace(go.Scatter(x=sorted_df_egypt["datetime"][:10],y=sorted_df_egypt['max'],mode='lines+markers',
                    line = dict(color='green', width=3,),name='max Egypt'))
        fig_max.add_trace(go.Scatter(x=sorted_df_world["datetime"][:10],y=sorted_df_world['max'],mode='lines+markers',
                    line = dict(color='yellow', width=3,),name='max world'))
        #mean data
        fig_mean.add_trace(go.Scatter(x=sorted_df_egypt["datetime"][:10],y=sorted_df_egypt['mean'],mode='lines+markers',
                    line = dict(color='black', width=3,),name='mean Egypt'))
        fig_mean.add_trace(go.Scatter(x=sorted_df_world["datetime"][:10],y=sorted_df_world['mean'],mode='lines+markers',
                    line = dict(color='gray', width=3,),name='mean world'))
        fig_min.update_layout(legend_title="Plot legend",
        title={
            'text': f"{fig_title} {egypt} and {world}",
            'font_size':30,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        fig_min.update_xaxes(title={'text':'Time','font_size':20})
        fig_min.update_yaxes(title={'text':f'{gas_type} produced','font_size':20})
        fig_max.update_layout(legend_title="Plot legend",
        title={
            'text': f"{fig_title} {egypt} and {world}",
            'font_size':30,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        fig_max.update_xaxes(title={'text':'Time','font_size':20})
        fig_max.update_yaxes(title={'text':f'{gas_type} produced','font_size':20})
        fig_mean.update_layout(legend_title="Plot legend",
        title={
            'text': f"{fig_title} {egypt} and {world}",
            'font_size':30,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        fig_mean.update_xaxes(title={'text':'Time','font_size':20})
        fig_mean.update_yaxes(title={'text':f'{gas_type} produced','font_size':20})
        html_fig1 = pio.to_html(fig_min, full_html=False)
        html_fig2 = pio.to_html(fig_max, full_html=False)
        html_fig3 = pio.to_html(fig_mean, full_html=False)
        combined_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Plotly Charts</title>
            </head>
            <body>
                <div>{html_fig1}</div>
                <div>{html_fig2}</div>
                <div>{html_fig3}</div>
            </body>
            </html>
        """
        elapsed_time = time.time() - start_time
        print(f"Request completed in {elapsed_time:.4f} seconds")
        return render_template_string(combined_html)
