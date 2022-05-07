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
from argparse import ArgumentParser, Namespace
import logging
import socket
import sys
import json

logging.basicConfig()
logger = logging.getLogger()


def post_status(conf: dict, cliargs: Namespace) -> tuple:
    """posts icinga service check result to API and returns json"""
    url = conf['url'] + "/v1/actions/process-check-result"
    logger.debug("url: " + conf['url'])
    if not conf['v_ssl']:
        urllib3.disable_warnings()  # don't verify ssl
    http = urllib3.PoolManager()
    headers = {
        "User-agent": "passinga",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    headers.update(urllib3.make_headers(basic_auth="%s:%s" % (conf['user'],
                                                              conf['pw'])))
    # TODO: set perfdata if available
    postdata = json.dumps(
        {
            "type": "Service",
            "check_source": conf['host'],
            "filter": 'host.name=="%s" && service.name=="%s"'
            % (conf['host'], cliargs.checkname),
            "exit_status": cliargs.exitrc,
            "plugin_output": cliargs.exitoutput,
        }
    )
    logger.debug('Postdata: ' + postdata)
    logger.debug('Headers: ' + str(headers))
    resp = http.request("POST", url, headers=headers, body=postdata)
    logger.debug('Response: ' + str(resp.data))
    return resp.status, json.loads(resp.data)


def readconf() -> dict:
    """read config file"""
    config = ConfigParser.ConfigParser()
    config.read(["/etc/passinga", os.path.expanduser("~/.config/.passinga")])
    logger.debug('Conf: ' + str(dict(config.items('Main'))))
    mainconf = config['Main']
    return {
        'url': mainconf.get("icinga_url"),
        'user': mainconf.get("username"),
        'pw': mainconf.get("password"),
        'host': mainconf.get("hostname", socket.gethostname()),
        'v_ssl': mainconf.getboolean("verify_ssl", True)
    }


def get_options() -> Namespace:
    """return CLI options"""
    parser = ArgumentParser()
    parser.add_argument("-s", "--exitrc", help="Icinga exit rc (0-3)",
                        dest="exitrc", type=int, choices=range(4))
    parser.add_argument("-n", "--checkname", help="Name of check", dest="checkname")
    parser.add_argument(
        "-o", "--exitoutput", help="exit output", dest="exitoutput", default=""
    )
    parser.add_argument("-m", "--mode", choices=['stdin', 'ansible', 'cli'],
                        default="cli")
    parser.add_argument("-f", "--fixrc", help="if exitrc non-zero value to send (1-3)",
                        dest="fixrc", type=int, choices=range(1, 4))
    args = parser.parse_args()
    logger.debug('args: ' + str(args))
    return args


def main():
    """get conf & checkresults & post to Icinga"""
    cliargs = get_options()
    conf = readconf()
    if cliargs.fixrc and cliargs.exitrc != 0:
        cliargs.exitrc = cliargs.fixrc
    if cliargs.mode == 'stdin':
        # get exitoutput from stdin
        cliargs.exitoutput = sys.stdin.read()
    status, response = post_status(conf, cliargs)
    logger.debug("Status: %s   Response: %s" % (status, response))
    errstr = ''
    rc = 1
    if status == 200:
        if "Successfully processed check result" in response["results"][0]["status"]:
            rc = 0
        else:
            errstr = response["results"][0]["status"]
    if rc == 1:
        print("Error: (%s) %s" % (status, errstr), file=sys.stderr)
    sys.exit(rc)


if __name__ == "__main__":
    """set loglevel & call main"""
    if os.getenv("PASSDEBUG"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    main()
