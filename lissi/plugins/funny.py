import logging, re

from random import randrange
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Funny(Plugin):
     
    def on_action(self, user, channel, msg):
        matches = re.match('kicks '+self.botname+'.*', msg)

        if matches:
            logger.info('Catched action \'kicks %s\'' % self.botname)
            
            options = {
                1: 'wanker!',
                2: 'stop that :(',
                3: 'ouch! :((',
                4: 'kicks ' + user + ' in the junk'}
            
            random = randrange(1,5)
            
            if random == 4:
                self.irc.me(channel, options[4])
            else:
                self.irc.privmsg(channel, options[random])
                
        matches = re.match('pats '+self.botname+'.*', msg)
        if matches:
            logger.info('Catched action \'pats %s\'' % self.botname)
            
            options = {
                1: 'does the happy dance :)',
                2: 'beams'}
            
            random = randrange(1,3)
            self.irc.me(channel, options[random])