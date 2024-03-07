Scripts to send alerts to telegram from a ELK SIEM Dockerized.

Make a service with the differents scripts in ubuntu:

$ sudo nano /etc/systemd/system/alerta2.service

[Unit]
Description=Script 1 example
After=networking.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /srv/scriptsalerts/alerta2.py
WorkingDirectory=/srv/scriptsalerts


[Install]
WantedBy=multi-user.target


$ sudo systemctl daemon-reload
$ sudo systemctl start alerta2.service
$ sudo systemctl enable alerta2.service

The scripts are configurated to read the elasticsearch database (logs-*) every 10 mins. And if see some coincidences, it send a telegram message
