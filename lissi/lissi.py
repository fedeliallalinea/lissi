import configparser, logging, os, sys

from logging.handlers import RotatingFileHandler
from lissi.net.irc import Irc
from lissi.net.bot import Bot

logger = logging.getLogger(__name__)

def configure_logger(config):
	try:
		log_level = getattr(logging, config.get('log','level'))
	except (AttributeError, KeyError):
		log_level = logging.INFO
		
	try:
		handlers = [ RotatingFileHandler(filename=config.get('log','file'), 
	        mode='w', 
	        maxBytes=10485760, 
	        backupCount=4)
		]
	except:
		handlers = None

	logging.basicConfig(handlers=handlers, 
                    level=log_level, 
                    format='%(asctime)s %(levelname)s %(filename)s - %(message)s')

def main():
	config = configparser.ConfigParser(allow_no_value=False)
	configFiles = config.read([
		os.path.expanduser('~/.config/lissi.cfg'),
		os.path.expanduser('/etc/lissi.cfg'),
		'./etc/lissi.cfg'], encoding='UTF-8')
	configure_logger(config)

	logger.info('Read %s config files' % configFiles)
	
	hasChannels = True
	try:
		channels = config.get('irc','channels')
		if not channels:
			raise Exception()
		channels = channels.replace(' ','').split(',')
	except Exception:
		logger.info('You have not set any channels')
		channels = []
		hasChannels = False
		
	try:
		invite_channels = config.get('irc','invite_channels')
		if not invite_channels:
			raise Exception()
		invite_channels = invite_channels.replace(' ','').split(',')
	except Exception:
		logger.info('You have not set any invite channels')
		invite_channels = []
		if hasChannels == False:
			logger.error('You have not set any channels or invite channels')
			sys.exit(1)

	irc = Irc()
	try:
		irc.connect(
				config.get('irc','server'), 
				config.getint('irc','port'), 
				config.get('bot','name'),
				config.get('bot','password'))
	except Exception as msg:
		logger.error('Wrong configuration: %s' % msg)
		sys.exit(1)
	
	for channel in channels:
		irc.join(channel)
	
	for channel in invite_channels:
		irc.join(channel, invite=True)
	
	try:
		bot = Bot(config.get('bot','name'), irc)
		for plugin in config.get('bot','plugins').replace(' ','').split(','):
			bot.add_plugin(plugin)
	except Exception as msg:
		logger.error('Wrong configuration: %s' % msg)
		sys.exit(1)
	
	bot.start()
	
if __name__ == '__main__':
	main()
		