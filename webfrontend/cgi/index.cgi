#!/usr/bin/perl

use File::HomeDir;
use CGI qw/:standard/;
use Config::Simple;
use Cwd 'abs_path';
use HTML::Entities;
use String::Escape qw( unquotemeta );
use JSON qw( decode_json );
use MIME::Base64 qw( encode_base64 );
use IO::Socket::INET;
use warnings;
use strict;
no strict "refs"; # we need it for template system

# ---------------------------------------
# Common variables
# ---------------------------------------
my  $cfg;
my  $conf;
my  $home = File::HomeDir->my_home;
my  $installfolder;
our $cache;
our $camcmd;
our $daemon_port;
our $do;
our $initial;
our $lang;
our $languagefile;
our $languagefileplugin;
our $local_daemon;
our $namef;
our $phrase;
our $phraseplugin;
our $psubfolder;
our $savedata;
our $template_title;
our $value;
our %query;
our @language_strings;
# ---------------------------------------
# DiskStation variables
# ---------------------------------------
our $cam_ids;
our $cids;
our $host;
our $notification;
our $port;
our $pwd;
our $stored_pwd;
our $username;
our @cameras;
# ---------------------------------------
# Notification variables
# ---------------------------------------
our $chat_ids;
our $email_pwd;
our $email_stored_pwd;
our $email_smtp;
our $email_smtp_port;
#our $email_use_tls;
our $email_user;
our $sent_via;
our $sent_via_list;
our $tbot_chat_id;
our $tbot_token;
# ---------------------------------------
# language variables
# ---------------------------------------
our $hlp_cam_list;
our $hlp_daemon;
our $hlp_email;
our $hlp_email_tls;
our $hlp_initial;
our $hlp_smtp_port;
our $hlp_star_mand;
our $hlp_udp_port;
our $hlp_user;
our $txt_cam_ids;
our $txt_chat_ids_avail;
our $txt_hide;
our $txt_installed_cams;
our $txt_lcl_server;
our $txt_logfile;
our $txt_no;
our $txt_none;
our $txt_pwd;
our $txt_save;
our $txt_send;
our $txt_settings;
our $txt_show;
our $txt_user;
our $txt_yes;


# ---------------------------------------
# Read Settings
# ---------------------------------------
$cfg             = new Config::Simple("$home/config/system/general.cfg");
$installfolder   = $cfg->param("BASE.INSTALLFOLDER");
$lang            = $cfg->param("BASE.LANG");

print "Content-Type: text/html\n\n";

# ---------------------------------------
# Parse URL
# ---------------------------------------
foreach (split(/&/,$ENV{"QUERY_STRING"}))
{
  ($namef,$value) = split(/=/,$_,2);
  $namef =~ tr/+/ /;
  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $query{$namef} = $value;
}

# ---------------------------------------
# Set parameters coming in - GET over POST
# ---------------------------------------
if ( !$query{'initial'} )   { 	if ( param('initial')  ) { $initial = quotemeta(param('initial')); } 
else { $initial = $initial; } } else { $initial = quotemeta($query{'initial'}); }

if ( !$query{'daemon_port'} )   { 	if ( param('daemon_port')  ) { $daemon_port = quotemeta(param('daemon_port')); } 
else { $daemon_port = $daemon_port; } } else { $daemon_port = quotemeta($query{'daemon_port'}); }

if ( !$query{'username'} )   { 	if ( param('username')  ) { $username = quotemeta(param('username')); } 
else { $username = $username; } } else { $username = quotemeta($query{'username'}); }

if ( !$query{'stored_pwd'} )   { if ( param('stored_pwd')  ) { $stored_pwd = param('stored_pwd'); } 
else { $stored_pwd = $stored_pwd;  } } else { $stored_pwd = $query{'stored_pwd'}; }

if ( !$query{'pwd'} )   { if ( param('pwd')  ) { $pwd = param('pwd'); } 
else { $pwd = $pwd;  } } else { $pwd = $query{'pwd'}; }

if ( !$query{'host'} )   { if ( param('host')  ) { $host = quotemeta(param('host')); } 
else { $host = $host;  } } else { $host = quotemeta($query{'host'}); }

if ( !$query{'port'} )   { if ( param('port')  ) { $port = quotemeta(param('port')); } 
else { $port = $port;  } } else { $port = quotemeta($query{'port'}); }	

if ( !$query{'notification'} )   { if ( param('notification')  ) { $notification = quotemeta(param('notification')); } 
else { $notification = $notification;  } } else { $notification = quotemeta($query{'notification'}); }	

if ( !$query{'cids'} )   { if ( param('cids')  ) { $cids = param('cids'); } 
else { $cids = $cids;  } } else { $cids = $query{'cids'}; }

if ( !$query{'sent_via'} )   { if ( param('sent_via')  ) { $sent_via = param('sent_via');         } 
else { $sent_via = $sent_via;  } } else { $sent_via = $query{'sent_via'};   }

if ( $sent_via eq "1" ) {
    if ( !$query{'tbot_token'} )   { if ( param('tbot_token')  ) { $tbot_token = quotemeta(param('tbot_token'));         } 
    else { $tbot_token = $tbot_token;  } } else { $tbot_token = quotemeta($query{'tbot_token'});   }

    if ( !$query{'tbot_chat_id'} )   { if ( param('tbot_chat_id')  ) { $tbot_chat_id = quotemeta(param('tbot_chat_id'));         } 
    else { $tbot_chat_id = $tbot_chat_id;  } } else { $tbot_chat_id = quotemeta($query{'tbot_chat_id'});   }
} 
if ( $sent_via eq "2" ) {
    if ( !$query{'email_smtp'} )   { if ( param('email_smtp')  ) { $email_smtp = quotemeta(param('email_smtp'));         } 
    else { $email_smtp = $email_smtp;  } } else { $email_smtp = quotemeta($query{'email_smtp'});   }

    if ( !$query{'email_smtp_port'} )   { if ( param('email_smtp_port')  ) { $email_smtp_port = quotemeta(param('email_smtp_port'));         } 
    else { $email_smtp_port = $email_smtp_port;  } } else { $email_smtp_port = quotemeta($query{'email_smtp_port'});   }

    #if ( !$query{'email_use_tls'} )   { if ( param('email_use_tls')  ) { $email_use_tls = quotemeta(param('email_use_tls'));         } 
    #else { $email_use_tls = $email_use_tls;  } } else { $email_use_tls = quotemeta($query{'email_use_tls'});   }

    if ( !$query{'email_user'} )   { if ( param('email_user')  ) { $email_user = quotemeta(param('email_user'));         } 
    else { $email_user = $email_user;  } } else { $email_user = quotemeta($query{'email_user'});   }

    if ( !$query{'email_stored_pwd'} )   { if ( param('email_stored_pwd')  ) { $email_stored_pwd = param('email_stored_pwd'); } 
    else { $email_stored_pwd = $email_stored_pwd;  } } else { $email_stored_pwd = $query{'email_stored_pwd'}; }

    if ( !$query{'email_pwd'} )   { if ( param('email_pwd')  ) { $email_pwd = param('email_pwd'); } 
    else { $email_pwd = $email_pwd;  } } else { $email_pwd = $query{'email_pwd'}; }
}



# ---------------------------------------
# Figure out in which subfolder we are installed
# ---------------------------------------
$psubfolder = abs_path($0);
$psubfolder =~ s/(.*)\/(.*)\/(.*)$/$2/g;


# ---------------------------------------
# Save settings to config file
# ---------------------------------------
if (param('savedata')) {
    $conf = new Config::Simple("$home/config/plugins/$psubfolder/plugin.cfg");
    
    $conf->param('SERVER.PORT', unquotemeta($daemon_port));
    $conf->param('SERVER.INITIAL', "0");
    $conf->param('DISKSTATION.USER', unquotemeta($username));
    if ($pwd eq "") { $conf->param('DISKSTATION.PWD', $stored_pwd); } else { $conf->param('DISKSTATION.PWD', encode_base64($pwd, '')); }
    $conf->param('DISKSTATION.HOST', unquotemeta($host));
    $conf->param('DISKSTATION.PORT', unquotemeta($port));
    $conf->param('DISKSTATION.NOTIFICATION', unquotemeta($notification));
    $conf->param('DISKSTATION.CIDS', '"'.$cids.'"');
    $conf->param('DISKSTATION.SENT_VIA', $sent_via);
    if ( $sent_via eq 1 ) { # Telegram
        $conf->param('TELEGRAM.TOKEN', unquotemeta($tbot_token));
        $conf->param('TELEGRAM.CHAT_ID', unquotemeta($tbot_chat_id));
    }
    elsif ( $sent_via eq 2 ) { # Email
        $conf->param('EMAIL.SMTP', unquotemeta($email_smtp));
        $conf->param('EMAIL.SMTP_PORT', unquotemeta($email_smtp_port));
        #$conf->param('EMAIL.USE_TLS', unquotemeta($email_use_tls));
        $conf->param('EMAIL.USER', unquotemeta($email_user));
        if ($email_pwd eq "") { $conf->param('EMAIL.PWD', $email_stored_pwd); } else { $conf->param('EMAIL.PWD', encode_base64($email_pwd, '')); }
    }
	else { # none
		$conf->param('TELEGRAM.TOKEN', '');
        $conf->param('TELEGRAM.CHAT_ID', '');
		$conf->param('EMAIL.SMTP', '');
        $conf->param('EMAIL.SMTP_PORT', '');
        #$conf->param('EMAIL.USE_TLS', '');
        $conf->param('EMAIL.USER', '');
		$conf->param('EMAIL.PWD', '');
	}
    
    $conf->save();
    
    # Actions will only be done, if the configuration changed at least once!
    if ($initial eq "0") {
        # RESTART syno_plugin.py
        # this is necessary to load the new configuration!
        system("$installfolder/system/daemons/plugins/$psubfolder restart");
        # check for installed cameras after config change
        $camcmd = 'python /opt/loxberry/webfrontend/cgi/plugins/synology/bin/cameras.py &';
        system($camcmd);
    }
}


# ---------------------------------------
# Parse config file
# ---------------------------------------
$conf = new Config::Simple("$home/config/plugins/$psubfolder/plugin.cfg");
$initial = encode_entities($conf->param('SERVER.INITIAL'));
$daemon_port = encode_entities($conf->param('SERVER.PORT'));
$username = encode_entities($conf->param('DISKSTATION.USER'));
$stored_pwd = encode_entities($conf->param('DISKSTATION.PWD'));
$host = encode_entities($conf->param('DISKSTATION.HOST'));
$port = encode_entities($conf->param('DISKSTATION.PORT'));
$notification = encode_entities($conf->param('DISKSTATION.NOTIFICATION'));
$cids = encode_entities($conf->param('DISKSTATION.CIDS'));
$sent_via = encode_entities($conf->param('DISKSTATION.SENT_VIA'));
$tbot_token = encode_entities($conf->param('TELEGRAM.TOKEN'));
$tbot_chat_id = encode_entities($conf->param('TELEGRAM.CHAT_ID'));
$email_smtp = encode_entities($conf->param('EMAIL.SMTP'));
$email_smtp_port = encode_entities($conf->param('EMAIL.SMTP_PORT'));
#$email_use_tls = encode_entities($conf->param('EMAIL.USE_TLS'));
$email_user = encode_entities($conf->param('EMAIL.USER'));
$email_stored_pwd = encode_entities($conf->param('EMAIL.PWD'));

# ---------------------------------------
# Init Language
# ---------------------------------------
# Clean up lang variable
$lang         =~ tr/a-z//cd; $lang         = substr($lang,0,2);
#If there's no language phrases file for choosed language, use german as default
if (!-e "$installfolder/templates/system/$lang/language.dat") {
    $lang = "en";
}
# Read translations / phrases
$languagefile           = "$installfolder/templates/system/$lang/language.dat";
$phrase                 = new Config::Simple($languagefile);
$languagefileplugin     = "$installfolder/templates/plugins/$psubfolder/$lang/language.dat";
$phraseplugin           = new Config::Simple($languagefileplugin);

# ---------------------------------------
# Fill language variables
# ---------------------------------------
$hlp_cam_list = $phraseplugin->param("HLP_CAM_LIST");
$hlp_daemon = $phraseplugin->param("HLP_DAEMON");
$hlp_email = $phraseplugin->param("HLP_EMAIL");
$hlp_email_tls = $phraseplugin->param("HLP_EMAIL_TLS");
$hlp_initial = $phraseplugin->param("HLP_INITIAL");
$hlp_smtp_port = $phraseplugin->param("HLP_SMTP_PORT");
$hlp_star_mand = $phraseplugin->param("HLP_STAR_MAND");
$hlp_udp_port = $phraseplugin->param("HLP_UDP_PORT");
$hlp_user = $phraseplugin->param("HLP_USER");
$txt_cam_ids = $phraseplugin->param("TXT_CAM_IDS");
$txt_chat_ids_avail = $phraseplugin->param("TXT_CHAT_IDS_AVAIL");
$txt_hide = $phraseplugin->param("TXT_HIDE");
$txt_installed_cams = $phraseplugin->param("TXT_INSTALLED_CAMS");
$txt_lcl_server = $phraseplugin->param("TXT_LCL_SERVER");
$txt_logfile = $phraseplugin->param("TXT_LOGFILE");
$txt_pwd = $phraseplugin->param("TXT_PWD");
$txt_no = $phraseplugin->param("TXT_NO");
$txt_none = $phraseplugin->param("TXT_NONE");
$txt_save = $phraseplugin->param("TXT_SAVE");
$txt_send = $phraseplugin->param("TXT_SEND");
$txt_settings = $phraseplugin->param("TXT_SETTINGS");
$txt_show = $phraseplugin->param("TXT_SHOW");
$txt_user = $phraseplugin->param("TXT_USER");
$txt_yes = $phraseplugin->param("TXT_YES");

# ---------------------------------------
# Daemon tools
# ---------------------------------------
if ( param('do') ) { 
    $do = quotemeta( param('do') ); 
    if ( $do eq "email") {
        my $sock = new IO::Socket::INET(PeerAddr => '127.0.0.1',
                PeerPort => $daemon_port,
                Proto => 'udp', Timeout => 1) or die('Error opening socket.');
        my $data = "TestMail";
        send($sock, $data, 0);
        exit;
    }
}

# Title
$template_title = $phrase->param("TXT0000") . ": Synology";

# ---------------------------------------
# Load header and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
# ---------------------------------------
open(F,"$installfolder/templates/system/$lang/header.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# ---------------------------------------
# check for lock folder -> running/stopped
# ---------------------------------------
if ( -f "/tmp/syno_plugin.lock" ) { $local_daemon = $phraseplugin->param("TXT_RUNNING"); }
else { $local_daemon = $phraseplugin->param("TXT_NOT_RUNNING"); }

# ---------------------------------------
# Get installed cameras
# ---------------------------------------
@cameras = `cat $installfolder/data/plugins/$psubfolder/cameras.dat`;
foreach (@cameras) {
    $cam_ids .= "$_<br>";
}

# ---------------------------------------
# Fill SENT_VIA selection dropdown
# ---------------------------------------
for (my $i = 0; $i <= 2;$i++) {
	if ($i eq $sent_via) {
        if ($i eq 1) { $sent_via_list .= '<option selected value="'.$i.'">Telegram Bot</option>\n'; }
        elsif ($i eq 2) { $sent_via_list .= '<option selected value="'.$i.'">Email</option>\n'; }
        else { $sent_via_list .= '<option selected value="0">'.$txt_none.'</option>\n'; }
        } else {
        if ($i eq 1) { $sent_via_list .= '<option value="'.$i.'">Telegram Bot</option>\n'; }
        elsif ($i eq 2) { $sent_via_list .= '<option value="'.$i.'">Email</option>\n'; }
        else { $sent_via_list .= '<option value="0">'.$txt_none.'</option>\n'; }
    }
}


# ---------------------------------------
# Load content from template
# ---------------------------------------
open(F,"$installfolder/templates/plugins/$psubfolder/$lang/settings.html") || die "Missing template plugins/$psubfolder/$lang/settings.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# ---------------------------------------
# Load footer and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
# ---------------------------------------
open(F,"$installfolder/templates/system/$lang/footer.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

exit;
