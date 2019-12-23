#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import fastapi
import logging
import os
import starlette.responses

from util import parcels_to_geojson

# FastAPI server
app = fastapi.FastAPI()

# logger
logger = logging.getLogger('server')

# endpoints
@app.get("/trajectory")
async def trajectory(lat: float, lon: float, t0: datetime.datetime):
    content = parcels_to_geojson(lat, lon, t0)
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
