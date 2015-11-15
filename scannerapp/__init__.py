#!/usr/bin/python2.7
import os
import config

from flask import Flask, send_file, render_template, request, flash, url_for, g

app = Flask(__name__, static_url_path='')
app.secret_key = 'some_secret'


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response

def command_builder(format, resolution, color):

    import string
    import random

    temp_filename = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))

    scan_command = "/usr/bin/scanimage " + '--format=tiff' + " --resolution " + resolution + "dpi" + " > " + config.temp_dir +"/" + temp_filename + ".tiff"
    convert_command = "convert " + config.temp_dir + "/" + temp_filename + ".tiff " + config.temp_dir + "/" + temp_filename + "." + format
    rm_command = "rm " + config.temp_dir + "/" + temp_filename + ".tiff"

    temp_filename = temp_filename + "." + format

    return scan_command, convert_command, rm_command, temp_filename

def scanmethod(scan_command, convert_command, rm_command):
        
    os.system(scan_command)
    os.system(convert_command)
    os.system(rm_command)
    return
    
@app.route('/')
def index():
    return render_template('index.html')    

@app.route('/download', methods=['POST'])
def get_uncropped():
    print "tak"
    print request.method
    if request.method == 'POST':
        
        temp_filename = request.form['temp_filename']
        filename = request.form['filename'] + "." + temp_filename.split('.', 1)[-1]
        print temp_filename, filename

        path_to_file = config.temp_dir + "/" + temp_filename

        @after_this_request
        def gc(response):
            rm_command = "rm " + config.temp_dir + "/" + temp_filename
            os.system(rm_command)
            return render_template('index.html')

        return send_file(path_to_file, as_attachment=True, attachment_filename=filename)
    else:
        abort(404)

@app.route('/scantest')
def ss():
    return render_template('scantest.html')  

@app.route('/scan', methods=['POST'])
def scan():
    if request.method == 'POST':
        res = request.form['resolution']
        format = request.form['format']
        color = request.form['colortype']

        scan_command, convert_command, rm_command, temp_filename = command_builder(format, res, color)
        scanmethod(scan_command, convert_command, rm_command)
        
        return render_template('scan.html', temp_filename=temp_filename)

        # return send_file(dir_to_file, as_attachment=True, attachment_filename=filename)
                

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8000)
