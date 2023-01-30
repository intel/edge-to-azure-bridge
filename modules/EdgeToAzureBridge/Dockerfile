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
                       build-essential \
                       git \
                       wget \
                       pkg-config \
                       software-properties-common && \
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
#RUN git clone https://github.com/open-edge-insights/eii-core.git --branch master --single-branch

FROM ubuntu:$UBUNTU_IMAGE_VERSION AS runtime

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                       build-essential \
                       git \
                       wget \
                       pkg-config \
                       zlib1g \
                       xz-utils \
                       util-linux \
                       sqlite3 \
                       perl \
                       openssl \
                       gzip\
                       libgnutls28-dev\
                       gnupg2 \
                       libc-bin \
                       e2fsprogs \
                       tar \
                       libpcre2-dev \
                       bash \
                       libsepol1 \
                       libgmp10 \
                       dpkg \
                       systemd \                       
                       software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    wget -qO- https://cmake.org/files/v3.15/cmake-3.15.0-Linux-x86_64.tar.gz | \
    tar --strip-components=1 -xz -C /usr/local

# Setting python dev env
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    python3-distutils \
                    python3-minimal \
                    python3-pip \
                    wget && \
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
#COPY --from=builder /app/eii-core/common/util/*.py util/

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
