import logging, re

from abc import ABC

logger = logging.getLogger(__name__)

class Plugin(ABC):
    
    def __init__(self, irc, botname):
        self.irc = irc
        self.botname = botname
 
    def execute(self, user, channel, msg):
        matches_action = re.match('^\x01ACTION (.*)\x01$', msg)
        matches_command = re.match('^!(\w+)(?: (.*)|)', msg)
        listeners = self.get_listen_items()
        
        if matches_action:
            self.on_action(user, channel, matches_action.group(1));
        elif matches_command: 
            cmd = matches_command.group(1)

            params = []
            if matches_command.group(2):
                params = matches_command.group(2).split()
                
            self.run_callback('cmd_'+cmd, params, user, channel, msg)
        elif isinstance(listeners, list) == True:
            for l in listeners:
                if 'regex' in l.keys() and 'callback' in l.keys():
                    for regex in l['regex']:
                        matches = re.match(regex, msg)
                        if matches:
                            logger.info('Listen item \'%s\' catch' % l['regex'])
                            params = []
                            for group in matches.groups():
                                params.append(group)
                            self.run_callback('listen_'+l['callback'], params, user, channel, msg)
                else:
                    logger.error('Missing regex or callback key in listen item \'%s\'' % l)
            
    
    def run_callback(self, callback, params, user, channel, msg):
            try:
                fn = getattr(self, callback)
                fn(params, user, channel, msg)
            except AttributeError:
                pass
    
    def on_action(self, user, channel, msg):
        pass
            
    def get_listen_items(self):
        return None