Passinga - Icinga 2 Passive Check Script
========================================

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
	verify_ssl: on
	hostname: dbhost.yourdomain.com


And capture your job status / output and push to Icinga in a passive check:


	BACKOUTPUT=$(/usr/bin/backupjob)
	BACKSTATUS=$?
	if [[ $BACKSTATUS -ne 0 ]]; then BACKSTATUS=1; fi

	passinga.py -n 'NinjaBackup' -o "$BACKOUTPUT" -s $BACKSTATUS
