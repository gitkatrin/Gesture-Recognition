import paho.mqtt.client as mqtt
import json

my_id = "katrin"

def on_connect(client, userdata, flags, rc):
    client.subscribe([                    
                    ("hshl/company/"+my_id, 2),
                    ])

def on_message(client, userdata, msg):
    print(str(msg.payload))
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)

data = {
    "name": "Frau Katrin Glöwing", 
    "reasons" :["..."], 
    "topic": "hshl/company/"+my_id
    }
client.publish("hshl/police", json.dumps(data))

#client.loop_forever()
client.loop_start()