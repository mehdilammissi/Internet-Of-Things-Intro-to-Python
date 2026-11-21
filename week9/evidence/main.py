# main logic: publish the calibrated light level once a second
from umqtt.simple import MQTTClient
from time import sleep
import config
from lightnode import LightNode          # your Week 8 class, unchanged
TOPIC = f"bench/{config.STATION}/light".encode()
node   = LightNode(adc_pin=34, pwm_pin=25, dark=200, bright=3550)
client = MQTTClient(f"node-{config.STATION}", config.BROKER_IP)
client.connect()
print("MQTT connected to", config.BROKER_IP)
while True:
    pct = node.read_pct()
    client.publish(TOPIC, f"{pct:.1f}".encode())
    sleep(1)