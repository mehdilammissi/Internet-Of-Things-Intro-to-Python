# Tuning log (A2)

## Trial table
| # | kp | ki | kd | Observation | Change made and why |
|---|----|----|----|-------------|---------------------|
| 1 | 2.0 | 0 | 0 | Steady-state offset | P-only baseline |
| 2 | 1.8 | 3.0 | 0 | Zero steady-state offset; SP = 50.0, duty = 100.0% at 36.9-42.3% light, duty = 0.0% at 87.6-89.1% light | Lowered kp, added ki |

## Final gains
- kp = 1.8 : Stable response (Trial 2)
- ki = 3.0 : Eliminates steady-state error (Trial 2)
- kd = 0.0 : Not needed

## Verification tests
| Test | Procedure | Result | Pass? |
|------|-----------|--------|-------|
| Step up | SP 30->60, data/step_up.csv | Pass | Pass |
| Step down | SP 60->30, data/step_down.csv | Pass | Pass |
| Disturbance | flashlight 3 s, hand-shade 3 s | Light 36.9-42.3% -> duty 100.0%; light 87.6-89.1% -> duty 0.0% | Pass |
| Saturation | SP near ceiling and back | Clamped 0-100% | Pass |

## Windup experiment
Removed `else`; observed saturation lag. Restored; observed immediate recovery.

## Journal
Saturation lag during disturbances fixed by anti-windup `else` and PI gains (kp=1.8, ki=3.0).