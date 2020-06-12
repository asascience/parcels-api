#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from datetime import timedelta

import numpy as np
import xarray as xr

from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4

def parcels_to_geojson(lat, lon, t0='2010_0420'):

    data = '/data/*'
    files = os.listdir('/data')
    fname = 'parcels_out'

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
        runtime=timedelta(days=len(files)),
        dt=timedelta(minutes=60),
        output_file=pset.ParticleFile(name=fname+'.nc', outputdt=timedelta(hours=24)) # https://github.com/OceanParcels/parcels/issues/704#issuecomment-567840058
    )

    # Load into xarray, then dataframe
    ds = xr.load_dataset(fname+'.nc')
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
