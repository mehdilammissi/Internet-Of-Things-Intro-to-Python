# sim_node.py: a stand-in for the light node. It runs on the Pi.
# It speaks the same MQTT topics as a real node:
#   publishes  bench/<station>/light    one reading per second, in %
#   publishes  bench/<station>/status   "online" / "offline" (retained)
#   listens on bench/<station>/cmd      for "sp:NN" (a new setpoint)
# Usage:  python sim_node.py        (station s01)
#         python sim_node.py s07    (another station)
import random
import sys
import time
import paho.mqtt.client as mqtt

STATION = sys.argv[1] if len(sys.argv) > 1 else "s01"
LIGHT = f"bench/{STATION}/light"
STATUS = f"bench/{STATION}/status"
CMD = f"bench/{STATION}/cmd"

sp = 50.0        # the setpoint the loop aims for, in %
pv = 20.0        # the light level reached so far, in %

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(CMD)
    client.publish(STATUS, "online", retain=True)
    print(f"sim node {STATION}: connected to the broker", flush=True)

def on_message(client, userdata, msg):
    global sp
    text = msg.payload.decode()
    if text.startswith("sp:"):
        try:
            sp = max(0.0, min(100.0, float(text[3:])))
            print(f"  >>> command received: setpoint is now {sp:.0f} %", flush=True)
        except ValueError:
            print(f"  >>> command ignored: {text}", flush=True)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.will_set(STATUS, "offline", retain=True)    # the broker says this if we vanish
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect("localhost", 1883)
except OSError:
    sys.exit("No broker on localhost:1883. Run:  sudo systemctl start mosquitto")
client.loop_start()
while not client.is_connected():       # wait for the broker's welcome
    time.sleep(0.1)

try:
    while True:
        pv += 0.3 * (sp - pv) + random.uniform(-0.4, 0.4)   # close 30 % of the gap
        pv = max(0.0, min(100.0, pv))
        client.publish(LIGHT, f"{pv:.1f}")
        print(f"light {pv:5.1f} %   (setpoint {sp:.0f} %)", flush=True)
        time.sleep(1)
except KeyboardInterrupt:
    client.publish(STATUS, "offline", retain=True).wait_for_publish(2)
    client.disconnect()
    client.loop_stop()
    print("\nsim node stopped, status set to offline")
