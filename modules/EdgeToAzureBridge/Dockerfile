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

LABEL description="Edge-to-Cloud Bridge for Microsoft Azure* service Image"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates build-essential \
                       git \
                       wget libcjson-dev libzmq3-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/* && \
    wget -qO- https://cmake.org/files/v3.15/cmake-3.15.0-Linux-x86_64.tar.gz | \
    tar --strip-components=1 -xz -C /usr/local
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/local/lib

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-distutils python3-dev python3-minimal python3-pip && \
    python3 -m pip install -U pip && \
    ln -sf /usr/bin/pip /usr/bin/pip3 && \
    pip3 install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH $PYTHONPATH:/usr/local/lib/python3.8/dist-packages

ARG EII_VERSION

RUN git clone https://github.com/open-edge-insights/eii-c-utils.git \
    --branch ${EII_VERSION} --single-branch 

RUN git clone https://github.com/open-edge-insights/eii-core.git \
    --branch ${EII_VERSION} --single-branch 

RUN git clone https://github.com/open-edge-insights/eii-messagebus.git \
    --branch ${EII_VERSION} --single-branch

RUN git clone https://github.com/open-edge-insights/eii-configmgr.git \
    --branch ${EII_VERSION} --single-branch

ARG CMAKE_INSTALL_PREFIX="/usr/local"

ARG EIIMessageBus="./eii-messagebus"
ARG ConfigMgr="./eii-configmgr"
ARG EIICutils="./eii-c-utils"

RUN cd ${ConfigMgr} && rm -rf deps
ARG INSTALL_PATH=${CMAKE_INSTALL_PREFIX}/lib

RUN cd ${EIIMessageBus} && rm -rf deps 

RUN cd ${EIICutils}/ && \
   rm -rf build && \
   mkdir build && \
   cd build && \
   cmake -DCMAKE_INSTALL_INCLUDEDIR=${CMAKE_INSTALL_PREFIX}/include -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} -DWITH_TESTS=${RUN_TESTS} -DCMAKE_BUILD_TYPE=$CMAKE_BUILD_TYPE .. && \
   make && \
   if [ "${RUN_TESTS}" = "ON" ] ; then cd ./tests  && \
   ./config-tests  \
   ./log-tests \
   ./thp-tests \
   ./tsp-tests \
   ./thexec-tests \
   cd .. ; fi  && \
   make install

RUN pip3 install --user -r ${EIIMessageBus}/python/requirements.txt

RUN cd ${EIIMessageBus} && \
    rm -rf build/ && \
    mkdir build/ && \
    cd build/ && \
    cmake  -DWITH_TESTS=${RUN_TESTS} -DWITH_TESTS=${RUN_TESTS} -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} .. && \
    make install

RUN cd ${EIIMessageBus}/python && python3 setup.py install --user

RUN apt update && apt install -y --no-install-recommends unzip
RUN cd ${ConfigMgr} && \
   # Installing grpc from DEB package
   cd grpc-package/ && \
   unzip grpc-1.29.0-Linux.zip -d / && \
   cd .. && \
   rm -rf build && \
   mkdir build && \
   cd build && \
   cmake  -DWITH_TESTS=${RUN_TESTS} -DCMAKE_BUILD_TYPE=$CMAKE_BUILD_TYPE .. && \
   make install

RUN cd ${ConfigMgr}/python && \
   python3 setup.py.in install --user

#Install libzmq
RUN rm -rf deps && \
    mkdir -p deps && \
    cd deps && \
    wget -q --show-progress https://github.com/zeromq/libzmq/releases/download/v4.3.4/zeromq-4.3.4.tar.gz -O zeromq.tar.gz && \
    tar xf zeromq.tar.gz && \
    cd zeromq-4.3.4 && \
    ./configure --prefix=${CMAKE_INSTALL_PREFIX} && \
    make install

# Install cjson
RUN rm -rf deps && \
    mkdir -p deps && \
    cd deps && \
    wget -q --show-progress https://github.com/DaveGamble/cJSON/archive/v1.7.12.tar.gz -O cjson.tar.gz && \
    tar xf cjson.tar.gz && \
    cd cJSON-1.7.12 && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_INCLUDEDIR=${CMAKE_INSTALL_PREFIX}/include -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} .. && \
    make install

COPY . .

RUN pip3 install --user -r requirements.txt

# Runtime image
FROM ubuntu:$UBUNTU_IMAGE_VERSION as runtime

WORKDIR /app
ARG EII_USER_NAME

RUN mkdir -p .local/lib

COPY --from=builder /app/eab/ /app/eab
COPY --from=builder /app/*.py /app/
COPY --from=builder /app/*.json /app/
COPY --from=builder /app/eii-core/common/util/*.py util/
COPY --from=builder /root/.local/lib .local/lib
COPY --from=builder /usr/local/lib/lib* /usr/local/lib/
COPY --from=builder /app/eii-core/common/ /app/common

ARG EII_UID

RUN useradd -r -u ${EII_UID} -G users,video,audio ${EII_USER_NAME}

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-distutils python3-minimal python3-setuptools && \
    rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/EII/:${CMAKE_INSTALL_PREFIX}/lib:/usr/local/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH $PYTHONPATH:/EII/:/app/.local/lib/python3.8/site-packages:/app/.local/lib/python3.8/dist-packages:/app/common/:/root/.local/lib/python3.8/site-packages/:${CMAKE_INSTALL_PREFIX}/lib

ARG EII_SOCKET_DIR
RUN mkdir -p /home/${EII_USER_NAME}/ && chown -R ${EII_USER_NAME}:${EII_USER_NAME} /home/${EII_USER_NAME} && \
    mkdir -p ${EII_SOCKET_DIR} && chown -R ${EII_USER_NAME}:${EII_USER_NAME} $EII_SOCKET_DIR 

RUN chown -R ${EII_USER_NAME}:${EII_USER_NAME} .local/
RUN chown ${EII_USER_NAME}:${EII_USER_NAME} /app /var/tmp
USER $EII_USER_NAME
ENTRYPOINT ["python3","-u","main.py"]
