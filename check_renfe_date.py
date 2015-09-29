#!/bin/env python
# -*- coding: utf-8 -*-
# State: alpha

from bs4 import BeautifulSoup as bs
import json
import ConfigParser
import requests

Config = ConfigParser.ConfigParser()
Config.read('data.conf')

def check_renfe_date():
    urlbase = 'https://venta.renfe.com/vol/index.do'
    url = 'https://venta.renfe.com/vol/buscarTren.do'
    origin = Config.get('renfe', 'origin')
    dest = Config.get('renfe', 'dest')
    date = Config.get('renfe', 'date')
    script_sessionid = ''

    estaciones_payload = "callCount=1&windowName=&c0-scriptName=estacionesManager&c0-methodName=getEstacionesIntAuto&c0-id=0&batchId=1&instanceId=0&page=%2Fvol%2Findex.do&scriptSessionId=o*ygDPpho6ORWkCO1ve8EDGao1l/3ocIo1l-VrlGaOSP6"
    payload = "cdgoOrigen=0071%2C03216%2C03216&cdgoDestino=0071%2C51003%2C51003&tipoBusqueda=autocomplete&desOrigen=Valencia+Joaquin+Sorolla&desDestino=Sevilla-Santa+Justa&ninos=0&currenLocation=menuBusqueda&operation=&grupos=false&tipoOperacion=IND&empresas=false&getTarifasSesion=false&adultos=1&actTipoViajero=true&IdOrigen=Valencia+Joaquin+Sorolla&IdDestino=Sevilla-Santa+Justa&FechaIdaSel=29%2F09%2F2015&HoraIdaSel=00%3A00&FechaVueltaSel=&HoraVueltaSel=00%3A00&adultos_=1&ninos_=0&ninosMenores=0&codPromocional=&txtoUsuario=&txtoPass="

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
        'Accept-Encoding': 'gzip, deflate', 
        'Accept-Language': 'en-US,en;q=0.8,es;q=0.6', 
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Host': 'venta.renfe.com', 
        'Origin': 'https://venta.renfe.com', 
        'Pragma': 'no-cache', 
        'Referer': 'https://venta.renfe.com/vol/inicioCompra.do', 
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
    }

    session = requests.Session()
    estaciones = session.post('https://venta.renfe.com/vol/dwr/call/plaincall/estacionesManager.getEstacionesIntAuto.dwr', data=estaciones_payload, headers=headers) .text
    # Regex to extract real JSON
    estaciones = json.loads(estaciones)
    
    session.get(urlbase)
    
    response = session.post(url, data=payload, headers=headers).text
    if "Se ha producido un error" in response:
        print response
        print "Error"
    elif "AVE" in response:
        res = bs(response, 'html.parser')
        print res
        print "Buy your ticket"


if __name__ == "__main__":
    check_renfe_date()
