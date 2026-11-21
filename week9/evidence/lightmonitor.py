# lightmonitor.py: a monitor with memory
import paho.mqtt.client as mqtt
class LightMonitor:
    """Follows one station's light topic; remembers the latest reading."""
    def __init__(self, broker, station):
        self.topic    = f"bench/{station}/light"
        self.last_pct = None
        self.count    = 0
        self.client   = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect      # bound methods as callbacks:
        self.client.on_message = self.on_message      # self travels with the function
        self.client.connect(broker, 1883)
    def on_connect(self, client, userdata, flags, reason_code, properties):
        client.subscribe(self.topic)
    def on_message(self, client, userdata, msg):
        self.last_pct = float(msg.payload.decode())
        self.count += 1
        self.react()
    def react(self):
        print(f"[{self.count:4d}] {self.topic}: {self.last_pct:.1f} %")
    def run(self):
        self.client.loop_forever()
if __name__ == "__main__":
    LightMonitor("localhost", "s07").run()