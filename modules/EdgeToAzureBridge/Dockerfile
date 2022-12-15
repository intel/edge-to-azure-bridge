# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: MIT

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

ARG EII_VERSION
ARG EII_UID
ARG EII_USER_NAME
ARG UBUNTU_IMAGE_VERSION
FROM ubuntu:$UBUNTU_IMAGE_VERSION as builder
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

LABEL description="Edge-to-Cloud Bridge for Microsoft Azure* service Image"

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                       build-essential=12.8ubuntu1.1 \
                       git=1:2.25.1-1ubuntu3.6 \
                       wget=1.20.3-1ubuntu2 \
                       pkg-config=0.29.1-0ubuntu4 \
                       software-properties-common=0.99.9.8 && \
    rm -rf /var/lib/apt/lists/* && \
    wget -qO- https://cmake.org/files/v3.15/cmake-3.15.0-Linux-x86_64.tar.gz | \
    tar --strip-components=1 -xz -C /usr/local
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/local/lib

ARG CMAKE_INSTALL_PREFIX
# Install libzmq
RUN rm -rf deps && \
    mkdir -p deps
WORKDIR /app/deps
RUN wget -q --show-progress https://github.com/zeromq/libzmq/releases/download/v4.3.4/zeromq-4.3.4.tar.gz -O zeromq.tar.gz && \
    tar xf zeromq.tar.gz
WORKDIR /app/deps/zeromq-4.3.4
RUN ./configure --prefix=${CMAKE_INSTALL_PREFIX} && \
    make install

# Install cjson
WORKDIR /app
RUN rm -rf deps && \
    mkdir -p deps
WORKDIR /app/deps
RUN wget -q --show-progress https://github.com/DaveGamble/cJSON/archive/v1.7.12.tar.gz -O cjson.tar.gz && \
    tar xf cjson.tar.gz
WORKDIR /app/deps/cJSON-1.7.12
RUN mkdir build
WORKDIR /app/deps/cJSON-1.7.12/build 
RUN cmake -DCMAKE_INSTALL_INCLUDEDIR=${CMAKE_INSTALL_PREFIX}/include -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} .. && \
    make install
WORKDIR /app
ARG EII_VERSION
RUN git clone https://github.com/open-edge-insights/eii-core.git \
    --branch master --single-branch

FROM ubuntu:$UBUNTU_IMAGE_VERSION AS runtime

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                       build-essential=12.8ubuntu1.1 \
                       git=1:2.25.1-1ubuntu3.6 \
                       wget=1.20.3-1ubuntu2 \
                       pkg-config=0.29.1-0ubuntu4 \
                       zlib1g=1:1.2.11.dfsg-2ubuntu1.5 \
                       xz-utils=5.2.4-1ubuntu1.1 \
                       util-linux=2.34-0.1ubuntu9.3 \
                       sqlite3=3.31.1-4ubuntu0.5 \
                       perl=5.30.0-9ubuntu0.3 \
                       openssl=1.1.1f-1ubuntu2.16 \
                       gzip=1.10-0ubuntu4.1 \
                       libgnutls28-dev=3.6.13-2ubuntu1.7 \
                       gnupg2=2.2.19-3ubuntu2.2 \
                       libc-bin=2.31-0ubuntu9.9 \
                       e2fsprogs=1.45.5-2ubuntu1.1 \
                       tar=1.30+dfsg-7ubuntu0.20.04.2 \
                       libpcre2-dev=10.34-7ubuntu0.1 \
                       bash=5.0-6ubuntu1.2 \
                       libsepol1=3.0-1ubuntu0.1 \
                       libgmp10=2:6.2.0+dfsg-4ubuntu0.1 \
                       dpkg=1.19.7ubuntu3.2 \
                       systemd=245.4-4ubuntu3.19 \                       
                       software-properties-common=0.99.9.8 && \
    rm -rf /var/lib/apt/lists/* && \
    wget -qO- https://cmake.org/files/v3.15/cmake-3.15.0-Linux-x86_64.tar.gz | \
    tar --strip-components=1 -xz -C /usr/local

# Setting python dev env
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    python3-distutils=3.8.10-0ubuntu1~20.04 \
                    python3-minimal=3.8.2-0ubuntu2 \
                    python3-pip=20.0.2-5ubuntu1.6 \
                    wget=1.20.3-1ubuntu2 && \
    rm -rf /var/lib/apt/lists/*

ARG CMAKE_INSTALL_PREFIX
ENV CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} \
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/EII/:${CMAKE_INSTALL_PREFIX}/lib:/usr/local/lib:$LD_LIBRARY_PATH \
    PYTHONPATH=$PYTHONPATH:/EII/:/app/.local/lib/python3.8/site-packages:/app/.local/lib/python3.8/dist-packages:/app/common/:/root/.local/lib/python3.8/site-packages/:${CMAKE_INSTALL_PREFIX}/lib

WORKDIR /app
ARG PKG_SRC
ARG EII_VERSION
COPY eii-utils-4.0.0-Linux.deb ./
COPY eii-messagebus-4.0.0-Linux.deb ./
COPY eii-configmanager-4.0.0-Linux.deb ./
RUN dpkg -i eii-utils-4.0.0-Linux.deb
RUN dpkg -i eii-messagebus-4.0.0-Linux.deb
RUN dpkg -i eii-configmanager-4.0.0-Linux.deb
RUN rm -rf eii-*.deb

# Installation of eiimessagebus and configmgr whl packages
ARG PYPI_SRC
ARG CFGMGR_WHL
ARG MSGBUS_WHL
COPY requirements.txt ./
COPY eii_configmgr-4.0.0-cp38-cp38-manylinux2014_x86_64.whl ./
COPY eii_msgbus-4.0.0-cp38-cp38-manylinux2014_x86_64.whl ./

RUN pip3 install --no-cache-dir -r requirements.txt
run pip3 install --no-cache-dir eii_configmgr-4.0.0-cp38-cp38-manylinux2014_x86_64.whl
RUN pip3 install --no-cache-dir eii_msgbus-4.0.0-cp38-cp38-manylinux2014_x86_64.whl

RUN apt-get remove --auto-remove --purge -y python3-pip wget

COPY --from=builder ${CMAKE_INSTALL_PREFIX}/lib ${CMAKE_INSTALL_PREFIX}/lib
COPY --from=builder /app/eii-core/common/util/*.py util/

ARG EII_SOCKET_DIR
ARG EII_USER_NAME
ARG EII_UID
RUN groupadd $EII_USER_NAME -g $EII_UID && \
    useradd -l -r -u $EII_UID -g $EII_USER_NAME $EII_USER_NAME

RUN mkdir -p /home/${EII_USER_NAME}/ && chown -R ${EII_USER_NAME}:${EII_USER_NAME} /home/${EII_USER_NAME} && \
    mkdir -p ${EII_SOCKET_DIR} && chown -R ${EII_USER_NAME}:${EII_USER_NAME} $EII_SOCKET_DIR 

RUN chown ${EII_USER_NAME}:${EII_USER_NAME} /app /var/tmp
USER $EII_USER_NAME
COPY . .
HEALTHCHECK --interval=1h CMD python3 --version || exit 1
ENTRYPOINT ["python3","-u","main.py"]
