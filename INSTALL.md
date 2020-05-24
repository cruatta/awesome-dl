# FreeBSD/FreeNAS
## Required
Create a new jail for awesome-dl and exec into it
```bash
jexec <jid> sh
```

Install the prerequisites, with sudo or as root 
```bash
pkg install sudo python37 py37-pip py37-sqlite3 py37-certifi curl
```

You might be asking why we need curl? curl installs some important dependencies to make certificate checks work with youtube-dl, including `ca_root_nss`, the curl CA certificate bundle

Next, transport the awesome_dl wheel file to your server

```bash
pip install awesome_dl*.whl
```

Create a user for awesome-dl

```bash
pw user add -n awesome -s /usr/sbin/nologin -d /media
```

Create a logs directory
```bash
mkdir -p /var/log/awesome-dl
chown -R awesome /var/log/awesome-dl
```

Start the awesome-dl manually
```bash
cd /media
sudo -u awesome python3.7 -m uvicorn awesomedl:app --host 0.0.0.0 --port 8080 2>&1 | tee /var/log/awesome-dl/awesome.log
```

or pick your favorite process supervisor or init system to start it automatically