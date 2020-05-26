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
