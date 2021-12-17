# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 16:56:42 2021

@author: Kelsey.Ruckert
"""
import requests    
from datetime import datetime
from datetime import timedelta
import numpy as np
    
def EDSrequestData(lat, lon, 
                   t0=(datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d'), 
                   t=(datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d'),
                   dataset='HYCOM GLOBAL NAVY'):#='HYCOM GLOBAL NAVY'
    # model=dataset.replace(' ', '_')
    
    # if dataset=='HYCOM GLOBAL NAVY':
    #     filemodel=dataset.replace(' ', '')
    #     filemodel=filemodel.lower()
    # else:
    #     filemodel=model
    
    if dataset=='HYCOM GLOBAL NAVY':
        model=dataset.replace(' ', '_')
        filemodel=dataset.replace(' ', '')
        filemodel=filemodel.lower() + '_'
    elif dataset=='HYCOM 3D R1':
        model=dataset.replace(' ', '_')
        filemodel=model.lower() + '_'
    elif dataset=='HYCOM GOM':
        model=dataset.replace(' ', '_')
        filemodel=model.lower()
    elif dataset=='COPERNICUS GLOBAL':
        model=dataset.replace(' ', '_')
        filemodel=model
    elif dataset=='CODAR STPS':
        model=dataset.replace(' ', '')
        filemodel=model.lower()
    else:
        model=dataset.replace(' ', '_')
        filemodel=model.lower()  

    north=lat+10
    west=lon-10
    east=lon+10
    south=lat-10
    
    date=t0    
    dateObj = datetime.strptime(date, '%Y-%m-%d')
    dateObjEnd = datetime.strptime(t, '%Y-%m-%d')
    dayDelta = dateObjEnd - dateObj 

    requestedDays = np.arange(dayDelta.days)
    
    for downloadDay in requestedDays:
        end_date = dateObj + timedelta(days=downloadDay.item())
        stringdate = end_date.strftime("%Y-%m-%d")
        
        if dataset=='HYCOM GLOBAL NAVY':
            filedate = end_date.strftime("%Y%m%d%H")
        elif dataset=='HYCOM 3D R1':
            filedate = end_date.strftime("%Y%m%d%H")
        elif dataset=='HYCOM GOM':
            end_date = end_date - timedelta(days=2) # 00:00 of the day is in the previous dates nc file
            filedate = end_date.strftime("%Y%m%d%H")
        elif dataset=='COPERNICUS GLOBAL':
            filedate = end_date.strftime("%Y%m%d")
        elif dataset=='CODAR STPS':
            end_date = end_date - timedelta(days=1) # 00:00 of the day is in the previous dates nc file
            filedate = end_date.strftime("%Y%m%d")
        elif 'HFRADAR' in dataset and dataset!='HFRADAR USWC':
            #stringdate = (end_date+timedelta(days=1)).strftime("%Y-%m-%d")
            end_date = end_date - timedelta(days=1)
            filedate = end_date.strftime("%Y%m%d") 
        else:
            filedate = end_date.strftime("%Y%m%d") 
        
        # http://edsdata.oceansmap.com/thredds/catalog/EDS/catalog.html
        # TRY HYCOM GLOBAL NAVY; HYCOM 3D R1; HYCOM GOM format (i.e., water_u, water_v, and depths)
        dataurl = ('http://edsdata.oceansmap.com/thredds/ncss/EDS/'+model+'/'+filemodel+
               filedate+'.nc?var=water_u&var=water_v&north='+str(north)+'&west='+str(west)+
               '&east='+str(east)+'&south='+str(south)+'&disableProjSubset=on&horizStride=1&time_start='+
               stringdate+'T00%3A00%3A00Z&time_end='+stringdate+
               'T00%3A00%3A00Z&timeStride=1&vertCoord=1&addLatLon=true&accept=netcdf')
        
        rthredds = requests.get(dataurl)
        
        # TRY COPERNICUS GLOBAL format if URL fails (i.e., uo, vo, and depths)
        if rthredds.status_code < 200 or rthredds.status_code > 229:
            dataurl = ('http://edsdata.oceansmap.com/thredds/ncss/EDS/'+model+'/'+filemodel+
                       filedate+'.nc?var=uo&var=vo&north='+str(north)+'&west='+str(west)+
                       '&east='+str(east)+'&south='+str(south)+'&disableProjSubset=on&horizStride=1&time_start='+
                       stringdate+'T00%3A30%3A00Z&time_end='+stringdate+
                       'T00%3A30%3A00Z&timeStride=1&vertCoord=1&addLatLon=true&accept=netcdf')
            rthredds = requests.get(dataurl)
            
            # TRY CODAR STPSformat if URL fails (i.e., u, v, and no depths)
            if rthredds.status_code < 200 or rthredds.status_code > 229:
                dataurl = ('https://edsdata.oceansmap.com/thredds/ncss/EDS/'+model+'/'+filemodel+
                       filedate+'.nc?var=u&var=v&north='+str(north)+'&west='+str(west)+
                       '&east='+str(east)+'&south='+str(south)+'&disableProjSubset=on&horizStride=1&time_start='+
                       stringdate+'T00%3A00%3A00Z&time_end='+stringdate+
                       'T00%3A00%3A00Z&timeStride=1&addLatLon=true&accept=netcdf')
                rthredds = requests.get(dataurl)
                # THROW ERROR if no formats match
                if rthredds.status_code < 200 or rthredds.status_code > 229:
                    raise Exception("Model " + model + " cannot be requested")
        
        # if dataset=='HYCOM GLOBAL NAVY':
        #     filedate = end_date.strftime("%Y%m%d%H")
        #     dataurl = ('http://edsdata.oceansmap.com/thredds/ncss/EDS/'+model+'/'+filemodel+'_'+
        #                filedate+'.nc?var=water_u&var=water_v&north='+str(north)+'&west='+str(west)+
        #                '&east='+str(east)+'&south='+str(south)+'&disableProjSubset=on&horizStride=1&time_start='+
        #                stringdate+'T00%3A00%3A00Z&time_end='+stringdate+
        #                'T00%3A00%3A00Z&timeStride=1&vertCoord=1&addLatLon=true&accept=netcdf')
        # else:
        #     filedate = end_date.strftime("%Y%m%d")
        #     dataurl = ('http://edsdata.oceansmap.com/thredds/ncss/EDS/'+model+'/'+filemodel+
        #                filedate+'.nc?var=uo&var=vo&north='+str(north)+'&west='+str(west)+
        #                '&east='+str(east)+'&south='+str(south)+'&disableProjSubset=on&horizStride=1&time_start='+
        #                stringdate+'T00%3A30%3A00Z&time_end='+stringdate+
        #                'T00%3A30%3A00Z&timeStride=1&vertCoord=1&addLatLon=true&accept=netcdf')
        
        # rthredds = requests.get(dataurl)
        
        # SAVE the data to NETCDF
        open('/data/' + filemodel + end_date.strftime("%Y%m%d") + '.nc', 'wb').write(rthredds.content)   
