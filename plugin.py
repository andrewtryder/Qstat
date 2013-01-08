###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

# my libs
import os
import sys
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
        
    def _verify(self):
        """Verify that the application is accessible."""
        try:
            pipe = os.popen("%s 2> /dev/null" % self.qstatpath)
            try:
                if not pipe.read():
                    self.log.error("QStat application not accessible")
            finally:
                pipe.close()
                self.log.info(("qstat found at: %s") % (self.qstatpath))
        except IOError:
            self.log.error("QStat communication interrupted.")

    def _qstat(self, type, name, port=None):
        """invoke qstat against a specified server."""
        if port is None:
            address = name
        else:
            address = '%s:%d' % (name, port)
        pipe = os.popen("%s -xml -%s %s -utf8 -P -R 2> /dev/null" % (self.qstatpath, type, address))
        try:
            return pipe.read()
        finally:
            pipe.close()

    def qstat(self, irc, msg, args, optlist, opttype, optserver):
        """[--players] <server type> <server name>
        Use qstat to query a server type.
        """

        args = {'showPlayers':False}
        
        if optlist:
            for (key, value) in optlist:
                if key == 'showplayers':
                    args['showPlayers'] = True

        qstatxml = self._qstat(opttype, optserver)
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
                    tmpdict['name'] = childchildren.find('name').text
                    tmpdict['score'] = childchildren.find('score').text
                    tmpdict['ping'] = childchildren.find('ping').text
                    players[tmpdict['name']] = tmpdict
            elif child.tag == "rules": # handle rules
                for childchildren in child.getchildren():
                    rules[childchildren.get('name')] = childchildren.text
            else:
                output[child.tag] = child.text

        irc.reply(str(output))
        irc.reply(str(players))
        irc.reply(str(rules))

    qstat = wrap(qstat, [getopts({'players': ''}), ('somethingWithoutSpaces'), ('somethingWithoutSpaces')])

Class = QStat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=270:
