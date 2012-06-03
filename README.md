Supybot-Qstat
=============

Supybot plugin for qstat to display details from Quake serversThis plugin was inspired by pyqstat, which is a Python wrapper to QStat, the cli utility to query
Quake and other servers. I was going to port pyqstat directly but the wrapper was a bit complex
for the simple functionality needed.

First, you need to set the config.py variable to where qstat is located. Many distributions have
outdated versions, so grabbing their latest svn branch and compiling is best. 

The plugin executes qstat with -xml, parses, and outputs.

NOTES:

Needs some formatting on the output + options to display players.
