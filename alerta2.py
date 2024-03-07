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
            "_source": ["@timestamp", "agent.name", "host.ip", "source.ip", "event.outcome", "message", "user.name"],
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match": {
                                            "event.outcome": "success"
                                        }
                                    },
                                    {
                                        "match": {
                                            "event.outcome": "failure"
                                        }
                                    }
                                ],
                                "minimum_should_match": 1
                            }
                        },
                        {
                            "match": {
                                "event.dataset": "system.auth"
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
        f = open("resultado.txt", "w")
        f.close()
        f = open("resultado.txt", "a")
        print("--------------------")
        print(response)
        if response != "":
            for hit in response['hits']['hits']:
                source = hit['_source']
                contador = contador + 1
                nombremaquina = str(source['agent']['name'])
                ipmaquina = str(source['host']['ip'])
                if (source.get('source')):
                        iporigen = str(source['source']['ip'])
                        usuario = str(source['user']['name'])
                else:
                        mensaje = str(source['message'])
                        iporigen = re.search(r'rhost=([^\s]+)', mensaje).group(1)
                        usuario = re.search(r'user=([^\s]+)', mensaje).group(1)
                tipoevento = str(source['event']['outcome'])

                cadena5 = """
🚷Alerta, SSH
Fecha: {0}
🖥 {1}
IP Maquina: {2}
👤 {3}
IP Origen: {4}
The SSH event login has resulted in a status: {5}
--------------------
            """.format(source['@timestamp'], nombremaquina, ipmaquina, usuario, iporigen, tipoevento)
                cadena6 = """
🚩🚩ROOT ALERT!!, SSH
Fecha: {0}
🖥 {1}
IP Maquina: {2}
👤 {3}
IP Origen: {4}
The SSH event login has resulted in a status: {5}
--------------------
            """.format(source['@timestamp'], nombremaquina, ipmaquina, usuario, iporigen, tipoevento)
                if "root" in cadena5:
                    f.write(cadena6)
                else:
                    f.write(cadena5)
            f.close()
            f = open("resultado.txt", "r")
            comprobacion = f.read()
            if comprobacion != "":
                f.close()
                f = open("resultado.txt", "a")
                f.write("""https://siemdocker.mol.local/app/dashboards#/view/system-5517a150-f9ce-11e6-8115-a7c18106d86a""")
                f.close()
                f = open("resultado.txt", "r")
                documento = f.read()
                if "Usuario: root" in documento:
                    requests.post(f'https://api.telegram.org/{botid}/sendVideo?chat_id=-416043971&video=https://c.tenor.com/RH0yZZhFk5IAAAAC/alert-warning.gif')
                else:
                    pass
                requests.post(f'https://api.telegram.org/{botid}/sendMessage',
                              data={'chat_id': f'{chatid}', 'text': documento})
                f.close()
                os.system("sed -i '1i Subject:SSH_SIEM_Desarrollo' resultado.txt")
                os.system("echo Alerts send to telegram")
            else:
                os.system("echo No hay datos")
        f.close()
        time.sleep(600)
    except:
        os.system("echo Error al conectarse con Elasticsearch")
        time.sleep(100)
