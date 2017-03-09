#!/usr/bin/perl

# This is a sample Script file
# It does not much:
#   * Loading configuration
#   * including header.htmlfooter.html
#   * and showing a message to the user.
# That's all.

use File::HomeDir;
use CGI qw/:standard/;
use Config::Simple;
use Cwd 'abs_path';
use IO::Socket::INET;
use HTML::Entities;
use String::Escape qw( unquotemeta );
use JSON qw( decode_json );
use warnings;
use strict;
no strict "refs"; # we need it for template system

my  $home = File::HomeDir->my_home;
our $lang;
my  $installfolder;
my  $cfg;
my  $conf;
our $psubfolder;
our $template_title;
our $namef;
our $value;
our %query;
our $phrase;
our $phraseplugin;
our $languagefile;
our $languagefileplugin;
our @language_strings;
our $cache;
our $savedata;
our $LOGFILE;
our $line;
our $backlink;


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
# Figure out in which subfolder we are installed
# ---------------------------------------
$psubfolder = abs_path($0);
$psubfolder =~ s/(.*)\/(.*)\/(.*)$/$2/g;


# Init Language
	# Clean up lang variable
	$lang         =~ tr/a-z//cd; $lang         = substr($lang,0,2);
  # If there's no language phrases file for choosed language, use german as default
		if (!-e "$installfolder/templates/system/$lang/language.dat") 
		{
  		$lang = "de";
	}
	# Read translations / phrases
		$languagefile 			= "$installfolder/templates/system/$lang/language.dat";
		$phrase 				= new Config::Simple($languagefile);
		$languagefileplugin 	= "$installfolder/templates/plugins/$psubfolder/$lang/language.dat";
		$phraseplugin 			= new Config::Simple($languagefileplugin);


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
# Load log file
# ---------------------------------------
$LOGFILE = "$installfolder/log/plugins/$psubfolder/synology.log";
open(LOGFILE) or die("Could not open log file.");
foreach $line (<LOGFILE>) {
    chomp($line);              # remove the newline from $line.
    print "<div>"; 
    print $line;
    print "</div>";
    # do line-by-line processing.
}

$backlink = "/admin/plugins/$psubfolder/index.cgi";
print "<div><a href=\"" . $backlink . "\">back</a></div>";

# ---------------------------------------
# Load content from template
# ---------------------------------------
#open(F,"$installfolder/templates/plugins/$psubfolder/$lang/log.html") || die "Missing template plugins/$psubfolder/$lang/log.html";
#  while (<F>) {
#    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
#    print $_;
#  }
#close(F);

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
