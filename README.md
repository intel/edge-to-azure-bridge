## Contents

- [Contents](#contents)
  - [Edge-to-Cloud Bridge for Microsoft Azure* Introduction](#Edge-to-Cloud-Bridge-for-Microsoft-Azure-*-introduction)
    - [Prerequisites](#prerequisites)
  - [Building the Image](#building-the-image)
  - [Running in EII Mode](#running-in-EII-mode)
  - [Running the microservice](#running-the-microservice)
    - [Tutorial 1 - Sending Data using Edge-to-Cloud Bridge for Microsoft Azure* service](#tutorial-1---sending-data-using-edge-to-cloud-bridge-for-microsoft-azure-service)
    - [Tutorial 2 - Changing Topics and Message Schema for Edge-to-Cloud Bridge for Microsoft Azure* service](#tutorial-2---changing-topics-and-message-schema-for-edge-to-cloud-bridge-for-microsoft-azure-service)
    - [Tutorial 3 - Sending the Data from Edge Video Analytics Microservice to Azure IOT Hub using Edge-to-Cloud Bridge for Microsoft Azure* Service.](#tutorial-3---sending-the-data-from-edge-video-analytics-microservice-to-azure-iot-hub-using-edge-to-cloud-bridge-for-microsoft-azure-service)
   

## Edge-to-Cloud Bridge for Microsoft Azure* Introduction

Edge-to-Cloud Bridge for Microsoft Azure* service connects to publishers (MQTT Broker, EII Message Bus) and sends data to Azure IOT Hub. This repository contains the source code for Edge-to-Cloud Bridge for Microsoft Azure* service. For information on how to build the use case, refer to the [Get Started guide](https://www.intel.com/content/www/us/en/developer/articles/technical/edge-to-cloud-bridge-for-microsoft-azure-service.html).

> NOTE: Currently, the microservice works in an open network only.

### Prerequisites

- MQTT Port 1883, 8080, 8554  is not used. (for non-EII runtime)
- Azure IoT Edge Runtime
- Azure CLI

## Building the Image

- To build the base image, run the following command
     `docker-compose -f docker-compose-build.yml build edge_to_azure_bridge`

- You can download the prebuilt container image for Edge-to-Cloud Bridge for Microsoft Azure* service from [Docker Hub](https://hub.docker.com/r/intel/edge_to_azure_bridge)

## Running in EII Mode

> **NOTE**:
> 1. The independent build of the EdgeToAzureBridge service can be done as per above [section](#building-the-image)
> 2. As EdgeToAzureBridge service is being deployed as Azure IoT modules along with other EII modules as a use case solution, independent deployment of EdgeToAzureBridge service with or without Config Manager Agent service dependency is not been enabled.

- Refer to [README](README_EII.md) for using Edge-to-Cloud Bridge for Microsoft Azure* service in EII mode with other EII supported modules.

## Running the Microservice

The Edge-to-Cloud Bridge for Microsoft Azure* service runs as an Azure Module. You need to set up your development system for using the microservice with Azure IOT runtime.

Development system Setup :

- [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt#option-1-install-with-one-command)
- [Install Azure IOT Runtime](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu)
- [Create Azure IoT Hub](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-create-through-portal)
- [Register an Azure IoT Device](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device)

### Tutorial 1 - Sending Data using Edge-to-Cloud Bridge for Microsoft Azure* Service

The microservice connects to the MQTT broker and listens to the messages incoming to the topics defined in the configuration file (mosquitto.json). Once the microservice receives the data on these topics, it validates the message with a schema (schema.json) and sends the data to Azure IOT Hub.

The default schema is defined below.

```json
{
    "properties": {
      "objects": {
        "description": "The unique identifier for a inference metadata.",
        "type": "array"
      }
    },
    "required": [ "objects" ]
  }
```

The message published to the broker in the given JSON schema will be upstreamed to the Azure IoT Hub.

- The MQTT publisher can publish the payload to the Broker as per the schema in the JSON format below:
  
```json
  {
    "objects":["Payload1", "Payload2"]
  }
```

Follow the steps to setup the service :-

- Update the Deployment manifest file (config/deployment.template.json) with the absolute path to the config files.

```js
<snip>

[\"EDGE_TO_AZURE_BRIDGE_RESOURCES/mosquitto/:/mosquitto/config\"]

<snip>
```

- The below command will replace the placeholder tag in the configuration with the absolute path to the Resources folder.

```js
sed -i "s^EDGE_TO_AZURE_BRIDGE_RESOURCES^$PWD^g" config/deployment.template.json
```

1. Deploy the manifest file using the command below

```sh
az iot edge set-modules -n <azure-iot-hub-name> -d <azure-iot-edge-device-name> -k config/deployment.template.json
```

2. Check the deployment status using

```sh
sudo iotedge list
```

- Test will send a message to the service.

- The MQTT publisher can publish the payload to the Broker as per the schema in the JSON format below:
  
```json
  {
    "objects":["Payload1", "Payload2"]
  }
```

- There are multiple ways to publish data to the Broker :

  - You can use any OpenSource MQTT Client to publish data to the Broker (example [MQTTExplorer](http://mqtt-explorer.com/))

  - From your code, using any MQTT client SDK example : [Python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php) , [JavaScript](https://www.eclipse.org/paho/index.php?page=clients/js/index.php)


- Monitor Azure IOT Hub Data

```sh
az iot hub monitor-events --output table --device-id <Device ID> --hub-name <IoT HUB name>
```

### Tutorial 2 - Changing Topics and Message Schema for Edge-to-Cloud Bridge for Microsoft Azure* Service

- For changing the topics to which your application publishes the messages, update the mosquitto.json file with the list of topics.

- For example, lets assume the application publishes to camera1 topic, we can update the configuration file as below:

```json
{
    "topics": ["camera1"],
    "BrokerHost": "MQTTBroker",
    "BrokerPort": 1883
}
```

- For changing the message schema, update the schema.json file

- For example, lets assume the application publishes location and people count to the topic as below:-

```json
{
  
  "location": "SB_2_1",
  "people_count": 3

}
```

- We can update the schema to validate the messages coming to the service.

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "properties": {
      "location": {
        "description": "Location of the camera",
        "type": "string"
      },
      "people_count": {
        "description": "No of people",
        "type": "integer"
      }
    },
    "required": [ "location", "people_count"]
  }
```

- To learn more about defining the schemaFollow, use this [link](https://json-schema.org/learn/getting-started-step-by-step.html) 

1. To update the service with these changes restart the service.

```sh
sudo iotedge restart EdgeToAzureBridge
```

2. Send the message with the above schema and to the defined topic to verify.

### Tutorial 3 - Sending the Data from Edge Video Analytics Microservice to Azure IOT Hub using Edge-to-Cloud Bridge for Microsoft Azure* Service

1. Install the [Video Analytics Use Case](https://www.intel.com/content/www/us/en/developer/articles/technical/video-analytics-service.html). For information on how to build the use case, please refer to the [Get Started](https://www.intel.com/content/www/us/en/developer/articles/technical/video-analytics-service.html#inpage-nav-3) guide.

2. Download the required models as documented [here](https://www.intel.com/content/www/us/en/developer/articles/technical/video-analytics-service.html#inpage-nav-3-1)
  
3. Once the models are downloaded, update the Deployment manifest file (config/deployment_evam.template.json) with the location of the Edge Video Analytics Resources folder.

```sh
<snip>

[\"EVAM_RESOURCES/models:/app/models\",\"EVAM_RESOURCES/pipelines:/app/pipelines\

<snip>
```
4. Run the below command

```sh
sed -i "s^EVAM_RESOURCES^<Path to EVAM Resources>^g" config/deployment_evam.template.json
```

- Example:

```sh
sed -i "s^EVAM_RESOURCES^/home/intel/public/video_analytics/Video_Analytics_2021.4.2/Edge_Video_Analytics_Resources^g" config/deployment_evam.template.json
```
5. From the Edge to Azure Resources folder, update the deployment template with the absolute path to the configuration files

```sh
<snip>

{\"Binds\":[\"EDGE_TO_AZURE_BRIDGE_RESOURCES/mosquitto.json:/app/mosquitto.json\"

<snip>
```

6. Run the below command

```sh
sed -i "s^EDGE_TO_AZURE_BRIDGE_RESOURCES^$PWD^g" config/deployment_evam.template.json
```

7. Deploy the manifest file using the command below

```sh

az iot edge set-modules -n <azure-iot-hub-name> -d <azure-iot-edge-device-name> -k config/deployment_evam.template.json
```

8. Check the deployment status using

```sh
sudo iotedge list
```

9. Start a new pipeline and monitor Azure IoT Hub data. (Update the SYSTEM_IP_ADDRESS below, before running the pipeline)

```sh
curl --location --request POST 'http://localhost:8080/pipelines/object_detection/person_vehicle_bike' --header 'Content-Type: application/json' --data-raw '{
  "source": {
      "uri": "https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4?raw=true",
      "type": "uri"
  },
  "destination": {
      "metadata": {
        "type": "mqtt",
        "host": "<SYSTEM_IP_ADDRESS>:1883",
        "topic": "vaserving"
      }
  }
}
'
```
10.  Monitor Azure IOT Hub Data

```sh
az iot hub monitor-events --output table --device-id <Device ID> --hub-name <IoT HUB name>
```

>To learn more about Azure IoT Hub visit this [link.](https://azure.microsoft.com/en-in/services/iot-hub/)


# Licensing Info
The code in this repository is MIT-licensed. More information can be found in the license file. This project uses Intel EII libraries during building, which are not MIT-licensed. See those libraries' details for information on their licensing and conditions.