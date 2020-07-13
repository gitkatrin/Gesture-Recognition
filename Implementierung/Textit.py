import paho.mqtt.client as mqtt
import time
import random
import string
import json
# Methode um Daten zu senden


def sendData():

    ###########################CREATE USER#######################################
    topic = "/hshl/users/"  # Das Topic in dem gesendet werden soll
    # Die Daten die gesendet werden sollen
    call = {
        "driver_name": "Herrmann",
        "location": [51.3, 23.22],  # Array mit Koordinaten
        "reasons": "None",  # Array mit reasons
        "id": "car1"
    }
    client.publish(topic, json.dumps(call))
    print("sendet")

###########################CREATE FIREFIGHTER#######################################
    topic = "/hshl/firefighters/"  # Das Topic in dem gesendet werden soll
    # Die Daten die gesendet werden sollen
    call = {
        "driver_name": "KatjaBurkard",
        "location": [52.3, 26.22],  # Array mit Koordinaten
        "isFree": True,  # als bool
        "id": "fire1"
    }
    client.publish(topic, json.dumps(call))
    print("sendet")

###########################CREATE POLICE#######################################
    topic = "/hshl/polices/"  # Das Topic in dem gesendet werden soll
    # Die Daten die gesendet werden sollen
    call = {
        "driver_name": "Klaus",
        "location": [13.3, 33.22],  # Array mit Koordinaten
        "isFree": True,  # als bool
        "id": "pol1"
    }
    client.publish(topic, json.dumps(call))
    print("sendet")

###########################CREATE AMBULANCE#######################################
    topic = "/hshl/ambulances/"  # Das Topic in dem gesendet werden soll
    # Die Daten die gesendet werden sollen
    call = {
        "driver_name": "Annegret",
        "location": [33.3, 3.22],  # Array mit Koordinaten
        "isFree": True,  # als bool
        "id": "amb1"
    }
    client.publish(topic, json.dumps(call))
    print("sendet")

###########################CREATE HOSPITAL#######################################
    topic = "/hshl/hospitals/"  # Das Topic in dem gesendet werden soll
    # Die Daten die gesendet werden sollen
    call = {
        "hospital_name": "Hospitalomat",
        "location": [43.3, 23.22],  # Array mit Koordinaten
        "doctors": 12,
        "id": "hosp1",
        "freeRooms": 123,
        "specialists": ["specialist1", "specialist2"]
    }
    client.publish(topic, json.dumps(call))
    print("sendet")

    ###########################UPDATE USER#######################################
    topic = "/hshl/users/car1"  # Das Topic in dem gesendet werden soll
    # Die Daten die gesendet werden sollen
    call = {
        "driver_name": "Herrmann",
        "location": [51.3, 23.22],  # Array mit Koordinaten
        "reasons": "accident",  # Array mit reasons
        "id": "car1"
    }
    client.publish(topic, json.dumps(call))
    print("sendet")


def on_connect(client, userdata, flags, rc):
    sendData()  # Aufruf der Senden Methode


# Dont change anything from here!!
BROKER_ADDRESS = "mr2mbqbl71a4vf.messaging.solace.cloud"  # Adresse des MQTT Brokers
client = mqtt.Client()

client.on_connect = on_connect  # Zuweisen des Connect Events
# Benutzernamen und Passwort zur Verbindung setzen
client.username_pw_set("solace-cloud-client", "nbsse0pkvpkvhpeh3ll5j7rpha")
client.connect(BROKER_ADDRESS, port=20614)  # Verbindung zum Broker aufbauen

print("Connected to MQTT Broker: " + BROKER_ADDRESS)
client.loop_forever()  # Endlosschleife um neue Nachrichten empfangen zu können