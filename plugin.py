###
# Copyright (c) 2012-2014, spline
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

    def _qstatmasters(self, game=None):
        qstatmasters = {
            'cod2m':'Call of Duty 2 Master server','cod4m':'Call of Duty 4 Master server',
            'codm':'Call of Duty Master server','d3m':'Descent3 Master (PXO) server',
            'dm3m':'Doom 3 Master server','gsm':'Gamespy Master server',
            'hla2sm':'Steam Master server','hlm':'Half-Life Master server',
            'hwm':'HexenWorld Master server','iourtm':'ioUrbanTerror Master server',
            'netpm':'NetPanzer Master server','nexuizm':'Nexuiz Master server',
            'openarenam':'OpenArena Master server','ottdm':'openTTD Master server',
            'preym':'Prey Master server','q2m':'Quake II Master server',
            'q3m':'Quake III Master server','q4m':'Quake 4 Master server',
            'qwm':'QuakeWorld Master server','rwm':'Return to Castle Wolfenstein Master server',
            'sof2m':'SOF2 Master server','sof2m1.0':'SOF2 Master (1.0) server',
            'stm':'Steam Master server','stma2s':'Steam Master for A2S server',
            'stmhl2':'Steam Master for HL2 server','t2m':'Tribes 2 Master server',
            'tbm':'Tribes Master server','ut2004m':'UT2004 Master server',
            'warsowm':'Warsow Master server','woetm':'Enemy Territory Master server' }
        if not game:
            return qstatmasters
        elif game in qstatmasters:
            return True
        else:
            return False
            
    def _qstatgames(self, game=None):
        qstatgames = {
            'a2s':'Half-Life 2 new server','ams':"America's Army v2.x server",
            'bfbc2':'Battlefield Bad Company 2 server','bfs':'BFRIS server',
            'cod2s':'Call of Duty 2 server','cod4s':'Call of Duty 4 server',
            'cods':'Call of Duty server','crs':'Command and Conquer: Renegade server',
            'crysis':'Crysis server','cubes':'Sauerbraten server',
            'd3g':'Descent3 Gamespy Protocol server','d3p':'Descent3 PXO protocol server',
            'd3s':'Descent3 server','dm3s':'Doom 3 server',
            'efm':'Star Trek: Elite Force server','efs':'Star Trek: Elite Force server',
            'etqws':'QuakeWars server','eye':'All Seeing Eye Protocol server',
            'fcs':'FarCry server','fls':'Frontlines-Fuel of War server',
            'gps':'Gamespy Protocol server','grs':'Ghost Recon server',
            'gs2':'Gamespy V2 Protocol server','gs3':'Gamespy V3 Protocol server',
            'gs4':'Gamespy V4 Protocol server','h2s':'Hexen II server',
            'hazes':'Haze Protocol server','hl2s':'Half-Life 2 server',
            'hla2s':'Half-Life server','hlqs':'Half-Life server',
            'hls':'Half-Life server','hrs	':'Heretic II server',
            'hws':'HexenWorld server','iourts':'ioUrbanTerror server',
            'jk3m':'Jedi Knight: Jedi Academy server','jk3s':'Jedi Knight: Jedi Academy server',
            'kps':'Kingpin server','maqs':'Medal of Honor: Allied Assault (Q) server',
            'mas':'Medal of Honor: Allied Assault server','mhs':'Medal of Honor: Allied Assault server',
            'mumble':'Mumble server','netp':'NetPanzer server',
            'nexuizs':'Nexuiz server','openarenas':'OpenArena server',
            'ottds':'OpenTTD server','preys':'PREY server',
            'prs':'Pariah server','q2s':'Quake II server',
            'q3s':'Quake III: Arena server','q4s':'Quake 4 server',
            'qs':'Quake server','qws':'QuakeWorld server',
            'rss':'Ravenshield server','rws':'Return to Castle Wolfenstein server',
            'sas':'Savage server','sfs':'Soldier of Fortune server',
            'sgs':'Shogo: Mobile Armor Division server','sms':'Serious Sam server',
            'sns':'Sin server','sof2s':'Soldier of Fortune 2 server',
            't2s':'Tribes 2 server','tbs':'Tribes server',
            'tee':'Teeworlds server','terraria':'Terraria server',
            'tm':'TrackMania server','tremulous':'Tremulous server',
            'tremulousm':'Tremulous Master server','ts2':'Teamspeak 2 server',
            'ts3':'Teamspeak 3 server','uns':'Unreal server',
            'ut2004s':'UT2004 server','ut2s':'Unreal Tournament 2003 server',
            'ut3s':'UT3 server','vent':'Ventrilo server',
            'warsows':'Warsow server','waws':'Call of Duty World at War server',
            'wics':'World in Conflict server','woets':'Enemy Territory server',
            'wolfs':'Wolfenstein server' }
        if not game:
            return qstatgames
        elif game in qstatgames:
            return True
        else:
            return False
         
    def _qstatmaster(self, opttype, optserver, optport=None):
        """invoke qstat against a specified master server."""
        if optport is None:
            address = optserver
        else:
            address = '%s:%d' % (name,optport)
        opttype = '-'+opttype
        # build command
        command = [self.qstatpath,'-utf8','xml','-timeout','10','-sort','n','-u','-ne',opttype,address]  
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
    
    def qstatmaster(self, irc, msg, args, optlist, opttype, optserver):
        """<server type> <masterservername>
        Ex: iourtm master.urbanterror.info
        """
        
        # first, check if qstat works.
        if not self._verify():
            irc.reply("I cannot execute qstat. Please check the qstatPath config variable.")
            return
        
        # second, check gametype
        if self._qstatmasters(game=opttype) is False:
            irc.reply("ERROR: Game type must be one of {0}".format(self._qstatgames()))
            return
            
        # execute qstat and process XML.
        qstatxml = self._qstatmaster(opttype, optserver)
        if qstatxml is None:
            irc.reply("ERROR trying to query: %s. Check the logs" % optserver)
            return
            
        root = ElementTree.fromstring(qstatxml)
        if root.tag != "qstat":
            irc.reply("Something went horribly wrong running qstat.")
            return
            
    qstatmaster = wrap(qstatmaster, [getopts({}), ('somethingWithoutSpaces'), ('somethingWithoutSpaces')])

    def qstat(self, irc, msg, args, optlist, opttype, optserver):
        """[--players|--rules] <server type> <server name>
        Use qstat to query a server type.
        """

        # first, check if qstat works.
        if not self._verify():
            irc.reply("I cannot execute qstat. Please check the qstatPath config variable.")
            return
        
        # second, check gametype
        if self._qstatgames(game=opttype) is False:
            irc.reply("ERROR: Game type must be one of {0}".format(self._qstatgames()))
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
            irc.reply("Rules :: {0}".format(" | ".join([k + ": " + v for (k,v) in rules.iteritems()])))

    qstat = wrap(qstat, [getopts({'players':'','rules':''}), ('somethingWithoutSpaces'), ('somethingWithoutSpaces')])

Class = QStat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=270:
