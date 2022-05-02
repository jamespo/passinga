#!/usr/bin/env python3

# passinga - post passive check status to Icinga2
# (C) James Powell jamespo [at] gmail [dot] com 2022
# This software is licensed under the same terms as Python itself

# curl -k -s -S -i -u root:icinga -H 'Accept: application/json' \
#  -X POST 'https://localhost:5665/v1/actions/process-check-result' \
# -d '{ "type": "Service", "filter": "host.name==\"icinga2-master1.localdomain\" && service.name==\"passive-ping\"", "exit_status": 2, "plugin_output": "PING CRITICAL - Packet loss = 100%", "performance_data": [ "rta=5000.000000ms;3000.000000;5000.000000;0.000000", "pl=100%;80;100;0" ], "check_source": "example.localdomain", "pretty": true }'

import urllib3
import configparser as ConfigParser
import os.path
import os
from optparse import OptionParser
import logging
import socket
import sys
import json

logging.basicConfig()
logger = logging.getLogger()


def post_status(ic_url, user, pw, hostname, verify_ssl, checkopts):
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
            % (hostname, checkopts.checkname),
            "exit_status": checkopts.exitrc,
            "plugin_output": checkopts.exitoutput,
        }
    )
    logger.debug(postdata)
    logger.debug(headers)
    resp = http.request("POST", url, headers=headers, body=postdata)
    logger.debug(resp.data)
    return resp.data


def readconf():
    """read config file"""
    config = ConfigParser.ConfigParser()
    config.read(["/etc/passinga", os.path.expanduser("~/.config/.passinga")])
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
    parser = OptionParser()
    parser.add_option("-s", "--exitrc", help="Icinga exit rc (0-3)", dest="exitrc")
    parser.add_option("-n", "--checkname", help="Name of check", dest="checkname")
    parser.add_option(
        "-o", "--exitoutput", help="exit output", dest="exitoutput", default=""
    )
    opts, args = parser.parse_args()
    return opts


def main():
    if os.getenv("PASSDEBUG"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    checkopts = get_options()
    (icinga_url, username, password, hostname, verify_ssl) = readconf()
    data = post_status(icinga_url, username, password, hostname, verify_ssl, checkopts)
    rc = 0
    sys.exit(rc)


if __name__ == "__main__":
    main()
