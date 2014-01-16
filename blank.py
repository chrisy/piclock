#!/usr/bin/env python
# SPI Clock

import spidev
import time, datetime
import math

speed = 1000000
bpw = 8

spi = spidev.SpiDev()
spi.open(0,0)
spi.bits_per_word = bpw
spi.lsbfirst = False
spi.mode = 0
spi.max_speed_hz = speed

p = []
for i in range(46):
	p.append(0)
	p.append(0)
	p.append(0)

# Send the data!
spi.xfer2(p, speed, 500, bpw)

