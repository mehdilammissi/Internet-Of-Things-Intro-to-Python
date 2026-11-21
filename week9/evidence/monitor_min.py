# monitor_min.py: print every light reading as it arrives
import paho.mqtt.client as mqtt
BROKER = "localhost"              # the broker is this very Pi
TOPIC  = "bench/s07/light"
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected:", reason_code)
    client.subscribe(TOPIC)       # subscribe HERE, not outside: see below
def on_message(client, userdata, msg):
    pct = float(msg.payload.decode())
    print(f"{msg.topic}: {pct:.1f} %")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883)
client.loop_forever()