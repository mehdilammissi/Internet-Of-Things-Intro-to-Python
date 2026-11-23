# verify.py: checks the Last Week dashboard, end to end, in about 25 seconds.
# Run it on the Pi, in the venv, while app.py and the node are both running:
#     python verify.py
# It prints one PASS or FAIL line per check and a RESULT line for the report.
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import paho.mqtt.client as mqtt

BASE = "http://localhost:5000"
results = []


def http(method, url, data=None):
    """Return (status code, content type, body text). Code 0 means no answer."""
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=4) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read().decode()
    except Exception:
        return 0, "", ""


def check(n, ok, what, detail, hint=""):
    results.append(ok)
    print(f"{n:>2} {'PASS' if ok else 'FAIL'}  {what:<42} {detail}", flush=True)
    if not ok and hint:
        print(f"         fix: {hint}", flush=True)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))      # no packet is sent
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def light():
    code, ctype, body = http("GET", BASE + "/api/light")
    try:
        return code, ctype, json.loads(body)
    except ValueError:
        return code, ctype, {}


print("Last Week check", time.strftime("%Y-%m-%d %H:%M:%S"), "host", socket.gethostname())

# 1  the page answers on the Pi itself
code, ctype, body = http("GET", BASE + "/")
check(1, code == 200 and "text/html" in ctype, "page answers on localhost",
      f"{code} {ctype.split(';')[0]}", "start app.py in Terminal A")
if code == 0:
    sys.exit("RESULT 0/8  the server is not running, nothing else can be checked")

# 2  the page answers on the network address (the bind wall is down)
ip = lan_ip()
if ip is None or ip.startswith("127."):
    check(2, False, "page answers on the network address", "no network address",
          "connect the Pi to a network, then run again")
else:
    code, _, _ = http("GET", f"http://{ip}:5000/")
    check(2, code == 200, f"page answers on {ip}", str(code),
          'the last line of app.py must be app.run(host="0.0.0.0", port=5000)')

# 3  the data route answers with JSON
code, ctype, d = light()
keys = all(k in d for k in ("station", "pct", "status"))
check(3, code == 200 and "application/json" in ctype and keys, "/api/light answers with JSON",
      f"{code} {ctype}", "app.py needs the /api/light route from stage 5")
station = d.get("station", "s01")

# 4  an unknown path is a clean 404
code, _, _ = http("GET", BASE + "/nope")
check(4, code == 404, "unknown path /nope is refused", str(code))

# 5  the values are live: the bridge is fed by MQTT
first = d
time.sleep(3.2)
_, _, second = light()
live = second.get("pct") is not None and second.get("updated") != first.get("updated")
check(5, live, "readings are live (two reads, 3 s apart)",
      f"{first.get('pct')} -> {second.get('pct')}  status {second.get('status')}",
      "start the node in Terminal B, and check that STATION is s01 in app.py")

# 6  the setpoint route rejects GET
code, _, _ = http("GET", BASE + "/api/setpoint")
check(6, code == 405, "GET /api/setpoint is refused", str(code),
      "app.py must be the stage 7 version, with the /api/setpoint route")

# 7  a POST becomes an MQTT command
heard = []
listener = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
listener.on_connect = lambda c, u, f, rc, p: c.subscribe(f"bench/{station}/cmd")
listener.on_message = lambda c, u, m: heard.append(m.payload.decode())
try:
    listener.connect("localhost", 1883)
    listener.loop_start()
    time.sleep(0.8)
except OSError:
    pass
now = second.get("pct") or 50.0
target = 30 if now > 50 else 70
code, _, body = http("POST", BASE + "/api/setpoint", {"sp": target})
time.sleep(1.0)
check(7, code == 200 and f"sp:{target}" in heard, f"POST sp={target} reaches bench/{station}/cmd",
      f"{code} heard {heard}", "app.py must be the stage 7 version, and mosquitto must be active")

# 8  the loop closes: the reading follows the setpoint
t0 = time.time()
settled = None
pct = now
while time.time() - t0 < 20:
    _, _, d = light()
    pct = d.get("pct")
    if pct is not None and abs(pct - target) <= 3:
        settled = time.time() - t0
        break
    time.sleep(1)
check(8, settled is not None, f"reading follows the setpoint ({now} -> {target})",
      f"within 3 points after {settled:.0f} s" if settled is not None else f"still {pct} after 20 s",
      "start the node in Terminal B; a real node needs its own controller running")
try:
    listener.loop_stop()
    listener.disconnect()
except Exception:
    pass

print(f"RESULT {sum(results)}/8  station {station}  host {socket.gethostname()}  "
      f"{time.strftime('%Y-%m-%d %H:%M')}")
