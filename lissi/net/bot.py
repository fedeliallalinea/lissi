import importlib, logging, signal, sys

logger = logging.getLogger(__name__)

class Bot:

    def __init__(self, name, irc):
        self.name = name
        self.irc = irc
        self._plugins = []
        
        signal.signal(signal.SIGINT, self._handler_stop_signals)
        signal.signal(signal.SIGTERM, self._handler_stop_signals)
        
    def add_plugin(self, plugin):
        try:
            module = importlib.import_module('%s.%s' % ('lissi.plugins', plugin))
            cls = getattr(module, plugin.capitalize())
            self._plugins.append(cls(self.irc,self.name))
        except ModuleNotFoundError:
            logger.error('No module plugins.%s found' % plugin.lower())
        except AttributeError:
            logger.error('No class %s found in module plugins.%s' % (plugin,plugin.lower()))
            
    def _handler_stop_signals(self, signum, frame):
        sys.exit(0)
            
    def start(self):
        logger.info("%s bot is started" % self.name)
        
        while True:
            lines = self.irc.get_response(lines=True)

            for line in lines:
                line=line.rstrip()
                irc_cmd = self.irc.parse_line(line)
                if irc_cmd is None:
                    continue
                
                # keep bot alive
                if irc_cmd['command'] == 'PING':
                    self.irc.send_command('PONG', irc_cmd['params'][0])
                elif irc_cmd['command'] == 'PRIVMSG':
                    nick = irc_cmd['nick']
                    channel = irc_cmd['params'][0]
                    msg = irc_cmd['params'][1] if irc_cmd['params'][1] else None
                    
                    # is a private message
                    if not channel.startswith('#'):
                        channel = nick
                    
                    for plugin in self._plugins:
                        plugin.execute(nick,channel,msg)
