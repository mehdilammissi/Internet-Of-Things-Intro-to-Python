from machine import ADC, Pin, PWM


class LightNode:
    def __init__(self, adc_pin=34, pwm_pin=25, dark=200, bright=3550):
        self.adc = ADC(Pin(adc_pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.pwm = PWM(Pin(pwm_pin), freq=1000)
        self.dark = dark
        self.bright = bright

    def read_raw(self):
        return self.adc.read()

    def read_pct(self):
        pct = (self.read_raw() - self.dark) / (self.bright - self.dark) * 100
        return max(0.0, min(100.0, pct))

    def set_led(self, duty_u16):
        self.pwm.duty_u16(duty_u16) 