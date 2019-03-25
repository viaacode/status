#!/bin/sh

PORT=${PORT:-8080}
PROCESSES=${PROCESSES:-4}
THREADS=${THREADS:-2}
STRATEGY=${STRATEGY:-uswgi}

if [[ "$STRATEGY" == "gunicorn" ]]; then
   gunicorn viaastatus.server.wsgi:application --bind 0.0.0.0:"$PORT" --workers "$PROCESSES"
else
   uwsgi --http :"$PORT" --wsgi-file src/viaastatus/server/wsgi.py --callable application --processes "$PROCESSES" --threads "$THREADS"
fi
