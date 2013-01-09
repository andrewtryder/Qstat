# Supybot-Qstat

Description

    Supybot plugin for qstat to display details from Quake servers.
    This plugin was inspired by pyqstat, which is a Python wrapper to QStat, the cli utility to query
    Quake and other servers. I was going to port pyqstat directly but the wrapper was a bit complex
    for the simple functionality needed.

Instructions
    
    First, you need to set the config.py variable to where qstat is located. This is critical.
    We do some checks to see if it works but debugging can be tricky.
    
    IMPORTANT: Many distributions, including my Debian and Ubuntu setups, have a "qstat" program
    that looks like the latest at 2.12. There have been minor changes over the years commited to the
    trunk version of qstat on their SVN repo @ SF. I cannot emphasize running this enough because
    they not only added in many newer games, including Urban Terror, which I use it for, but fixed
    some annoying bugs.
    
    You can grab it via: 
    
    svn co https://qstat.svn.sourceforge.net/svnroot/qstat/trunk/qstat2 qstat2
    
    Compile and install. 
    
    Once installed, you need to configure plugins.QStat.qstatPath /full/path/to/qstat/executable
