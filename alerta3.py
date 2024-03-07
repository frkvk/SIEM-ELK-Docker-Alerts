from elasticsearch import Elasticsearch
from elasticsearch.serializer import JSONSerializer
from configparser import ConfigParser, ExtendedInterpolation
import os
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SetEncoder(JSONSerializer):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONSerializer.default(self, obj)


def readConfig():
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read("elastic.ini")
    global es
    global botid
    global chatid

    es = Elasticsearch(
        [config['Global']['IP']],
        http_auth=(config['Global']['usuario'], config['Global']['password']),
        scheme=config['Global']['scheme'],
        port=config['Global']['port'],
        verify_certs=(config['Global']['verify_certs'] == 1),
        serializer=SetEncoder()
    )
    botid = config["Global"]["TokenBot"]
    chatid = config["Global"]["TelegramChatID"]

busqueda = {"size": 40,
            "_source": ["@timestamp", "message"],
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match": {
                                            "tags": "WatchGuard-XXX"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "match": {
                                "message": "*credentials*"
                            }
                        },
                        {
                            "range": {"@timestamp": {"gte": "now-10m", "lt": "now"}}
                        }
                    ]
                }
            }
            }

while True:
    try:
        readConfig()
        contador = 0
        response = es.search(index='logs-*', body=busqueda)
        f = open("brutelogin.txt", "w")
        f.close()
        f = open("brutelogin.txt", "a")
        print("--------------------")
        print(response)
        if response != "":
            for hit in response['hits']['hits']:
                source = hit['_source']
                contador = contador + 1
                mensajeintento = str(source['message'])
                if "WebUI" in mensajeintento:
                    mensajeintento = re.search(r'WebUI(.*)', mensajeintento).group(1)
                    mensajeintento = f"WebUI {mensajeintento}"
                    tipodeacceso = " 🔴 Web interna"
                else:
                    mensajeintento = re.search(r'Authentication(.*)', mensajeintento).group(1)
                    mensajeintento = f"Authentication {mensajeintento}"
                    tipodeacceso = " 🟡 Web externa (Download profile .ovpn)"

                cadena5 = """
🚷Intento Logins Watchguard
Fecha: {0}
Tipo de Alerta: {1}
Alerta: {2}
--------------------
            """.format(source['@timestamp'], tipodeacceso, mensajeintento)
                f.write(cadena5)
            f.close()
            f = open("brutelogin.txt", "r")
            comprobacion = f.read()
            if comprobacion != "":
                f.close()
                f = open("brutelogin.txt", "a")
                f.write("""URL PANEL KIBANA""")
                f.close()
                f = open("brutelogin.txt", "r")
                documento = f.read()
                requests.post(f'https://api.telegram.org/{botid}/sendMessage',
                              data={'chat_id': f'{chatid}', 'text': documento})
                f.close()
                os.system("sed -i '1i Subject:VPN Portal Logins' brutelogin.txt")
                os.system("echo Enviado telegram Alerta Siem Desarrollo")
            else:
                os.system("echo No hay datos")
        f.close()
        time.sleep(600)
    except:
        os.system("echo Error al conectarse con Elasticsearch")
        time.sleep(100)
