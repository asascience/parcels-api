#!/usr/bin/env python
# coding: utf-8

# # Subset HYCOM data

# ### Request from EDS
# 
# End point is http://coastmap.com/eds20/eds.asmx
#  
# First call GetData. This will start the file generation and return the new file name
#  
# * EDSKey - use “rpstest”. This is the catch all eds key that we use for testing. I’d like to set up a new EDS key for this project once we get further along.
# * SourceID - Hycom Global is 696, use that.
# * SourceName - This is what the beginning of the file name will use. You can probably just use “Hycom_Global”
# * OutputType - Just use 1
# * Start Date - Start of the time frame you want to download, use yyyy-MM-ddTHH:mm:ss format
# * End Date - End of the time frame you want to download, use yyyy-MM-ddTHH:mm:ss format
# * X1 - Lower left longitude
# * Y1 - Lower left latitude
# * X2 - Upper right longitude
# * Y2 - Upper right latitude
# * Zipped - true to return a zip file, false to return the raw file
#  
# Once this comes back, take the file name it returns and call GetStatus in a loop:
#  
# FileName - the file name returned from GetData
#  
# This will return either “IN_PROCESS “ and the percentage finished, “ERROR” if something goes haywire, or “COMPLETE” when the file is finished and ready to actually download.
#  
# Once you get “COMPLETE”, you can download the file from https://coastmap.com/edsoutput/<FileName>, with whatever tool you want.
#  
# That’s it. The whole process should take 20 seconds, depending on the size of your AOI. A sample C# program you can use for a point of reference is https://ri-vsq-git-01.eur.rpsgroup.com/EDS/TestHarness/blob/master/Form1.cs. It’s just an internal tool, quick and dirty code, but it gets the job done, at least it will show you how we call the functions.

# In[ ]:


from datetime import datetime
from zeep import Client


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
                url = f'https://coastmap.com/edsoutput/{result}'
                print(f'URL: {url}')
                return url

            
eds = EDS(
    start_date=datetime(2020, 7, 1),
    end_date=datetime(2020, 7, 3),
    x1=-99,
    y1=19,
    x2=32,
    y2=-79
)

url = eds.get_data()


# In[ ]:


# !curl -o Hycom_Global_20200713132800919_79065_52296.NC https://coastmap.com/edsoutput/Hycom_Global_20200713132800919_79065_52296.NC


# In[ ]:





# ### From internal server 
# smb://ri-vsq-mdl-03/DataStore/Forcings/Currents/Public/Global/HYCOM_reanalysis/data

# In[ ]:


import os
import glob
from datetime import datetime, date, timedelta


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)
        

root = os.path.abspath('/Volumes/DataStore/Forcings/Currents/Public/Global/HYCOM_reanalysis/data')

start = date(2011, 12, 25)
end = date(2012, 2, 14)

files = [f'{root}/{str(start.year)}/HYCOM_Reanalysis_SRF_Global_{dt.strftime("%Y_%m%d")}.nc' for dt in daterange(start, end)]
files


# In[ ]:




