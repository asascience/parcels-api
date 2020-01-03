# parcels-api
To run this in a local python virtual environment run these commands
```
python -m virtualenv parcels-env
source parcels-env/bin/activate
pip install -r requirements.txt
python server.py
```
If that all works you should be able to enter this url (for example) and get the json response you saw before
```
http://0.0.0.0:5000/trajectory?lat=28.7&lon=-88.3&t0=0
```
The goal is to do this in a docker container rather than a virtual environment. Build and run the container with these commands.
```
docker build -t base .
docker run -it --rm base /bin/bash
```
Then inside the container run 
```
python server.py
```
