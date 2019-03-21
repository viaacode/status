# VIAA Status
Quick, simple service to return status of various platforms through calls to PRTG

## Usage

#### Install
```bash
git clone https://github.com/viaacode/status.git
cd status
pip install .
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
CONFIG_FILE=/home/user/prtgconf.ini ./run.sh
```

(will read from `/home/user/prtgconf.ini` and launch http server on port 8080)

You can specify a different port, amount of threads and processes using environmental variables, eg.

```bash
PROCESSES=4 THREADS=8 PORT=80 ./run.sh
```

### Using docker

#### Build

```bash
docker build -t status:latest .
```

#### Run

```bash
docker run -p 8080:8080 -it --name status --rm status:latest
```

The site will then be available at http://127.0.0.1:8080
