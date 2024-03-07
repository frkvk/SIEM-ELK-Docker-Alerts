#!/bin/bash

echo "alerta1.service   *** iniciando ***" | systemd-cat -p info

contador=1
TOKEN="XXXX"
ID="XXX" 
ID2="XXX"
URL="https://api.telegram.org/bot$TOKEN/sendMessage"

docker logs --tail 10 -f kibana_8.11.0 | grep --line-buffered '.*' | sed -u -n '/Chromium/d;/Firefox/d;/monitoring_alert_cpu_usage/d;/securitySolution/d;/./p' | while read linea;
do
        echo -e "Linea: $contador"
        discomaquinas=$(echo "$linea" | grep "alertdisk")
       	discoesxi=$(echo "$linea" | grep "esxidisk")
        memoriamaquinas=$(echo "$linea" | grep "alertamemoria")
       	dockerstatus=$(echo "$linea" | grep "alertdocker")

	echo $linea
        let contador=contador+1
        Mensaje=$(echo $linea | cut -d'%' -f3-10 | tr -d ';' | tr -d '}' | tr -d '"')

        #Sentencia de discos de maquinas
        if [ "$discomaquinas" != "" ]
        then
                curl -s -X POST $URL -d chat_id=$ID -d text="🗂 Alert %0A $Mensaje"
        #Sentencia de memoria de las maquinas
        elif [ "$memoriamaquinas" != "" ]
        then
                echo "Alerta Memoria Maquina"
                curl -s -X POST $URL -d chat_id=$ID -d text="⚙ Alert %0A $Mensaje"
        #Sentencia de discos de ESXi
        elif [ "$discoesxi" != "" ]
        then
                curl -s -X POST $URL -d chat_id=$ID -d text="🗂 Alert ESXi %0A $Mensaje"
        #Sentencia de Docker
        elif [ "$dockerstatus" != "" ]
        then
                curl -s -X POST $URL -d chat_id=$ID -d text="♿️Alert Docker %0A $Mensaje"
        else
                echo "No hay alerta"
        fi
done
