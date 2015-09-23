#/bin/sh

# Settings for deploy
ip=`ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'`
port=8081
chdir=.
env=DJANGO_SETTINGS_MODULE=eliot.settings
module=eliot.wsgi:application
master=True
pidfile=uwsgi_eliot.pid
max_requests=5000
daemonize=$chdir/log/server.log
buffer_size=32768
static_map=/eliot/static=static
stats=127.0.0.1:9191
wsgi_file=$chdir/eliot/wsgi.py
processes=12
threads=120

# Run uwsgi
uwsgi --socket $ip:$port --chdir $chdir --env $env --processes $processes --threads $threads --stats $stats  --protocol=http --wsgi-file $wsgi_file --static-map=$static_map --static-gzip-all --callable=eliot --max-requests=$max_requests --pidfile=$pidfile --master --buffer-size=$buffer_size --module $module --daemonize=$daemonize --log-maxsize 24M

