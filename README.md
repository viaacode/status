# VIAA Status
Quick, simple service to return status of various platforms through calls to PRTG

## Usage

#### Install
```bash
git clone 
pip install status
```

#### Configure
Copy the example `config.ini.example` and fill in necessary config:

```bash
cp config.ini.example /home/user/prtgconf.ini
vi /home/user/prtgconf.ini
```

#### Run

Start server using `uwsgi`

```bash
CONFIG_FILE=/home/user/prtgconf.ini uwsgi --http :8080 --wsgi-file src/viaastatus/server/wsgi.py --processes 4 --threads 2
```

(will read from `/home/user/prtgconf.ini` and launch http server on port 8080)