import logging

from lissi.plugins.plugin import Plugin
from lissi.info import __version__, __authors__, __homepage__, __bugto__

logger = logging.getLogger(__name__)

class Info(Plugin):
     
    def cmd_info(self, params, user, channel, msg):
        logger.info('Catched command \'info\'')
        self.irc.privmsg(channel, '%s: version - %s' % (user,__version__))
        self.irc.privmsg(channel, '%s: authors - %s' % (user,__authors__))
        self.irc.privmsg(channel, '%s: homepage - %s' % (user,__homepage__))
        self.irc.privmsg(channel, '%s: bug to - %s' % (user,__bugto__))