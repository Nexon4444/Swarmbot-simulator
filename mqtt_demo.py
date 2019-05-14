import paho.mqtt.client as mqtt #import the client1
import time
############
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_connect():
    print ("connected")

broker_address="192.168.0.110"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
client.on_connect=on_connect()
print("connecting to broker")
client.connect(broker_address, port=2000) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","house/bulbs/bulb1")
client.subscribe("house/bulbs/bulb1")
# print("Publishing message to topic","house/bulbs/bulb1")
# client.publish("house/bulbs/bulb1","OFF")
client.loop_start() #stop the loop
time.sleep(200) # wait
