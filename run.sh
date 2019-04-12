#!/bin/sh

PORT=${PORT:-8080}
PROCESSES=${PROCESSES:-4}
THREADS=${THREADS:-2}
STRATEGY=${STRATEGY:-uwsgi}
IP=${IP:-0.0.0.0}

if [[ "$STRATEGY" == "gunicorn" ]]; then
   gunicorn viaastatus.server.wsgi:application --bind "$IP":"$PORT" --workers "$PROCESSES"
elif [[ "$STRATEGY" == "waitress" ]]; then
   waitress-serve --port "$PORT" --threads "$THREADS" viaastatus.server.wsgi:application
elif [[ "$STRATEGY" == "flask" ]]; then
   echo "WARNING: ONLY USE THIS FOR DEVELOPMENT"
   python src/viaastatus/server/wsgi.py
else
   uwsgi --http "$IP":"$PORT" --wsgi-file src/viaastatus/server/wsgi.py --callable application --processes "$PROCESSES" --threads "$THREADS"
fi
