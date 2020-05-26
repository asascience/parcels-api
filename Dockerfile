FROM centos:7.6.1810

LABEL maintainer="Brian.McKenna@rpsgroup.com"

RUN yum -y install epel-release          && \
    yum -y install hdf5-devel            && \
    yum clean all                        && \
    rm -rf /var/cache/yum

# build Python 3.7.4 and rollback yum requirements for build
RUN ROLLBACK=$(yum history | tail -n +4 | head -n 1 | sed 's/[ \t]*\([0-9]\{1,\}\).*/\1/') && \
    echo yum -y --setopt=tsflags=noscripts history rollback $ROLLBACK > rollback.sh

RUN yum -y install gcc m4 make    \
                   libcurl-devel  \
                   libffi-devel   \
                   openssl-devel  \
                   bzip2-devel    \
                   readline-devel \
                   sqlite-devel   \
                   gdbm-devel     \
                   xz-devel       \
                   ncurses-devel  \
                   libuuid-devel                                                          && \
    curl -O -L "https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz"                 && \
    tar xzf Python-3.7.4.tgz                                                              && \
    cd Python-3.7.4                                                                       && \
    ./configure                                                                           && \
    make                                                                                  && \
    make install                                                                          && \
    cd ..                                                                                 && \
    rm -rf Python-3.7.4*                                                                  && \
    curl -O -L "https://github.com/Unidata/netcdf-c/archive/v4.7.1.tar.gz"                && \
    tar xzf v4.7.1.tar.gz                                                                 && \
    cd netcdf-c-4.7.1                                                                     && \
    ./configure                                                                           && \
    make                                                                                  && \
    make install                                                                          && \
    cd ..                                                                                 && \
    rm -rf netcdf-c-4.7.1 v4.7.1.tar.gz                                                   && \
    sh /rollback.sh                                                                       && \
    rm -f rollback.sh                                                                     && \
    yum clean all                                                                         && \
    rm -rf /var/cache/yum


# parcels-api
COPY requirements.txt /requirements.txt
RUN yum -y install gcc m4 git

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

COPY md3/HYCOM* /data/

CMD python3.7 server.py
