# remote-scanner-webgui
Control your remote scanner from web browser

## Configuration

Make sure you've set `temp_dir` in your `config.py` to an appropriate location. This is where your scanned images will be saved. This is also where your images will be served from, so for the simplicity of deployment I suggest setting it to your static folder, but if you wish to keep them outside of your /var/www, you have to set your web server to serve that folder under `/static` alias.

You also need to make sure www-data has access to your scanner.

## Deployment

You are free to deploy this application to whatever webserver you wish. Given the fact this is supposed to run on your private network, you probably don't need much - I'm running it on a Raspberry Pi with Apache. 

Example Apache configuration:

    <VirtualHost *:80>
        WSGIDaemonProcess scanner user=www-data group=www-data threads=5
        WSGIScriptAlias /scanner /var/www/scannerapp/scannerapp.wsgi
        <Directory /var/www/scannerapp/scannerapp/>
                Order allow,deny
                Allow from all
        </Directory>
        Alias /static /var/www/scannerapp/scannerapp/static
        <Directory /var/www/scannerapp/scannerapp/static/>
                Order allow,deny
                Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>


## Cron job

To make sure you don't run out of disk space, you need to add a Cron job:

``
*/30 * * * * find /var/www/scannerapp/scannerapp/static/ -type f -amin +30 -delete
``

Please notice the path needs to be customised to whatever your `temp_dir` in `config.py` is. This particular job will run every 30 minutes and delete files last accessed more than 30 minutes ago. 

#### Why do I have to do that?

I've decided temporary files clean up is so straightforward to implement with cron jobs it was unnecessary to code such functionality in the app itself, be it by using a task scheduler, tempfiles, or other hacks in the code. Most other solutions would also essentially be overkill for this simple purpose, and incorporate unneeded difficulties in configuration, customization or maintenance. With a cron job, you can easily change the behaviour to suit your needs.

## TODO
* readme
* internationalization
* clean everything up
* about/settings page with scanner properties
* more image formats
* config, tests
* come up with a better way to code paths
