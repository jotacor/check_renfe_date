#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: https://github.com/jotacor
# Web: jotacor.com
# Version: 1.0

from bs4 import BeautifulSoup as bs
import ConfigParser
import mandrill
import re
import requests

Config = ConfigParser.ConfigParser()
Config.read('data.conf')


def get_station_codes(session, headers):
    stations_payload = "callCount=1&windowName=&c0-scriptName=estacionesManager&c0-methodName=getEstacionesIntAuto&c0-id=0&batchId=1&instanceId=0&page=%2Fvol%2Findex.do&scriptSessionId=o*ygDPpho6ORWkCO1ve8EDGao1l/3ocIo1l-VrlGaOSP6"
    stations = session.post('https://venta.renfe.com/vol/dwr/call/plaincall/estacionesManager.getEstacionesIntAuto.dwr', data=stations_payload, headers=headers).text
    tuples = re.findall('c:"([0-9nul]+,[0-9nul]+,[0-9nul]+)"|,d:"([A-z \(\*\)\.\'/\-0-9]+)"', stations)
    station_codes = dict()

    for tupl in tuples:
        if tupl[0].count('') > 1:
            has_code = True
            code = tupl[0].encode('utf-8').replace(',', '%2C')
            continue
        elif has_code:
            name = tupl[1].encode('utf-8').replace('\u00F1', 'ñ')
        station_codes.update({name: code})
        has_code = False

    return station_codes


def send_mail(subject, content, email_destination, mandrill_key):
    mandrill_client = mandrill.Mandrill(mandrill_key)
    message = {'html': content,
               'subject': subject,
               'from_email': 'jotacor@jotacor.com',
               'from_name': 'Check Renfe Date',
               'to': [{'email': email_destination,
                       'type': 'to'}],
               }
    return mandrill_client.messages.send(message=message, async=False, ip_pool='', send_at='')


def check_renfe_date():
    urlbase = 'https://venta.renfe.com/vol/index.do'
    url = 'https://venta.renfe.com/vol/buscarTren.do'
    origin = Config.get('renfe', 'origin')
    dest = Config.get('renfe', 'dest')
    date = Config.get('renfe', 'date')
    mandrill_key = Config.get('renfe', 'mandrill_key')
    email_destination = Config.get('renfe', 'email_destination')
    payload = "cdgoOrigen=%s&cdgoDestino=%s&tipoBusqueda=autocomplete&desOrigen=%s&desDestino=%s&ninos=0&currenLocation=menuBusqueda&operation=&grupos=false&tipoOperacion=IND&empresas=false&getTarifasSesion=false&adultos=1&actTipoViajero=true&IdOrigen=%s&IdDestino=%s&FechaIdaSel=%s&HoraIdaSel=00%%3A00&FechaVueltaSel=&HoraVueltaSel=00%%3A00&adultos_=1&ninos_=0&ninosMenores=0&codPromocional=&txtoUsuario=&txtoPass="
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8,en;q=0.6', 'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'venta.renfe.com', 'Origin': 'https://venta.renfe.com', 'Pragma': 'no-cache', 'Referer': 'https://venta.renfe.com/vol/inicioCompra.do', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

    session = requests.Session()
    station_codes = get_station_codes(session, headers)

    session.get(urlbase)
    if origin not in station_codes or dest not in station_codes:
        print "Almost one station does not exists."
        exit(1)

    payload = payload % (station_codes[origin], station_codes[dest], origin.replace(' ', '+'), dest.replace(' ', '+'), origin.replace(' ', '+'), dest.replace(' ', '+'), date.replace('-', '%2F'))
    response = session.post(url, data=payload, headers=headers).text
    res = bs(response, 'html.parser')
    if "Se ha producido un error" in response:
        print response
        print "Error"
        exit(1)
    elif res.html.body.table is None:
        print "There is no AVE for that date."
        exit(1)
    elif "AVE" in response:
        table = '<meta charset="UTF-8">' + str(res.html.body.table)
        try:
            subject = 'Train from %s to %s on date %s available.' % (origin, dest, date)
            print send_mail(subject, table, email_destination, mandrill_key)
        except mandrill.Error, e:
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            raise

if __name__ == "__main__":
    check_renfe_date()
