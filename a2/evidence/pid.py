# pid.py: PID controller with output clamping, anti-windup and derivative on measurement
class PIDController:
    """Three-term controller. Call update(sp, pv, dt) once per cycle."""

    def __init__(self, kp, ki, kd, out_min=0.0, out_max=100.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_min, self.out_max = out_min, out_max
        self.integral = 0.0      # accumulated past error
        self.prev_pv = None      # for the slope; None = first call

    def update(self, sp, pv, dt):
        e = sp - pv
        cand = self.integral + e * dt            # candidate new accumulator
        if self.prev_pv is None or dt <= 0:
            dpv = 0.0                            # no slope on first call
        else:
            dpv = (pv - self.prev_pv) / dt       # measurement slope (no setpoint kick)
        self.prev_pv = pv

        u = self.kp * e + self.ki * cand - self.kd * dpv
        if u > self.out_max:
            u = self.out_max                     # clamp: the LED has no 130 %
        elif u < self.out_min:
            u = self.out_min
        else:
            self.integral = cand                 # anti-windup: integrate only when unsaturated
        return u
