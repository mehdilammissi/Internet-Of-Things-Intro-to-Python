# main.py: PID light loop + Wi-Fi + MQTT
from time import ticks_ms, ticks_diff, sleep_ms
from pid import PIDController
from lightnode import LightNode
import net
import config

net.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)

# MQTT: if it fails, the control loop still runs
client = None
try:
    from umqtt.simple import MQTTClient
    client = MQTTClient("esp32-" + config.STATION, config.BROKER_IP)
    client.connect()
    print("MQTT OK")
except Exception as e:
    print("MQTT failed:", e)
    client = None

T_PV = ("bench/%s/light" % config.STATION).encode()
T_SP = ("bench/%s/setpoint" % config.STATION).encode()
T_U = ("bench/%s/duty" % config.STATION).encode()

PERIOD_MS = 100                 # 10 Hz control loop
KP, KI, KD = 1.8, 3.0, 0.0      # starting gains

# Set STEP_TEST to the list below for the step test, None for a fixed setpoint
STEP_TEST = None                # [(0, 30.0), (6, 60.0), (14, 30.0)]
END_S = 22
FIXED_SP = 50.0

node = LightNode(adc_pin=34, pwm_pin=25, dark=200, bright=3550)
pid = PIDController(KP, KI, KD)


def sp_at(t_s):
    if not STEP_TEST:
        return FIXED_SP
    sp = STEP_TEST[0][1]
    for t0, v in STEP_TEST:
        if t_s >= t0:
            sp = v
    return sp


if STEP_TEST:
    print("t_ms,sp,pv,u")

start = prev = ticks_ms()
count = 0
while True:
    now = ticks_ms()
    dt = ticks_diff(now, prev) / 1000
    prev = now
    t_ms = ticks_diff(now, start)

    sp = sp_at(t_ms / 1000)
    pv = node.read_pct()
    u = pid.update(sp, pv, dt)
    node.set_brightness(u)

    if STEP_TEST:
        print("%d,%.1f,%.1f,%.1f" % (t_ms, sp, pv, u))
        if t_ms / 1000 > END_S:
            node.set_brightness(0)
            break

    count += 1
    if client and count % 5 == 0:       # twice a second
        try:
            client.publish(T_PV, ("%.1f" % pv).encode())
            client.publish(T_SP, ("%.1f" % sp).encode())
            client.publish(T_U, ("%.1f" % u).encode())
        except Exception as e:
            print("publish failed:", e)
            client = None

    sleep_ms(max(0, PERIOD_MS - ticks_diff(ticks_ms(), now)))