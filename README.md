# VIAA Status
Quick, simple service to return status of various platforms through calls to PRTG.

## Usage

#### Install

First get the code by cloning the repository from github (alternatively download the zip and extract).

```bash
git clone https://github.com/viaacode/status.git
cd status
```

Depending on what you want to use as WSGI HTTP Server you need to specify additional requirement to be installed.

Currently supported:

 - uWSGI

   ```bash
   python -m pip install '.[uwsgi]'
   ```

 - gunicorn

   ```bash
   python -m pip install '.[gunicorn]'
   ```

 - waitress (supported on Windows)

   ```bash
   python -m pip install '.[waitress]'
   ```

#### Configure
Copy the example `config.ini.example` and fill in necessary config:

```bash
cp config.ini.example /home/user/prtgconf.ini
vi /home/user/prtgconf.ini
```

#### Run

Start server using the `./run.sh` script. By default it will attempt to use `uWSGI`.

```bash
CONFIG_FILE=/home/user/prtgconf.ini ./run.sh
```

(will read from `/home/user/prtgconf.ini` and launch http server on port 8080)

By default the `run.sh` script will read `config.ini` from the current directory. 

You can specify a different port, amount of threads and processes using environmental variables, eg.

```bash
PROCESSES=4 THREADS=8 PORT=80 ./run.sh
```

To run using a different WSGI server than the default uWSGI, use the STRATEGY environmental variable.

```bash
STRATEGY=gunicorn ./run.sh
STRATEGY=waitress ./run.sh
```

If `STRATEGY` is anything different than "gunicorn" or "waitress", the default `uwsgi` will be used.

To run with the default Flask WSGI HTTP server (not for production!), use:

```bash
python src/viaastatus/server/wsgi.py
```

There is also a `run.bat` file available for Windows that uses `waitress-serve` to serve the site with 4 threads on port 80.

### Using docker

The docker image uses `uWSGI` as WSGI HTTP server.

#### Build

```bash
docker build -t status:latest .
```

#### Run

```bash
docker run -p 8080:8080 -it --name status --rm status:latest
```

The site will then be available at http://127.0.0.1:8080
