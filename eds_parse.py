#!/usr/bin/env python
# coding: utf-8

# ### Parse EDS request

# In[1]:


import cmocean
import numpy as np
import xarray as xr
import numpy.ma as ma
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4


# Load data using Xarray
file = 'test_data/Hycom_Global_20200713132800919_79065_52296.NC'
ds0 = xr.open_dataset(file)

######### This step is not necessary
#### Pandas just made it easier to explore the data
######################################################
# Convert to (tidy) dataframe
df = ds0.to_dataframe().reset_index()

# Convert columns to numpy arrays for clearer manipulation
ncells = df.ncells.to_numpy()
time = df.time.to_numpy()
lon = df.lon.to_numpy()
lat = df.lat.to_numpy()
U = df.U.to_numpy()
V = df.V.to_numpy()
######################################################
######### Can go straight from Xarray/netCDF to numpy

# Create arrays of unique values
ncells_u = np.unique(ncells)
time_u = np.unique(time)
lon_u = np.unique(lon)
lat_u = np.unique(lat)

# Reshape the arrays according to lengths of unique arrays
shape = (len(lat_u), len(lon_u), len(time_u))
lon = lon.reshape(shape)
lat = lat.reshape(shape)
time = time.reshape(shape)
U = U.reshape(shape)
V = V.reshape(shape)

# Remove redundant information
lon = lon[:,:,0]
lat = lat[:,:,0]
time = time[0,0,:]

# Create Dataset from reshaped arrays
ds = xr.Dataset(
    data_vars={
        'U': (['x', 'y', 'time'], ma.masked_equal(U, U.min())),
        'V': (['x', 'y', 'time'], ma.masked_equal(V, V.min()))
    },
    coords={
        'lon': (['x', 'y'], lon),
        'lat': (['x', 'y'], lat),
        'time': time
    },
    attrs=ds0.attrs
)

# Copy variable and coordinate attributes
for v in ds.data_vars:
    ds[v].attrs = ds0[v].attrs
for c in ds.coords:
    ds[c].attrs = ds0[c].attrs


# In[2]:


# Boundaries for plot
left = -99
right = -79
bottom = 20
top = 32


# ### Plot

# In[3]:


def plot(da, kind, **kwargs):
        
    print(f'**kwargs: {kwargs}')
    
    fig = plt.figure(figsize=(13, 10))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    
    if kind == 'mpl':
        cbar_kwargs = kwargs['cbar_kwargs']
        cbar_lims = np.max([abs(np.nanmin(ds.U.values)), abs(np.nanmax(ds.U.values))])
        im = ax.pcolormesh(da.lon, da.lat, da.isel(time=0), transform=ccrs.PlateCarree(), cmap=kwargs['cmap'], vmin=-cbar_lims, vmax=cbar_lims)
        fig.colorbar(im, ax=ax, **cbar_kwargs)
    if kind == 'xr':
        da.isel(time=0).plot.pcolormesh(ax=ax, x='lon', y='lat', transform=ccrs.PlateCarree(), **kwargs)

    ax.patch.set_facecolor('0.6')
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    ax.set_xlim(left=left, right=right)
    ax.set_ylim(bottom=bottom, top=top)
 
    plt.show()


# In[4]:


plot(ds.V, kind='mpl', cmap=cmocean.cm.speed, cbar_kwargs={'shrink': 0.6, 'pad': 0.1, 'extend': 'both'})
plot(ds.V, kind='xr', cmap=cmocean.cm.speed, cbar_kwargs={'shrink': 0.6, 'pad': 0.1, 'extend': 'both'})


# In[ ]:





# In[ ]:





# ### Use netCDF4 instead of Xarray

# In[5]:


from netCDF4 import Dataset
import numpy as np

ncds = Dataset(file)

lon = ncds.variables['lon'][:]
lat = ncds.variables['lat'][:]
time = ncds.variables['time'][:]
U = ncds.variables['U'][:]
V = ncds.variables['V'][:]


# In[ ]:





# ### Now try Parcels

# In[6]:


filenames = {'U': file, 'V': file}
variables = {'U': 'U', 'V': 'V'}


# In[7]:


# dimensions = {'time': 'time', 'lon': 'lon', 'lat': 'lon'}
# fset = FieldSet.from_netcdf(
#     filenames,
#     variables,
#     dimensions,
#     allow_time_extrapolation=True
# )


# In[8]:


ds


# In[9]:


dimensions = {'time': 'time', 'lon': 'x', 'lat': 'y'}
fset = FieldSet.from_xarray_dataset(
    ds,
    variables,
    dimensions,
    transpose=True
)


# In[10]:


pset = ParticleSet.from_list(
    fieldset=fset,
    pclass=JITParticle,
    lon=-87,
    lat=27
)


# In[11]:


runtime = timedelta(hours=ds.time.size)
endtime = ds.time[-1].values
print(runtime)
print(endtime)


# In[12]:


pset.execute(
    AdvectionRK4,
    dt=timedelta(hours=1),
    runtime=runtime,
    output_file=pset.ParticleFile(
        name='parcels_out.nc',
        outputdt=timedelta(hours=3)
    )
)   


# In[ ]:




