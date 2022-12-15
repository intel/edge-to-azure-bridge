# Contents

- [Contents](#contents)
  - [Edge to Azure Bridge Module Overview](#edge-to-azure-bridge-module-overview)
  - [Running Unit Tests](#running-unit-tests)

## Edge to Azure Bridge Module Overview

This directory contains the source code for the Edge to Azure Bridge OEI service which bridges communication from the Message bus and the Azure IoT Edge Runtime. For more information on this service, refer to the [README_EII.md](../../README_EII.md). The purpose of this README is to cover some specifics related to the code itself, and not the usage of the module in OEI. Refer to the OEI and Azure Bridge READMEs for more information.

## Running Unit Tests

The Edge to Azure Bridge contains unit tests for various utility functions in the service. It does not contain unit tests for every single method, because most of it is not unit testable, meaning, you must have a fully operational Azure IoT Edge Runtime to run the code successfully. Testing the bridge in this way can be accomplished via using the Azure IoT Edge Runtime simulator documented in the root directory of the Azure Bridge service.

To run the unit tests for the Edge to Azure Bridge, install the Edge to Azure Bridge python dependencies:

>**Note:** It is highly recommended that you use a python virtual environment to install the python packages, so that the system python installation is not altered. For more information on setting up and using python virtual environment, refer to [Python Virtual environment.](https://www.geeksforgeeks.org/python-virtual-environment/)

 ```sh
 sudo -H -E pip3 install -r requirements.txt
 ```

1. Set up your `PYTHONPATH` to contian the necessary EII Python libraries for the test:

> **NOTE:** This can be skipped if you have installed the EII libraries on your system already. This step assumes none of the EII libraries for Python, Go, or C have been installed on your system.

```sh
export PYTHONPATH=${PYTHONPATH}:../../../common:../../../common/libs/ConfigManager/python
```

2. Run the unit tests with the following Python command:

```sh
python3 -m unittest discover
```

If successful, the following output is displayed:

```sh
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```
