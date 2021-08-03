# parcels-api

Full documentation can be found at: https://rpsgroup-my.sharepoint.com/:o:/p/kelsey_ruckert/EjUZ-DUqEllMgc9oNc-ihKQBBOyvDuXtsl0Ll4_WR6Usmw?e=wJUjlJ

### Run with venv
```
python3 -m venv parcels-env
source parcels-env/bin/activate
pip install -r requirements.txt
python server.py
```
### Run with docker
```
docker build -t eds-base-2 .
docker run --publish 5000:5000 -it --rm eds-base-2 /bin/bash
```
Then inside the container run
```
python3 server.py
```
If that all works you should be able to enter this url (for example) and get the json response you saw before
```
http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=2021-07-13&dataset=HYCOM%20GLOBAL%20NAVY
http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=2021-07-13&dataset=COPERNICUS%20GLOBAL
http://localhost:5000/trajectory?lat=28.7&lon=-88.3&t0=2021-07-14&dataset=HYCOM%20GOM
```
## To remove a docker image:
```
docker rmi eds-base-2:latest
```
To list docker images:
```
docker image ls
```