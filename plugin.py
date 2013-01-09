###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

# my libs
import os
import subprocess
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('QStat')

@internationalizeDocstring
class QStat(callbacks.Plugin):
    """Add the help for "@plugin help QStat" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def __init__(self, irc):
        self.__parent = super(QStat, self)
        self.__parent.__init__(irc)
        self.qstatpath = self.registryValue('qstatPath')
    
    def _qstatgames(self, optgame):
        """Check for valid games."""
        qstatgames = ['a2s','ams','bfbc2','bfs','cod2m','cod2s','cod4m','cod4s','codm','cods','crs','crysis','cube2',
        'd3g','d3m','d3p','d3s','dm3m','dm3s','efm','efs','etqws','eye','fcs','fls','gps','grs','gs2','gs3',
        'gs4','gsm','h2s','hazes','hl2s','hla2s','hla2sm','hlm','hlqs','hls','hrs','hwm','hws','iourtm','iourts',
        'jk3m','jk3s','kps','maqs','mas','mhs','mumble','netp','netpm','nexuizm','nexuizs','openarenam','openarenas',
        'ottdm','ottds','preym','preys','prs','q2m','q2s','q3m','q3s','q4m','q4s','qs','qwm','qws','rss','rwm','rws',
        'sas','sfs','sgs','sms','sns','sof2m','sof2m1.0','sof2s','stm','stma2s','stmhl2','t2m','t2s','tbm','tbs','tee',
        'terraria','tm','tremulous','tremulousm','ts2','ts3','uns','ut2004m','ut2004s','ut2s','ut3s','ventrilo','warsowm',
        'warsows','waws','wics','woetm','woets','wolfs']
        if optgame in qstatgames:
            return True
        else:
            return False
         
    def verify(self, irc, msg, args):
        verification = self._verify()
        irc.reply(str(verification))
    verify = wrap(verify)

    def statMaster(self, type, name, gametype, port=None):
        """invoke qstat against a specified master server."""
        if port is None:
            address = name
        else:
            address = '%s:%d' % (name, port)
        #-sort		sort servers and/or players
        #-u		only display servers that are up
        #-nf		do not display full servers
        #-ne		do not display empty servers
        #-nh		do not display header line.        
        self.log.info("Getting server list.")
        pipe = os.popen("%s -xml -%s,game=%s,status=notempty %s 2> /dev/null" % (self.path, type, gametype, address))
        try:
            return self.populate_master(pipe)
        finally:
            pipe.close()
        
    def _verify(self):
        """Verify that the application is accessible and works."""
        if not os.path.isfile(self.qstatpath) and not os.access(self.qstatpath, os.X_OK):
            self.log.info("ERROR: {0} either not found or not executable".format(self.qstatpath))
            return False
        else:
            return True
    
    def _qstat(self, opttype, optserver, optport=None):
        """invoke qstat against a specified server."""
        # handle server or server:port
        if optport is None:
            address = optserver
        else:
            address = '%s:%d' % (optserver, optport)
        # work with type
        opttype = '-'+opttype
        
        # build the command.
        command = [self.qstatpath,'-utf8','-xml','-timeout','10',opttype,address,'-P','-R']
        
        # try to execute.
        try:
            proc = subprocess.Popen(command,shell=False,close_fds=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        except OSError, e:
            self.log.error("Process error: %s" % e)
            return None
        
        # process the output.
        proc.wait()
        if proc.returncode is not 0:
            self.log.error("Process error: return code %s - output: %s" % (proc.stderr.readline().strip(),proc.returncode))
            return None
        else:
            out = proc.communicate()[0]
            lines = filter(None, out.splitlines())
            if lines[0] != '<?xml version="1.0" encoding="UTF-8"?>':
                self.log.error("I did not find the XML header I needed. Output: %s" % out)
                return None
            else:
                return out.strip()

    def qstat(self, irc, msg, args, optlist, opttype, optserver):
        """[--players] <server type> <server name>
        Use qstat to query a server type.
        """

        # first, check if qstat works.
        if not self._verify():
            irc.reply("I cannot execute qstat. Please check the qstatPath config variable.")
            return

        # arguments for output.
        args = {'showPlayers':False,'showRules':False}
        
        # handle optlist (getopts)
        if optlist:
            for (key, value) in optlist:
                if key == 'players':
                    args['showPlayers'] = True
                if key == 'rules':
                    args['showRules'] = True

        # execute qstat and process XML.
        qstatxml = self._qstat(opttype, optserver)
        if qstatxml is None:
            irc.reply("ERROR trying to query: %s. Check the logs" % optserver)
            return
            
        root = ElementTree.fromstring(qstatxml)
        if root.tag != "qstat":
            irc.reply("Something went horribly wrong running qstat.")
            return
        
        # setup output for the basics.
        output = {}
        output['servertype'] = root.find('server').get('type')
        output['serverstatus'] = root.find('server').get('status')
        output['serveraddress'] = root.find('server').get('address')

        # first do some checking if we're down since the rest of the xml won't be there.            
        if output['serverstatus'] == "DOWN":
            irc.reply("ERROR: {0} appears to be down.".format(output['serveraddress']))
            return
        elif output['serverstatus'] == "ERROR":
            irc.reply("ERROR trying to query {0}: {1}".format(output['serveraddress'],output['error']))
            return

        # rest of the dicts for output.
        players = {}
        rules = {}
        # iterate through the rest.
        for child in root.find('server'):
            if child.tag == "players": # handle players.
                for childchildren in child.getchildren():
                    tmpdict = {}
                    tmpdict['name'] = ircutils.bold(childchildren.find('name').text)
                    tmpdict['score'] = int(childchildren.find('score').text)
                    tmpdict['ping'] = childchildren.find('ping').text
                    players[tmpdict['score']] = tmpdict
            elif child.tag == "rules": # handle rules
                for childchildren in child.getchildren():
                    rules[childchildren.get('name')] = childchildren.text
            else:
                output[child.tag] = child.text

        output['playerperc'] = "{0:.1f}%".format((float(output['numplayers'])/float(output['maxplayers'])) * 100)

        # now, lets actually output.
        irc.reply("Server: {0}({1})  Name: {2}  Map: {3}  Players: {4}/{5} ({6})  Ping: {7}ms".format(output['hostname'],\
            output['gametype'],output['name'],output['map'],output['numplayers'],output['maxplayers'],output['playerperc'],output['ping']))
        if args['showPlayers']:
            playerlist = [v['name']+"("+str(k)+")" for (k,v) in sorted(players.iteritems(),key=players.get('score'),reverse=True)]
            irc.reply("Players({0}) :: {1}".format(len(players)," | ".join(playerlist)))
        if args['showRules']:
            irc.reply(str(rules))

    qstat = wrap(qstat, [getopts({'players':'','rules':''}), ('somethingWithoutSpaces'), ('somethingWithoutSpaces')])

Class = QStat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=270:
