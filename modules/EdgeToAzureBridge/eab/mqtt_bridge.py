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
import uuid
import os
import json
import jsonschema
import threading
import asyncio
from queue import Queue
from time import sleep
from util.log import configure_logging
import paho.mqtt.client as mqtt
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubModuleClient


class AzureConnection:
    def __init__(self, logger) -> None:
        """Initialize the Azure Connection

        :param logger: logger Object needed for logging
        :type logger: Object
        :raises ex: exception if the Azure Connection cannot be established
        """
        self.log = logger
        self.device_client = self.connect_azure()
        try:
            asyncio.run(self.device_client.connect())
        except Exception as ex:
            self.log.error(f"Exception: {ex}")
            raise ex

    def connect_azure(self):
        """Connect to Azure IoT Hub

        :raises ex: exception if the Azure Connection cannot be established
        :return: Azure connection object
        :rtype: Object
        """
        try:
            device_client = IoTHubModuleClient.create_from_edge_environment()
            self.log.info("Connected to Azure IOT via Edge Environment")
            return device_client

        except Exception as ex:
            self.log.error("Cannot Connect to Azure IOT Hub.{}".format(ex))
            raise ex

    async def send_data(self, data):
        """send data to Azure IoT Hub

        :param data: data to be Azure IoT Hub
        :type data: Object
        """
        msg = Message(str(data))
        msg.message_id = uuid.uuid4()
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        await self.device_client.send_message(msg)


class MQTTConnect(mqtt.Client):
    def __init__(self):
        """"
        Constructor to initialize the MQTT Connection.
        Initialize a parallel thread to send data to Azure IoT Hub
        """
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_connect_fail = self.on_connect_fail
        self.log = configure_logging("INFO", __name__, False)
        self.azure_connection = AzureConnection(self.log)
        self.brokerIP = self.get_config()[1]
        self.brokerPort = self.get_config()[2]
        self.topics = self.get_config()[0]
        self.q_data = Queue()
        self.schema = self.get_schema()
        self.sub = threading.Thread(target=self.azure_entrypoint)
        self.log.info(
            "MQTT Broker Details : {}:{} ".format(
                self.brokerIP, self.brokerPort)
        )

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when the client gets a connection response from the server.
        On Connect, subscribe to all the topics.
        """
        self.log.info(
            "Subscribing to MQTT Broker : {}:{} ".format(
                self.brokerIP, self.brokerPort)
        )
        for topic in self.topics:
            self.log.info("Subscribing to topic : {}".format(topic))
            self.client.subscribe(topic)
        if rc == 0:
            self.log.info(
                "Subscribed to MQTT Broker : {}:{} ".format(
                    self.brokerIP, self.brokerPort
                )
            )
        else:
            self.log.info(
                "Not able to subscribe to MQTT Broker : {}:{} ".format(
                    self.brokerIP, self.brokerPort
                )
            )

    def on_connect_fail(self, mqttc, obj):
        """
        Callback for when the client fails to connect to the server.
        """
        self.log.error(
            "Connection to MQTT Broker {}:{} failed {}:{}".format(
                self.brokerIP, self.brokerPort
            )
        )

    def on_message(self, mqttc, obj, msg):
        """
        Callback for when a message is received from the server.
        """
        self.log.info("MQTT Message received")
        self.q_data.put_nowait(msg)

    def get_schema(self):
        """
        Get the schema for the data to be sent to Azure IoT Hub

        :return: Schema for the data to be sent to Azure IoT Hub
        :rtype: Object
        """
        self.log.info("Loading Schema")
        with open("/app/schema.json", "r") as file:
            schema = json.load(file)
        return schema

    def get_config(self):
        """
        Get the config for connecting to MQTT Broker

        :return: MQTT Topics, Broker IP and Port
        :rtype: Object
        """
        self.log.info("Loading Schema")
        try:
            with open("/app/mosquitto.json", "r") as file:
                schema = json.load(file)
            return schema["topics"], schema["BrokerHost"], schema["BrokerPort"]
        except Exception as ex:
            raise ex

    def azure_entrypoint(self):
        """
        Gets the data in the queue from the MQTT Broker,
        and send it to the Azure IoT Hub
        """
        while True:
            if not self.q_data.empty():
                try:
                    result = self.q_data.get_nowait()
                    data = json.loads(result.payload)
                    # Sending only the valid schema to the Azure IoT Hub
                    jsonschema.validate(instance=data, schema=self.schema)
                    data["topic"] = result.topic
                    asyncio.run(self.azure_connection.send_data(data))
                except BaseException as err:
                    self.log.error(
                        "Exception in the Payload. : {}".format(err))
                    pass
            else:
                sleep(0.001)

    def stop(self):
        """
        Stop the MQTT Connection and the Azure Connection
        """
        self.log.info("Ending Connection".format(
            self.brokerIP, self.brokerPort))
        self.client.loop_stop()
        self.client.disconnect()
        self.log.debug("Disconnecting from Azure IoT Hub client")
        asyncio.run(self.azure_connection.device_client.disconnect())

    def start(self):
        """
        Start the MQTT Connection and the Azure Connection
        """
        self.log.info("Setting up connection".format(
            self.brokerIP, self.brokerPort))
        self.client.connect(self.brokerIP, int(self.brokerPort), 60)
        self.sub.start()
        self.client.loop_forever()
