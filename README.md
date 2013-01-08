# Supybot-Qstat

Description

    Supybot plugin for qstat to display details from Quake servers.
    This plugin was inspired by pyqstat, which is a Python wrapper to QStat, the cli utility to query
    Quake and other servers. I was going to port pyqstat directly but the wrapper was a bit complex
    for the simple functionality needed.

Instructions
    
    First, you need to set the config.py variable to where qstat is located.
    Many distributions have outdated versions, years old, so grabbing their latest svn branch and compiling is best. 
    
    You can grab it via: 
    
    https://qstat.svn.sourceforge.net/svnroot/qstat/trunk/qstat2
    
    Compile and install (beyond the scope of these instructions and document)
    
    Once installed, you need to configure plugins.QStat.qstatPath /full/path/to/qstat/executable
