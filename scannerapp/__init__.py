#!/usr/bin/python2.7
import os
import sys
import random
import string

import pyinsane.abstract as pyinsane
from pyinsane.rawapi import SaneException
from PIL import Image
from flask import Flask, render_template, request, flash, url_for, send_file

import config

app = Flask(__name__, static_url_path='')
app.secret_key = 'some_secret'
  
@app.route('/')
def index():

    devices = pyinsane.get_devices()

    return render_template('index.html', devices=devices)  

@app.route('/scan', methods=['POST'])
def scan_view():

    if request.method == 'POST':

        resolution = int(request.form['resolution'])
        format = request.form['format']
        mode = request.form['colortype']
        device_choice = request.form['device']
    
        devices = pyinsane.get_devices()
        scanner = [device for device in devices if device_choice in device.name][0]

        image, log = perform_scan(scanner, resolution=resolution, mode=mode)

        if image:

            temp_filename = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10)) + '.' + format
            temp_dir = getattr(config, 'temp_dir', '/tmp')

            if not os.path.exists(temp_dir):
                os.makedirs(temp_dirs)

            image_path = temp_dir+temp_filename
            image.save(image_path, quality=100)

            return render_template('scan.html', image=temp_filename, format=format)

        else:

            return render_template('scan_failed.html', error = log)



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


@app.route('/get_uncropped', methods=['POST'])
def get_uncropped():
    
    if request.method == 'POST':
        import re, string

        pattern = re.compile('[\W]+')

        temp_filename = request.form['temp_filename']
        filename = pattern.sub('', request.form['filename']) + "." + temp_filename.split('.', 1)[-1]
        temp_dir = getattr(config, 'temp_dir', '/tmp')

        path_to_file = temp_dir + temp_filename

        return send_file(path_to_file, as_attachment=True, attachment_filename=filename)

@app.route('/scantest')
def ss():
    
    return render_template('scantest.html')  

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8000, debug=False)
