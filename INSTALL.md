# FreeBSD/FreeNAS
## Required
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
pw user add -n awesome -s /sbin/nologin -d /media
```

Start the awesome-dl manually
```bash
sudo -u awesome python3.7 -m uvicorn awesomedl:app --host 0.0.0.0 --port 8080
```

or pick your favorite process supervisor or init system to start it automatically

## Optional
Install fail2ban
```bash
pkg install py37-fail2ban
```

Install nginx or the web server of your choice
```bash
pkg install nginx
```

The rest of the tutorial assumes nginx