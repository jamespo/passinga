#!/usr/bin/env python3

# passinga - post passive check status to Icinga2
# (C) James Powell jamespo [at] gmail [dot] com 2022
# This software is licensed under the same terms as Python itself

# curl -k -s -S -i -u root:icinga -H 'Accept: application/json' \
#  -X POST 'https://localhost:5665/v1/actions/process-check-result' \
# -d '{ "type": "Service", "filter": "host.name==\"icinga2-master1.localdomain\" && service.name==\"passive-ping\"", "exit_status": 2, "plugin_output": "PING CRITICAL - Packet loss = 100%", "performance_data": [ "rta=5000.000000ms;3000.000000;5000.000000;0.000000", "pl=100%;80;100;0" ], "check_source": "example.localdomain", "pretty": true }'

# passinga git:(main) ✗ /usr/lib/monitoring-plugins/check_ping -H 1.1.1.1 -c 90%,95% -w 80%,90%
# PING OK - Packet loss = 0%, RTA = 42.87 ms|rta=42.874001ms;80.000000;90.000000;0.000000 pl=0%;80;90;0


import urllib3
import configparser as ConfigParser
import os.path
import os
from argparse import ArgumentParser
import logging
import socket
import sys
import json

logging.basicConfig()
logger = logging.getLogger()


def post_status(ic_url, user, pw, hostname, verify_ssl, checkargs):
    """posts icinga service check result to API and returns json"""
    url = ic_url + "/v1/actions/process-check-result"
    logger.debug("url: " + url)
    http = urllib3.PoolManager()
    headers = {
        "User-agent": "passinga",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    headers.update(urllib3.make_headers(basic_auth="%s:%s" % (user, pw)))
    postdata = json.dumps(
        {
            "type": "Service",
            "check_source": hostname,
            "filter": 'host.name=="%s" && service.name=="%s"'
            % (hostname, checkargs.checkname),
            "exit_status": checkargs.exitrc,
            "plugin_output": checkargs.exitoutput,
        }
    )
    logger.debug('Postdata: ' + postdata)
    logger.debug('Headers: ' + str(headers))
    resp = http.request("POST", url, headers=headers, body=postdata)
    logger.debug('Response: ' + str(resp.data))
    return resp.status, json.loads(resp.data)


def readconf():
    """read config file"""
    config = ConfigParser.ConfigParser()
    config.read(["/etc/passinga", os.path.expanduser("~/.config/.passinga")])
    logger.debug('Conf: ' + str(dict(config.items('Main'))))
    return (
        config.get("Main", "icinga_url"),
        config.get("Main", "username"),
        config.get("Main", "password"),
        config.get("Main", "hostname")
        if config.has_option("Main", "hostname")
        else socket.gethostname(),
        config.getboolean("Main", "verify_ssl")
        if config.has_option("Main", "verify_ssl")
        else True,
    )


def get_options():
    """return CLI options"""
    parser = ArgumentParser()
    parser.add_argument("-s", "--exitrc", help="Icinga exit rc (0-3)", dest="exitrc")
    parser.add_argument("-n", "--checkname", help="Name of check", dest="checkname")
    parser.add_argument(
        "-o", "--exitoutput", help="exit output", dest="exitoutput", default=""
    )
    args = parser.parse_args()
    return args


def main():
    if os.getenv("PASSDEBUG"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    checkargs = get_options()
    (icinga_url, username, password, hostname, verify_ssl) = readconf()
    status, response = post_status(icinga_url, username, password, hostname, verify_ssl, checkargs)
    logger.debug("Status: %s   Response: %s" % (status, response))
    errstr = ''
    if status == 200:
        if "Successfully processed check result" in response["results"][0]["status"]:
            rc = 0
        else:
            rc = 1
            errstr = response["results"][0]["status"]
    else:
        rc = 1
    if rc == 1:
        print("Error: (%s) %s" % (status, errstr), file = sys.stderr)
    sys.exit(rc)


if __name__ == "__main__":
    main()
