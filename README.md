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
