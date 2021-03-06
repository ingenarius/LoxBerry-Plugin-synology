#!/bin/sh

# Bash script which is executed in case of an update (if this plugin is already
# installed on the system). This script is executed as very last step (*AFTER*
# postinstall) and can be for example used to save back or convert saved
# userfiles from /tmp back to the system. Use with caution and remember, that
# all systems may be different! Better to do this in your own Pluginscript if
# possible.
#
# Exit code must be 0 if executed successfull.
#
# Will be executed as user "loxberry".
#
# We add 5 arguments when executing the script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"

# To use important variables from command line use the following code:
ARGV0=$0 # Zero argument is shell command
echo "<INFO> ARGV0 - Command is: $ARGV0"

ARGV1=$1 # First argument is temp folder during install
echo "<INFO> ARGV1 - Temporary folder is: $ARGV1"

ARGV2=$2 # Second argument is Plugin-Name for scipts etc.
echo "<INFO> ARGV2 - (Short) Name is: $ARGV2"

ARGV3=$3 # Third argument is Plugin installation folder
echo "<INFO> ARGV3 - Installation folder is: $ARGV3"

ARGV4=$4 # Forth argument is Plugin version
echo "<INFO> ARGV4 - Installation folder is: $ARGV4"

ARGV5=$5 # Fifth argument is Base folder of LoxBerry
echo "<INFO> ARGV5 - Base folder is: $ARGV5"

echo "<INFO> replacing folder strings in daemon script"
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/system/daemons/plugins/$ARGV2
/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/system/daemons/plugins/$ARGV2

echo "<INFO> replacing folder strings in cron script"
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/system/cron/cron.10min/$ARGV2
/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/system/cron/cron.10min/$ARGV2
/bin/sed -i "s#REPLACEBYSUBFOLDER#$ARGV3#" $ARGV5/system/cron/cron.daily/$ARGV2
/bin/sed -i "s#REPLACEBYBASEFOLDER#$ARGV5#" $ARGV5/system/cron/cron.daily/$ARGV2

echo "<INFO> Copy back existing config files"
cp -v -r /tmp/uploads/$ARGV1\_upgrade/config/$ARGV3/* $ARGV5/config/plugins/$ARGV3/ 
echo "<INFO> Copy back existing log files"
cp -v -r /tmp/uploads/$ARGV1\_upgrade/log/$ARGV3/* $ARGV5/log/plugins/$ARGV3/ 
echo "<INFO> Remove temporary folders"
rm -r /tmp/uploads/$ARGV1\_upgrade

echo "<INFO> start syno_plugin"
$ARGV5/system/daemons/plugins/$ARGV2 start

# Exit with Status 0
exit 0
