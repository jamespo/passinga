Passinga - Icinga 2 Passive Check Script
========================================

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

### cli mode ###

This is the default mode.

Capture your job status / output and push to Icinga in a passive check:

	BACKOUTPUT=$(/usr/bin/backupjob)
	BACKSTATUS=$?
	# set non-zero RC to Icinga WARNING (2 for CRITICAL)
	if [[ $BACKSTATUS -ne 0 ]]; then BACKSTATUS=1; fi

	passinga.py -n 'NinjaBackup' -o "$BACKOUTPUT" -s $BACKSTATUS -f 1

Note the "-f 1" flag - this "fixes" the returncode so that any code != 0 sets an Icinga RC of 1 (WARNING).


### stdin mode ###

This can be used in a one-liner to push the status of standard Icinga checks.

    check_ping -H 2.2.2.2 -w 80,90% -c 90,100% | tee | passinga.py --mode stdin -s ${PIPESTATUS[0]} -n Ping

(Intermediate tee step required to correctly capture returncode).

stdin mode with PIPESTATUS special variable only works in Bash (or zsh with changes), you will need to specify shell in Debian/Ubuntu crontab as that defaults to dash ( https://wiki.ubuntu.com/DashAsBinSh#A.24PIPESTATUS ).
