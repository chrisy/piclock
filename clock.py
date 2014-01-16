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

# We have 7 segments
# They are arranged in a chain more or less thus
#   ---2---   ---2---
#  |       | |
#  3       1 3
#  |       | |
#   ---0---   ---0---  ...
#  |       | |
#  4       6 4
#  |       | |
#   ---5---   ---5---

# Ratio of segment proximities to the corners
# top-left, top-right, bottom-left, bottom-right
proximity = {
	0: [ 0.25, 0.25, 0.25, 0.25 ],
	1: [ 0, 1, 0, 0 ],
	2: [ 0.5, 0.5, 0, 0 ],
	3: [ 1, 0, 0, 0 ],
	4: [ 0, 0, 1, 0 ],
	5: [ 0, 0, 0.5, 0.5 ],
	6: [ 0, 0, 0, 1 ]
}

# Mask of which segements are lit for each numeral
digits = {
	0: [ 0, 1, 1, 1, 1, 1, 1 ],
	1: [ 0, 1, 0, 0, 0, 0, 1 ],
	2: [ 1, 1, 1, 0, 1, 1, 0 ],
	3: [ 1, 1, 1, 0, 0, 1, 1 ],
	4: [ 1, 1, 0, 1, 0, 0, 1 ],
	5: [ 1, 0, 1, 1, 0, 1, 1 ],
	6: [ 1, 0, 0, 1, 1, 1, 1 ],
	7: [ 0, 1, 1, 0, 0, 0, 1 ],
	8: [ 1, 1, 1, 1, 1, 1, 1 ],
	9: [ 1, 1, 1, 1, 0, 1, 1 ],

	# Random alphas/symbols that work
	'a': [ 1, 1, 1, 1, 1, 0, 1 ],
	'b': [ 1, 0, 0, 1, 1, 1, 1 ],
	'c': [ 1, 0, 0, 0, 1, 1, 0 ],
	'd': [ 1, 1, 0, 0, 1, 1, 1 ],
	'e': [ 1, 0, 1, 1, 1, 1, 0 ],
	'f': [ 1, 0, 1, 1, 1, 0, 0 ],
	'g': [ 1, 1, 1, 1, 0, 1, 1 ],
	'h': [ 1, 1, 0, 1, 1, 0, 1 ],
	'i': [ 0, 0, 0, 1, 1, 0, 0 ],
	'j': [ 0, 1, 0, 0, 0, 1, 1 ],
	'l': [ 0, 0, 0, 1, 1, 1, 0 ],
	'n': [ 1, 0, 0, 0, 1, 0, 1 ],
	'o': [ 1, 0, 0, 0, 1, 1, 1 ],
	'p': [ 1, 1, 1, 1, 1, 0, 0 ],
	'q': [ 1, 1, 1, 1, 0, 0, 0 ],
	'r': [ 1, 0, 0, 0, 1, 0, 0 ],
	's': [ 1, 0, 1, 1, 0, 1, 1 ],
	't': [ 1, 0, 0, 1, 1, 1, 0 ],
	'u': [ 0, 0, 0, 0, 1, 1, 1 ],
	'@': [ 1, 1, 1, 1, 1, 1, 0 ],
	'"': [ 0, 1, 0, 1, 0, 0, 0 ],
	"'": [ 0, 1, 0, 0, 0, 0, 0 ],
	'[': [ 0, 0, 1, 1, 1, 1, 0 ],
	']': [ 0, 1, 1, 0, 0, 1, 1 ],
	'|': [ 0, 1, 0, 0, 0, 0, 1 ],
	'-': [ 1, 0, 0, 0, 0, 0, 0 ],
	'_': [ 0, 0, 0, 0, 0, 1, 0 ],
}

def place_digit(value, arr, colors):
	mask = digits[value]
	for idx in range(7):
		if mask[idx]:
			arr.append(colors[idx][0])
			arr.append(colors[idx][1])
			arr.append(colors[idx][2])
		else:
			arr.append(0)
			arr.append(0)
			arr.append(0)

digit_count = 6
segment_count = digit_count * 7

# Build the color chain
count = 100
freq = 0.08
#freq = math.pi / count

pi2 = 2*math.pi/3
pi4 = 4*math.pi/3

def dsin(index, offset):
	return int(math.sin(freq*index + offset) * 127 + 64) & 0xff

chain = []
for i in range(count):
	chain.append([	dsin(i, 0),
			dsin(i, pi2),
			dsin(i, pi4)
	])

offset = 0
while True:
	p = []
	t = datetime.datetime.now().time()
	tdigits = []
	tdigits.append(int(t.hour / 10))
	tdigits.append(t.hour % 10)
	tdigits.append(int(t.minute / 10))
	tdigits.append(t.minute % 10)
	tdigits.append(int(t.second / 10))
	tdigits.append(t.second % 10)

	adj = 1.0
	if t.hour < 7 or t.hour > 16:
		adj = 0.25

	# Place the digits
	for i in range(digit_count):
		colors = []
		for s in range(7):
			idx = int(offset + i + s) % count
			colors.append([ chain[idx][0], chain[idx][1], chain[idx][2] ])
		place_digit(tdigits[i], p, colors)

	# Now place the dots
	if (t.microsecond / 4) < int(1000000 / 8):
		for i in range(4):
			p.append(0)
			p.append(0)
			p.append(0)
	else:
		for i in range(4):
			p.append(128)
			p.append(128)
			p.append(128)

	# Adjust the brightness!
	for i in range(len(p)):
		p[i] = int(p[i] * adj)

	# Send the data!
	spi.xfer2(p, speed, 500, bpw)

	# Wait briefly...
	time.sleep(0.01)

	offset += 0.1
	if offset >= count: offset = 0

