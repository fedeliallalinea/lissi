import logging, requests

from bs4 import BeautifulSoup
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Devaway(Plugin):
     
    def cmd_away(self, params, user, channel, msg):
        if len(params) >= 1:
            if msg.startswith('!'): 
                logger.info('Catched command \'away\' or \'devaway\' with parameters \'%s\'' % params)
            
            self._parse(
                'https://www.gentoo.org/inside-gentoo/developers/unavailable-developers.html', 
                params[0],
                user, channel)
        
    def cmd_devaway(self, params, user, channel, msg):
        self.cmd_away(params, user, channel, msg)
        
    def _parse(self, url, param, user, channel):
        resp = requests.get(url, allow_redirects=False)

        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            logger.debug(html)
            
            rows = html.find_all('tr')
            for row in rows:
                dev = row.find('th').text
                if dev.lower() == param.lower():
                    message = row.find('td').text
                    self.irc.privmsg(channel, '%s: %s' % (user, message))
                    return
                    
            self.irc.privmsg(channel, '%s: Sorry no devaway entry available for %s' % (user, param))
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            self.irc.privmsg(channel, '%s: the page return status code %d' % (user, resp.status_code))