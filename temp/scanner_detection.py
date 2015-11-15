import pyinsane.abstract as pyinsane

devices = pyinsane.get_devices()
assert(len(devices) > 0)
device = devices[0]

print("I'm going to use the following scanner: %s" % (str(device)))
scanner_id = device.name

device.options['resolution'].value = 300
# Beware: Some scanner have "Lineart" or "Gray" as default mode
device.options['mode'].value = 'Color'
scan_session = device.scan(multiple=False)
try:
    while True:
        scan_session.scan.read()
except EOFError:
    pass
image = scan_session.images[0]

print(image)