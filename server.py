#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import fastapi
import logging
import os
import glob
import starlette.responses
from starlette.middleware.cors import CORSMiddleware

from util import parcels_to_geojson

app = fastapi.FastAPI()

origins = [
    "http://localhost:5000",
    "http://localhost:8080",
    "localhost/:180",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logger
logger = logging.getLogger('server')

# endpoints
@app.get("/trajectory")
async def trajectory(lat: float, lon: float, t0: str, t:str, dataset: str):#datetime.datetime
    # remove data files (if any preexist)
    data = '/data/*'
    files = glob.glob(data)
    for f in files:
        os.remove(f)
        
    content = parcels_to_geojson(lat, lon, t0, t, dataset)#='HYCOM GLOBAL NAVY'
    return starlette.responses.JSONResponse(content=content)


# server
def main():
    import uvicorn
    headers = [
        ('Server', 'asyncio')
    ]
    PORT = int(os.getenv('UPLOAD_PORT', 5000))
    uvicorn.run(app, host='0.0.0.0', port=PORT, log_level="info", headers=headers)

if __name__ == "__main__":
    main()
