###
# Copyright (c) 2012, none
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

#
import os
import sys

# 'Working' with XML sucks. Awesome module to turn it into JSON.
# https://github.com/martinblech/xmltodict
import xmltodict

_ = PluginInternationalization('QStat')

@internationalizeDocstring
class QStat(callbacks.Plugin):
    """Add the help for "@plugin help QStat" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _verify(self):
        """Verify that the application is accessible."""

        qstatpath = self.registryValue('qstatPath')

        try:
            pipe = os.popen("%s 2> /dev/null" % qstatpath)
            try:
                if not pipe.read():
                    raise Error, "QStat application not accessible"
            finally:
                pipe.close()
                self.log.info(("qstat found at: %s") % (qstatpath))
        except IOError:
            raise Error, "QStat application communication interrupted"

    def _statServer(self, type, name, port=None):
        """invoke qstat against a specified server."""

        qstatpath = self.registryValue('qstatPath')

        if port is None:
            address = name
        else:
            address = '%s:%d' % (name, port)
        pipe = os.popen("%s -xml -%s %s -utf8 -P -R 2> /dev/null" % (qstatpath, type, address))
        try:
            return pipe.read()
        finally:
            pipe.close()

    def qstat(self, irc, msg, args, type, server):

        qstatpath = self.registryValue('qstatPath')

        query = self._statServer(type, server)
        querydict = xmltodict.parse(query)

        status = querydict['qstat']['server']['@status']
        map = querydict['qstat']['server']['map']
        hostname = querydict['qstat']['server']['hostname'].strip()
        name = querydict['qstat']['server']['name']
        gametype = querydict['qstat']['server']['gametype']
        ping = querydict['qstat']['server']['ping']
        numplayers = querydict['qstat']['server']['numplayers']
        maxplayers = querydict['qstat']['server']['maxplayers']
        #type = querydict['qstat']['server']['type']

        players = querydict['qstat']['server']['players']['player']

        #for player in players:
        #    name = player['name']

        percent = '{percent:.2%}'.format(percent=float(numplayers)/float(maxplayers))

        irc.reply("%s %s (%s) server running game: %s in map: %s lag: %s players %s/%s (%s)" % (status, hostname, name, gametype, map, ping, numplayers, maxplayers, percent))
        #irc.reply(querydict)

    qstat = wrap(qstat, [('somethingWithoutSpaces'),('somethingWithoutSpaces')])

Class = QStat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=270:
