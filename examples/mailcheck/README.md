mailcheck
=========

Test mail relaying is working with the help of swaks & procmail (or any other mail delivery and program delivery method).


Setup
=====

1. Create an icinga passive check:

       apply Service "mail_relay_" for (mailrelay in host.vars.mailrelays) {
			max_check_attempts = 1
			check_interval = 7h
			vars.notification_interval = 8h

			enable_active_checks = true

			check_command = "dummy"
			vars.dummy_text = "No Passive Check Result Received"
			vars.dummy_state = "3"

			display_name = "Mail Relay (" + mailrelay + ")"

			assign where host.vars.mailrelays
       }

mailrelays is an array of email address (eg testmail@hotmail.com) you want to check aren't blacklisting you

2. Configure program delivery to trigger the passive check (see mailcheck.rc for procmail example)

3. Set up a rule on your destination mail host (eg Hotmail, Google) to automatically forward (to recipient in step 4) and delete the mail. Forwardee address should be different from original sender address or rule may not work (due to mail loop suspicion).

4. Set up a regular cron job to email the addresses with JPMAILCHECK in the subject (see mailcheck-send.sh).

