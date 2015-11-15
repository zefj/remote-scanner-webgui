import pyinsane.abstract as pyinsane

devices = pyinsane.get_devices()
assert(len(devices) > 0)
device = devices[0]

print("I'm going to use the following scanner: %s" % (str(device)))
scanner_id = device.name