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

Configure in /etc/passinga:

	[Main]
	icinga_url: https://icinga.yourdomain.com:5655
	username: icingaapi
	password: 3wdfkmslke
	# set to on if you trust the cert being presented
	verify_ssl: off
	hostname: dbhost.yourdomain.com

And capture your job status / output and push to Icinga in a passive check:

	BACKOUTPUT=$(/usr/bin/backupjob)
	BACKSTATUS=$?
	# set non-zero RC to Icinga WARNING (2 for CRITICAL)
	if [[ $BACKSTATUS -ne 0 ]]; then BACKSTATUS=1; fi

	passinga.py -n 'NinjaBackup' -o "$BACKOUTPUT" -s $BACKSTATUS


## Notes ##

* Pipe mode only works in Bash, you will need to specify shell in Debian/Ubuntu crontab as that defaults to dash ( https://wiki.ubuntu.com/DashAsBinSh#A.24PIPESTATUS ).
