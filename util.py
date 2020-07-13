#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timedelta

import numpy as np
import xarray as xr
from zeep import Client

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

    
def parcels_to_geojson(lat, lon, t0='2010_0420'):

    data = '/data/*'
    files = os.listdir('/data') # todo: nix this
    fname = 'parcels_out.nc'

    # Hydrodynamics
    # TODO: make input t0 an actual option
    filenames = {'U': data, 'V': data}
    variables = {'U': 'u', 'V': 'v'}
    dimensions = {'lat': 'latitude', 'lon': 'longitude', 'time': 'time'}
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
