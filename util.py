#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timedelta
import glob
import numpy as np
import xarray as xr
from zeep import Client
from requestEDSdata import EDSrequestData
import netCDF4 as nc

from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4


class EDS:
    
    def __init__(self, start_date, end_date, x1, y1, x2, y2):
        self.start = start_date
        self.end = end_date
        self.x1 = x1 
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def get_data(self):

        client = Client('http://coastmap.com/eds20/eds.asmx?WSDL')
        
        result = client.service.GetData(
            Key='rpstest',
            SourceID=696,
            SourceName='Hycom_Global',
            OutputType=1,
            StartDate=self.start.strftime("%Y-%m-%dT%H:%M:%S"),
            EndDate=self.end.strftime("%Y-%m-%dT%H:%M:%S"),
            X1=self.x1,
            Y1=self.y1,
            X2=self.x2,
            Y2=self.y2,
            Zipped=False
        )

        while client.service.GetStatus(result) != 'COMPLETE ':
            if client.service.GetStatus(result) == 'COMPLETE ':
                print("Status: 'COMPLETE '")
                url = f'https://coastmap.com/edsoutput/{result}'
                print(f'URL: {url}')
                return url

    
def parcels_to_geojson(lat, lon, t0=(datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d'), 
                        t=(datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d'), dataset='HYCOM GLOBAL NAVY'): #'2010_0420'='HYCOM GLOBAL NAVY'
    
    # Download new files
    EDSrequestData(lat, lon, t0=t0,t=t, dataset=dataset)
    data = '/data/*'
    files = os.listdir('/data') # todo: nix this
    fname = 'parcels_out.nc'
    
    ds = nc.Dataset('/data/' + files[0])
    names = list(ds.variables.keys())

    # determine longitude and latitude variable names    
    if any(x == 'lon' for x in names):
        varlon = 'lon'
        varlat = 'lat'
    elif any(x == 'longitude' for x in names):
        varlon = 'longitude'
        varlat = 'latitude'
    else:
        varlon = 'Longitude'
        varlat = 'Latitude'
        
    # determine u and v variable names    
    if any(x == 'water_u' for x in names):
        varu = 'water_u'
        varv = 'water_v'
    elif any(x == 'uo' for x in names):
        varu = 'uo'
        varv = 'vo'
    else:
        varu = 'u'
        varv = 'v'
        
    # determine time variable name    
    if any(x == 'time' for x in names):
        vartime = 'time'
    else:
        vartime = 'MT'  
        
    # covert site location from -180 to 180 TO 0 to 360 (if dataset in 0-360)
    if any(ds[varlon][:] > 180): 
        if lon < 0:
            lon=360+lon
            
    if any(ds[varlat][:] > 180):
        if lat < 0:
            lat=360+lat    

    # Hydrodynamics
    # TODO: make input t0 an actual option
#    filenames = {'U': data, 'V': data}
#    variables = {'U': 'u', 'V': 'v'}
#    dimensions = {'lat': 'latitude', 'lon': 'longitude', 'time': 'time'}
    filenames = {'U': data, 'V': data}
    variables = {'U': varu, 'V': varv}
    dimensions = {'lat': varlat, 'lon': varlon, 'time': vartime}
    fset = FieldSet.from_netcdf(filenames, variables, dimensions, allow_time_extrapolation=True)

    # Particles
    pset = ParticleSet.from_list(
        fieldset=fset,
        pclass=JITParticle,
        lon=lon, #-88.386944
        lat=lat #28.736667
    )

    # Execute run and save results to output file
    pset.execute(
        AdvectionRK4,
        runtime=timedelta(days=len(files)), # todo: replace this with some other way 
        dt=timedelta(minutes=60),
        # https://github.com/OceanParcels/parcels/issues/704#issuecomment-567840058
        output_file=pset.ParticleFile(name=fname, outputdt=timedelta(hours=24))
    )

    # Load into xarray, then dataframe
    ds = xr.load_dataset(fname)
    df = ds.to_dataframe().reset_index(drop=True)
    
    # covert 0 to 360 TO -180 to 180
    df['lon'] = df.apply(lambda x: x.lon-360 if x.lon > 180 else x.lon, axis=1)
    df['lat'] = df.apply(lambda x: x.lat-360 if x.lat > 180 else x.lat, axis=1)
            
    # Geojson features
    features = []
    for val in df['trajectory'].unique():
        d = df[df['trajectory']==val]
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': list(zip(d.lon, d.lat))
            },
            'properties': {
                'metadata': {
                    'id': val
                },
                'data': {
                    'lon': {
                        'type': 'trajectory',
                        'units': 'degrees',
                        'times': list(d.time),
                        'values': list(d.lon)
                    },
                    'lat': {
                        'type': 'trajectory',
                        'units': 'degrees',
                        'times': list(d.time),
                        'values': list(d.lat)
                    },
                    'z': {
                        'type': 'trajectory',
                        'units': 'meters',
                        'times': list(d.time),
                        'values': list(d.z)
                    }
                }
            }
        }
        features.append(feature)
    geojson = {'type': 'FeatureCollection', 'features': features}

    # Convert time
    def time_converter(o):
        '''Convert time data type to json serializable string'''
        if isinstance(o, type(df.loc[0, 'time'])):
            return o.__str__()

    # Write geojson
    return json.loads(json.dumps(geojson, default=time_converter))
