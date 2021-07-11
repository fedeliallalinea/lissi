import logging, re, socket, time

from enum import Enum

logger = logging.getLogger(__name__)

class Irc:

	def __init__(self):
		# Define the socketfrom dns.rdataclass import NONE

		self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# See https://gist.github.com/datagrok/380449c30fd0c5cf2f30
		self._rfc2812_pattern = ''.join([
			'^',						# We'll match the whole line. Start.
										# Optional prefix and the space that separates it
										# from the next thing. Prefix can be a servername,
										# or nick[[!user]@host]
			'(?::(',					# This whole set is optional but if it's
										# here it begins with : and ends with space
				'([^@!\ ]*)',			# nick
				'(?:',					# then, optionally user/host
					'(?:',				# but user is optional if host is given
						'!([^@]*)',		# !user
					')?',				# (user was optional)
					'@([^\ ]*)',		# @host
				')?',					# (host was optional)
			')\ )?',					# ":nick!user@host " ends
			'([^\ ]+)',					# IRC command (required)
										# Optional args, max 15, space separated. Last arg is
										# the only one that may contain inner spaces. More than
										# 15 words means remainder of words are part of 15th arg.
										# Last arg may be indicated by a colon prefix instead.
										# Pull the leading and last args out separately; we have
										# to split the former on spaces.
			'(',
				'(?:',
					'\ [^:\ ][^\ ]*',	# space, no colon, non-space characters
				'){0,14}',				# repeated up to 14 times
			')',						# captured in one reference
			'(?:\ :?(.*))?',			# the rest, does not capture colon.
			'$'])						# EOL

	def send_command(self, *args, **kwargs):
		raw_command = self.prepare_command(*args, text=kwargs.get('text'))
		self.irc.send(raw_command.encode('UTF-8'))

	def prepare_command(self, *args, **kwargs):
		"""IRC messages are always lines of characters terminated with a
		CR-LF (Carriage Return - Line Feed) pair, and these messages SHALL
		NOT exceed 512 characters in length, counting all characters
		including the trailing CR-LF. Thus, there are 510 characters
		maximum allowed for the command and its parameters. There is no
		provision for continuation of message lines.
		"""
		text = kwargs.get('text')
		max_length = unicode_max_length = 510
		raw_command = ' '.join(args)
		if text is not None:
			raw_command = '{args} :{text}'.format(args=raw_command,text=text)

		while len(raw_command.encode('UTF-8')) > max_length:
			raw_command = raw_command[:unicode_max_length]
			unicode_max_length = unicode_max_length - 1

		return raw_command + '\r\n'

	def privmsg(self, dest, text):
		self.send_command('PRIVMSG', dest, text=text)
		
	def me(self, dest, text):
		self.send_command('PRIVMSG', dest, text='\x01ACTION '+text+'\x01')

	def connect(self, server, port, botnick, botpass):
		logger.info('Try to commenct on %s:%d' % (server,port))
		self.irc.connect((server, port))
		time.sleep(2)
		logger.debug(self.get_response())

		
		logger.info('Set nick/user to %s' % botnick)
		# Perform user authentication
		self.send_command('NICK', botnick)
		self.send_command('USER', botnick, botnick, botnick, botnick)
		self.send_command('NICKSERV IDENTIFY', botnick, botpass)
		time.sleep(10)
		logger.debug(self.get_response())

	def join(self, channel, invite=False):
		logger.info('Join channel %s' % channel)
		if invite is True:
			self.privmsg('ChanServ', 'invite ' + channel)
			time.sleep(1)

		self.send_command('JOIN', channel)
		time.sleep(1)
		logger.debug(self.get_response())

	def get_response(self, lines=False):
		time.sleep(1)
		readbuffer = self.irc.recv(2040).decode('UTF-8')
		
		logger.debug('Read irc buffer\n%s' % readbuffer)
		if lines is True:
			return readbuffer.split('\n')
		else:
			return readbuffer
	
	def parse_line(self, string):
		matches = re.match(self._rfc2812_pattern, string)
		if not matches:
			return None
		
		params = matches.group(6).lstrip().split()
		if matches.group(7):
			params.append(matches.group(7).lstrip())
		
		return {
			'raw': string,
			'prefix': matches.group(1),
			'nick': matches.group(2), # or servername
			'username': matches.group(3),
			'hostname': matches.group(4),
			'command': matches.group(5),
			'params': params
		}
		
class IrcCmd(Enum):
	PRIVMSG='PRIVMSG'
	PING='PING',
	KICK='KICK'
	
	
	