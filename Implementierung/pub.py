import paho.mqtt.client as mqtt
import time

#Methode um Daten zu senden
def sendData():
    topic = "/hshl/test" #Das Topic in dem gesendet werden soll
    payLoad = "Hello World" #Die Daten die gesendet werden sollen
    client.publish(topic, payLoad)

#Event, dass beim Verbindungsaufbau aufgerufen wird
def on_connect(client, userdata, flags, rc):
    sendData()#Aufruf der Senden Methode

#Dont change anything from here!!
BROKER_ADDRESS = "mr2mbqbl71a4vf.messaging.solace.cloud" #Adresse des MQTT Brokers
client = mqtt.Client()
client.on_connect = on_connect #Zuweisen des Connect Events
client.username_pw_set("solace-cloud-client", "nbsse0pkvpkvhpeh3ll5j7rpha") # Benutzernamen und Passwort zur Verbindung setzen
client.connect(BROKER_ADDRESS, port = 20614) #Verbindung zum Broker aufbauen

print("Connected to MQTT Broker: " + BROKER_ADDRESS)
client.loop_forever()#Endlosschleife um neue Nachrichten empfangen zu können