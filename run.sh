#!/bin/sh

PORT=${PORT:-8080}
PROCESSES=${PROCESSES:-4}
THREADS=${THREADS:-2}

uwsgi --http :"$PORT" --wsgi-file src/viaastatus/server/wsgi.py --callable application --processes "$PROCESSES" --threads "$THREADS"
