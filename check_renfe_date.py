#!/bin/env python
# -*- coding: utf-8 -*-
# State: alpha

from bs4 import BeautifulSoup as bs
import json
import ConfigParser
import re
import requests

Config = ConfigParser.ConfigParser()
Config.read('data.conf')

def check_renfe_date():
    urlbase = 'https://venta.renfe.com/vol/index.do'
    url = 'https://venta.renfe.com/vol/buscarTren.do'
    origin = Config.get('renfe', 'origin')
    dest = Config.get('renfe', 'dest')
    date = Config.get('renfe', 'date').replace('-', '%2F')

    estaciones_payload = "callCount=1&windowName=&c0-scriptName=estacionesManager&c0-methodName=getEstacionesIntAuto&c0-id=0&batchId=1&instanceId=0&page=%2Fvol%2Findex.do&scriptSessionId=o*ygDPpho6ORWkCO1ve8EDGao1l/3ocIo1l-VrlGaOSP6"
    payload = "cdgoOrigen=%s&cdgoDestino=%s&tipoBusqueda=autocomplete&desOrigen=%s&desDestino=%s&ninos=0&currenLocation=menuBusqueda&operation=&grupos=false&tipoOperacion=IND&empresas=false&getTarifasSesion=false&adultos=1&actTipoViajero=true&IdOrigen=%s&IdDestino=%s&FechaIdaSel=%s&HoraIdaSel=00%%3A00&FechaVueltaSel=&HoraVueltaSel=00%%3A00&adultos_=1&ninos_=0&ninosMenores=0&codPromocional=&txtoUsuario=&txtoPass="

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
    estaciones = session.post('https://venta.renfe.com/vol/dwr/call/plaincall/estacionesManager.getEstacionesIntAuto.dwr', data=estaciones_payload, headers=headers).text
    tuplas = re.findall('c:"([0-9nul]+,[0-9nul]+,[0-9nul]+)"|,d:"([A-z \(\*\)\.\'/\-0-9]+)"', estaciones)
    station_codes = dict()
    for tupla in tuplas:
        if tupla[0].count('') > 1:
            has_code = True
            code = tupla[0].encode('utf-8').replace(',', '%2C')
            continue
        elif has_code:
            name = tupla[1].encode('utf-8').replace('\u00F1', 'ñ')
        station_codes.update({name:code})
        has_code = False

    session.get(urlbase)
    if origin in station_codes and dest in station_codes:
        payload = payload % (station_codes[origin], station_codes[dest], origin.replace(' ', '+'), dest.replace(' ', '+'), origin.replace(' ', '+'), dest.replace(' ', '+'), date)
    else:
        print "Almost one station doesn't exists."
    response = session.post(url, data=payload, headers=headers).text
    if "Se ha producido un error" in response:
        print response
        print "Error"
    elif "AVE" in response:
        res = bs(response, 'html.parser')
        tabla = '<meta charset="UTF-8">' + res.html.body.table
        print "Buy your ticket"

    #Send mail with the table

if __name__ == "__main__":
    check_renfe_date()
