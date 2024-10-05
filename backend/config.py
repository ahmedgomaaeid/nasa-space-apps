import os

class Config:
    STAC_API_URL = os.getenv('STAC_API_URL', 'default_stac_api_url')
    RASTER_API_URL = os.getenv('RASTER_API_URL', 'default_raster_api_url')
