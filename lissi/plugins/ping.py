import logging

from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Ping(Plugin):
     
    def cmd_ping(self, params, user, channel, msg):
        logger.info('Catched command \'ping\'')
        self.irc.privmsg(channel, '%s: pong' % user)