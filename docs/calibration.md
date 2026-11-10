Week 8 Calibration Report
Dark Anchor (1850): Our bench recorded a dark baseline of 1850 counts by completely covering the LDR sensor with an opaque cap in ambient room light. 
We allowed the raw ADC readings to settle completely before logging this minimum threshold value.
Bright Anchor (51200): Our bench recorded a bright ceiling of 51200 counts by holding a smartphone flashlight approximately $5\text{ cm}$ directly above the sensor. 
This forced the ADC signal to peak near its upper saturation limit under direct illumination.
Averaging Configuration ($n = 16$): Our software calculates a moving average using $n = 16$ consecutive samples per reading cycle.
This specific sample size effectively suppresses high-frequency electrical noise and ambient lighting flicker while maintaining responsive, real-time performance.
