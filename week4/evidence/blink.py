from gpiozero import LED
from time import sleep

led = LED(17)

for n in range(10):
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
    print(f"blink {n}")

