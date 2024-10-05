from typing import Callable, Dict, Any
from flask import Response
import folium
import httpx
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"
studeyname_to_collection_name={
    "GOSAT-based Top-down Total and Natural Methane Emissions":"gosat-based-ch4budget-yeargrid-v1",
    "MiCASA Land Carbon Flux":"micasa-carbonflux-daygrid-v1",
    "OCO-2 GEOS Column CO₂ Concentrations":"oco2geos-co2-daygrid-v10r",
    "OCO-2 MIP Top-Down CO₂ Budgets":"oco2-mip-co2budget-yeargrid-v1",
    "ODIAC Fossil Fuel CO₂ Emissions":"odiac-ffco2-monthgrid-v2023",
    "TM5-4DVar Isotopic CH₄ Inverse Fluxes":"tm54dvar-ch4flux-monthgrid-v1",
    "Wetland Methane Emissions, LPJ-EOSIM Model_monthly":"lpjeosim-wetlandch4-daygrid-v2",
}
collection_name_to_study_name={
            "oco2-mip-co2budget-yeargrid-v1":"OCO-2 MIP Top-down CO₂ Budgets"
            ,
            "odiac-ffco2-monthgrid-v2023":"ODIAC Fossil Fuel CO₂ Emissions"
            , 
            "oco2geos-co2-daygrid-v10r":"OCO-2 GEOS Column CO₂ Concentrations"
            ,
            "tm54dvar-ch4flux-monthgrid-v1":"TM5-4DVar Isotopic CH₄ Inverse Fluxes"
            ,
            "lpjeosim-wetlandch4-daygrid-v2":"Wetland Methane Emissions, LPJ-EOSIM Model"
            ,
            "gosat-based-ch4budget-yeargrid-v1":"GOSAT-based Top-down Total and Natural Methane Emissions"
            ,
            "eccodarwin-co2flux-monthgrid-v5":"Air-Sea CO₂ Flux, ECCO-Darwin Model v5"
            ,
            "micasa-carbonflux-daygrid-v1":"MiCASA Land Carbon Flux"
        
        }
collections_to_itemId = {
    "oco2-mip-co2budget-yeargrid-v1": "oco2-mip-co2budget-yeargrid-v1-",
    "odiac-ffco2-monthgrid-v2023": "odiac-ffco2-monthgrid-v2023-odiac2023_1km_excl_intl_",
    "tm54dvar-ch4flux-monthgrid-v1": "tm54dvar-ch4flux-monthgrid-v1-",
    "epa-ch4emission-yeargrid-v2express": "epa-ch4emission-yeargrid-v2express-",
    "vulcan-ffco2-yeargrid-v4": "vulcan-ffco2-yeargrid-v4-",
    "gosat-based-ch4budget-yeargrid-v1": "gosat-based-ch4budget-yeargrid-v1-",
    "eccodarwin-co2flux-monthgrid-v5": "eccodarwin-co2flux-monthgrid-v5-",
    "micasa-carbonflux-daygrid-v1": "micasa-carbonflux-daygrid-v1-",
    "lpjeosim-wetlandch4-daygrid-v2": "lpjeosim-wetlandch4-daygrid-v2-",
    "oco2geos-co2-daygrid-v10r": "oco2geos-co2-daygrid-v10r-",
    "sedac-popdensity-yeargrid5yr-v4.11":"sedac-popdensity-yeargrid5yr-v4.11-",
    "oco2geos-co2-daygrid-v10r":"oco2geos-co2-daygrid-v10r-",
    "gra2pes-ghg-monthgrid-v1":"gra2pes-ghg-monthgrid-v1-"
}
color_maps_dict={
    "purd":"PuRd",
    "rainbow":"rainbow",
    "magma":"magma"
}

UrlFunction = Callable[[Dict[str, Any], str, str, str,str], Response]

async def create_map(tile: str,asset:str,item,color:str,min,max) -> Response:
    base = folium.Map(location=[10.3214957, 31.7397001], max_bounds=True, min_zoom=3,zoom_start=3, tiles="OpenStreetMap", name="Normal map")
    borders_style = {
        'color': 'black',
        'weight': 1,
        'fill': True,
        'fillColor': 'white',
        'fillOpacity': 0.2
    }
    folium.GeoJson("eg.json", name="Focus on EGYPT", style_function=lambda x: borders_style,show=False).add_to(base)
    
    folium.TileLayer(
        tiles=tile, 
        attr="GHG", 
        opacity=0.5, 
        name=f"See {asset}",
        overlay=True, 
        min_zoom=3,
    ).add_to(base)
    cmap = plt.get_cmap(color_maps_dict[color])
    norm = plt.Normalize(vmin=min, vmax=max)  # Define vmin and vmax according to your data
    colormap = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    # Step 3: Define a linear colormap for the legend in Folium
    folium_colormap = folium.LinearColormap(
        colors=[cmap(i) for i in np.linspace(0, 1, 6)],  # Extract 6 colors evenly spaced
        vmin=min, vmax=max,
    )
    folium_colormap.add_to(base)
    
    folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', name="Height map", attr="opentopomap",show=False, min_zoom=3).add_to(base)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', name="live map",show=False, attr="Esri.WorldImagery", min_zoom=3).add_to(base)
    
    folium.LayerControl().add_to(base)
    
    return Response(base._repr_html_(), content_type='text/html')

def fetch_tiles(url: str) -> str:
    response = httpx.get(url)
    if response.status_code != 200:
        return None
    return response.json().get("tiles", [])[0]

async def generic_data_handler(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    max=item["assets"][asset_name]["raster:bands"][0]["statistics"]["maximum"]
    min=item["assets"][asset_name]["raster:bands"][0]["statistics"]["minimum"]
    rescale_values = {"max":item["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":item["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}
    color_map = color
    print("getting data...")
    url = (
        f"{RASTER_API_URL}/collections/{collection_name}/items/{item_id}/tilejson.json"
        f"?assets={asset_name}&color_formula=gamma+r+1.05&colormap_name={color_map}"
        f"&rescale={rescale_values['min']},{rescale_values['max']}"
    )
    
    tile = fetch_tiles(url)
    if tile is None:
        return "Error in get tiles"
    
    return await create_map(tile,asset_name,item,color_map,min,max)

async def OCO_2MIP(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)

async def ODIAC(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)

async def TM5_4DVar(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)

async def EPA_CH4Emission(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)

async def Vulcan_Fossil(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def Utilizing_the_Air_Sea_CO(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def MiCASA_Land_Carbon(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def Wetland_Methane_Emissions(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def OCO_2_GEOS(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def GOSAT_based(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def SEDAC_Gridded(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
async def GRAPES_Greenhouse(item: dict, asset_name: str, collection_name: str, item_id: str,color:str) -> Response:
    return await generic_data_handler(item, asset_name, collection_name, item_id,color)
collections_to_function: Dict[str, UrlFunction] = {
    "oco2-mip-co2budget-yeargrid-v1": OCO_2MIP,
    "odiac-ffco2-monthgrid-v2023": ODIAC,
    "tm54dvar-ch4flux-monthgrid-v1": TM5_4DVar,
    "epa-ch4emission-yeargrid-v2express": EPA_CH4Emission,
    "vulcan-ffco2-yeargrid-v4": Vulcan_Fossil,
    "gosat-based-ch4budget-yeargrid-v1":GOSAT_based,
    "eccodarwin-co2flux-monthgrid-v5":Utilizing_the_Air_Sea_CO,
    "micasa-carbonflux-daygrid-v1":MiCASA_Land_Carbon,
    "lpjeosim-wetlandch4-daygrid-v2":Wetland_Methane_Emissions,
    "oco2geos-co2-daygrid-v10r":OCO_2_GEOS,
    "sedac-popdensity-yeargrid5yr-v4.11":SEDAC_Gridded,
    "gra2pes-ghg-monthgrid-v1":GRAPES_Greenhouse
}