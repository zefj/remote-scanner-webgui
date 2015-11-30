#!/usr/bin/python2.7
import os
import sys
import random
import string
import json

import pyinsane.abstract as pyinsane
from pyinsane.rawapi import SaneException
from PIL import Image
from flask import Flask, render_template, request, flash, url_for, send_file, jsonify, abort, make_response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import _W, _H

import config

app = Flask(__name__, static_url_path='')
app.secret_key = 'some_secret'
temp_dir = getattr(config, 'temp_dir', '/tmp')

def perform_scan(scanner, **kwargs):

    error = None

    if scanner:
        try:
            for key, val in kwargs.iteritems():
                scanner.options[key].value = val

            scan_session = scanner.scan(multiple=False)

            try:
                while True:
                    scan_session.scan.read()
            except EOFError:
                pass

            return scan_session.images[0], None

        except SaneException:
            error = str(sys.exc_info()[1])
            return None, error
    
    else:
        error = 'No scanner detected.'
        return None, error

def create_pdf(temp_filename, filename):

    c = canvas.Canvas(temp_dir + filename)
    image = Image.open(temp_dir + temp_filename)
    width, height = c.drawInlineImage(image, 0, 0, width = _W, height = _H, preserveAspectRatio=True)
    c.setPageSize((width, height))
    c.showPage()
    c.save()

    return filename

"""
API endpoint for listing available devices. This returns a JSON object with all the devices that, in theory, 'scanimage -L' would recognize. If failed, check your permissions.
"""
@app.route('/list_devices')
def list_devices():

    devices = {}

    for device in pyinsane.get_devices():

        devices[str(device)] = {}
        d = devices[str(device)]

        for opt in device.options.values():
                d[opt.name] = opt.constraint

    if len(devices) == 0:
        return make_response(jsonify({'error': 'No devices found'}), 200)

    return jsonify(**devices)

@app.route('/')
def index():

    return render_template('index.html')  

@app.route('/scan', methods=['POST'])
def scan_view():

    if request.method == 'POST':

        resolution = int(request.form['resolution'])
        format = request.form['format']
        mode = request.form['mode']
        device_choice = request.form['device']
    
        devices = pyinsane.get_devices()
        scanner = [device for device in devices if device.name in device_choice][0]

        image, log = perform_scan(scanner, resolution=resolution, mode=mode)

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_filename = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))

        """
        If PDF is the desired output extension, save temporarily as jpeg to allow display 
        """
        if image and format != 'pdf':
            temp_filename = temp_filename + '.' + format

        elif image and format == 'pdf':
            temp_filename = temp_filename+ '.jpeg'

        else:
            return render_template('scan_failed.html', error = log)

        image.save(temp_dir+temp_filename, quality=100)

        return render_template('scan.html', image=temp_filename, format=format)  

@app.route('/get_uncropped?<string:temp_filename>&<string:format>', methods=['POST'])
def get_uncropped(format, temp_filename):
    
    if request.method == 'POST':
        import re, string

        pattern = re.compile('[\W]+')
        filename = pattern.sub('', request.form['filename']) + "." + format

        if format == 'pdf':
            temp_filename = create_pdf(temp_filename, filename)

        path_to_file = temp_dir + temp_filename

        return send_file(path_to_file, as_attachment=True, attachment_filename=filename)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8000, debug=False)
