import logging, requests

from bs4 import BeautifulSoup
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Glsa(Plugin):
    
    def cmd_glsa(self, params, user, channel, msg):
        if len(params) >= 1:
            if msg.startswith('!'):
                logger.info('Catched command \'glsa\' with parameters \'%s\'' % params)
            
            if params[0].startswith('#'):
                params[0] = params[0][1:]
            self._parse(
                'https://security.gentoo.org/glsa/%s' % params[0], 
                params[0],
                user, channel)
            
    def listen_glsa(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[0]['regex'])
        self.cmd_glsa(params, user, channel, msg)
                
    def _parse(self, url, param, user, channel):
        resp = requests.get(url, allow_redirects=False)

        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            logger.debug(html)
            
            title = html.find('h1', {'class': 'first-header'}).text.strip()
            info = html.find('div', {'class': 'col-12 col-md-2'}).find_all('p')
            
            self.irc.privmsg(channel, '%s: GLSA - %s' % (user, title))
            for i in [0,2,3]:
                txt = info[i].find('strong').text.strip() + ' - '
                info[i].find('strong').extract()
                txt = txt + info[i].text.strip()
                self.irc.privmsg(channel, '%s: %s' % (user, txt))
            self.irc.privmsg(channel, '%s: https://security.gentoo.org/glsa/%s' % (user, param))
            
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            self.irc.privmsg(channel, '%s: the page return status code %d' % (user, resp.status_code))
    
    def get_listen_items(self):
        return [{
            'callback': 'glsa',
            'regex': [
                '.*https://security.gentoo.org/glsa/([0-9]{6}-[0-9]+).*'
            ]
        }]