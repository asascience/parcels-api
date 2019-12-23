FROM base

LABEL maintainer="Brian.McKenna@rpsgroup.com"

# parcels-api
COPY requirements.txt /requirements.txt
RUN yum -y install gcc m4

RUN pip3.7 install pip --upgrade       && \
    pip3.7 install -r requirements.txt && \
    rm -f requirements.txt

ENV PARCELS_PATH /srv/parcels
RUN mkdir -p "$PARCELS_PATH"
COPY server.py /srv/parcels
COPY util.py /srv/parcels
WORKDIR /srv/parcels

# forcing data mount
VOLUME /data

EXPOSE 5000

CMD python3.7 server.py

