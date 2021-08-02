# parcels-api
### Run with venv
```
python3 -m venv parcels-env
source parcels-env/bin/activate
pip install -r requirements.txt
python server.py
```
### Run with docker
```
docker build -t base .
docker run --publish 5000:5000 -it --rm base /bin/bash
```
Then inside the container run
```
python3 server.py
```
If that all works you should be able to enter this url (for example) and get the json response you saw before
```
http://0.0.0.0:5000/trajectory?lat=28.7&lon=-88.3&t0=0
```
http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=0


docker build -t eds-base .
docker run --publish 5000:5000 -it --rm eds-base /bin/bash

http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=2021-01-12

http://localhost:5000/trajectory?lat=26.53729&lon=-90.37788&t0=2021-01-10

http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=2021-01-12&dataset=HYCOM%20GLOBAL%20NAVY
http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=2021-01-12&dataset=COPERNICUS%20GLOBAL