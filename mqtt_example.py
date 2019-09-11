import time

import paho.mqtt.client as mqtt #import the client1
broker_address="localhost"
def on_message(client, userdata, message):
    print ("message receivedL ", str(message.payload.decode("utf-8")))


#broker_address="iot.eclipse.org"

print("creating new instance")
client = mqtt.Client("P1") #create new instance
client2 = mqtt.Client("P2") #create new instance
client.on_message = on_message
client2.on_message = on_message
print("connecting to broker")
client.connect(broker_address, port=2000) #connect to broker
client2.connect(broker_address, port=2000) #connect to broker
print("Subscribing to topic","house/bulbs/bulb1")
# client.subscribe("house/bulbs/bulb1")
client2.subscribe("house/bulbs/bulb1")
client.loop_start()
client2.loop_start()
print("Publishing message to topic","house/bulbs/bulb1")
client.publish("house/bulbs/bulb1","OFF")
# client.loop_read()


time.sleep(200)
client.loop_stop()

