# app.py, stage 7: a page that reads, a button that acts.
import time
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template, request

STATION = "s01"
latest = {"station": STATION, "pct": None, "status": "unknown",
          "updated": None, "sp": None}

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(f"bench/{STATION}/light")
    client.subscribe(f"bench/{STATION}/status")

def on_message(client, userdata, msg):     # once per MQTT message
    text = msg.payload.decode()
    if msg.topic.endswith("/light"):
        try:
            latest["pct"] = float(text)
            latest["updated"] = time.strftime("%H:%M:%S")
        except ValueError:
            pass                           # not a number: ignore
    else:
        latest["status"] = text

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883)
mqttc.loop_start()               # MQTT now runs in the background

app = Flask(__name__)

@app.route("/")                  # HTML, for people
def home():
    return render_template("dashboard.html", station=STATION)

@app.route("/api/light")         # JSON, for programs
def api_light():
    return jsonify(latest)       # whatever the dict holds right now

# POST only: this route acts
@app.route("/api/setpoint", methods=["POST"])
def api_setpoint():
    try:
        sp = float(request.form["sp"])
    except ValueError:
        return jsonify(ok=False, error="sp must be a number"), 400
    sp = max(0.0, min(100.0, sp))            # keep it in 0..100
    latest["sp"] = sp
    mqttc.publish(f"bench/{STATION}/cmd", f"sp:{sp:.0f}")
    return jsonify(ok=True, sp=sp)

app.run(host="0.0.0.0", port=5000)
