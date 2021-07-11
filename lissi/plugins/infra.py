import logging, re, requests, time

from bs4 import BeautifulSoup
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Infra(Plugin):
     
    def cmd_infra(self, params, user, channel, msg):
        if len(params) >= 1:
            logger.info('Catched command \'topic\' with parameters \'%s\'' % params)
            
            if len(params[0]) < 3:
                self.irc.privmsg(channel, '%s: the name of the service must be at least 3 characters' % user)
                logger.error('the parameter \'%s\' must be at least 3 characters' % params[0])
            else:
                self._parse(
                    'https://infra-status.gentoo.org', 
                    params[0],
                    user, channel)
        
    def _parse(self, url, param, user, channel):
        resp = requests.get(url, allow_redirects=False)

        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            
            logger.debug(html)
            
            items = html.find_all('a', {'class': 'list-group-item'})
            for item in items:
                service = item.text.strip()
                
                if re.match('.*'+param+'.*', service, re.IGNORECASE):
                    status = item['title']
                    self.irc.privmsg(channel, '%s: %s -> %s' % (user, service, status))
                    time.sleep(0.5)
                
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            self.irc.privmsg(channel, '%s: the page return status code %d' % (user, resp.status_code))