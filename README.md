Passinga - Icinga 2 Passive Check Script
========================================

## Install ##

Copy passinga.py into your path.

Requirements: Python 3.6+ & [urllib3](https://pypi.org/project/urllib3/) module.

## Setup ##

Create an API user just with perms to push check results:

	object ApiUser "icingaapi" {
	   password = "3wdfkmslke"
	   permissions = [ "actions/process-check-result" ]
	}

Create a passive service in Icinga conf:

	apply Service "NinjaBackup" {
			max_check_attempts = 1
			retry_interval = 5m
			check_interval = 5m

			enable_active_checks = false

			check_command = "dummy"
			vars.dummy_text = "No Passive Check Result Received"
			vars.dummy_state = "3"

			assign where host.vars.config.backuphost
	}

Pick it up in a host definition:

    // dbhost.yourdomain.com
    vars.config.backuphost = "1"

Configure in /etc/passinga or ~/.config/.passinga:

	[Main]
	icinga_url: https://icinga.yourdomain.com:5655
	username: icingaapi
	password: 3wdfkmslke
	# set to on if you trust the cert being presented
	verify_ssl: off
	# this must match with the host configured for the check in Icinga
	hostname: dbhost.yourdomain.com


## Usage ##

	usage: passinga.py [-h] [-s {0,1,2,3}] [-n CHECKNAME] [-o EXITOUTPUT] [-m {stdin,ansible,cli}] [-f {1,2,3}]
	
	options:
	  -h, --help            show this help message and exit
	  -s EXITRC, --exitrc EXITRC
	                        parent rc to pass in
	  -n CHECKNAME, --checkname CHECKNAME
	                        Name of check
	  -o EXITOUTPUT, --exitoutput EXITOUTPUT
	                        exit output
	  -m {stdin,ansible,cli}, --mode {stdin,ansible,cli}
	  -f {1,2,3}, --fixrc {1,2,3}
	                        if exitrc non-zero value to send (1-3)
	

### cli mode ###

This is the default mode.

Capture your job status / output and push to Icinga in a passive check:

	BACKOUTPUT=$(/usr/bin/backupjob)
	BACKSTATUS=$?
	passinga.py -n 'NinjaBackup' -o "$BACKOUTPUT" -s $BACKSTATUS -f 1

Note the "-f 1" flag - this "fixes" the returncode so that any code != 0 sets an Icinga RC of 1 (WARNING).


### stdin mode ###

This can be used to push the status of standard Icinga checks.

    PINGSTATUS=$(mktemp)
    check_ping -H 2.2.2.2 -w 80,90% -c 90,100% > $PINGSTATUS
    cat $PINGSTATUS | passinga.py --mode stdin -s $? -n Ping
    rm $PINGSTATUS

Intermediate step required to capture $?

### ansible mode ###

Parse the results of ansible playbooks and push to icinga:

    ANSIBLE_CALLBACKS_ENABLED=json ANSIBLE_STDOUT_CALLBACK=json ansible-playbook mwsync.yml \
        | tee | passinga.py --mode ansible -n "MediaWiki Sync"
        
A helper script "icansirun" is included suitable for cron etc which you can use as below:

    CHECKNAME=backup ANSIBLE_CONFIG=/home/ansiman/conf/ansible.cfg icansirun playbook.yml



