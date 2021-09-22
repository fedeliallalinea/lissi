import logging, requests

from bs4 import BeautifulSoup
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Gml(Plugin):
            
    def listen_gml(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[0]['regex'])
        self._parse(
            'https://archives.gentoo.org/%s/message/%s' % (params[0], params[1]), 
            params,
            user, channel)
                
    def _parse(self, url, params, user, channel):
        resp = requests.get(url, allow_redirects=False)

        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            logger.debug(html)

            rows = html.find('table', {'class': 'ag-header-table'}).find_all('tr')
            
            self.irc.privmsg(channel, '%s: Messsage - %s' % 
                 (user,
                  rows[2].find('td').text.strip()))
            self.irc.privmsg(channel, '%s: from %s (%s)' % 
                 (user, 
                  rows[0].find('td').text.strip(), 
                  rows[3].find('td').text.strip()))
            if (len(rows) > 5):
                self.irc.privmsg(channel, '%s: in reply to %s' % 
                    (user, rows[5].find('td').text.strip()))
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            self.irc.privmsg(channel, '%s: the page return status code %d' % (user, resp.status_code))
    
    def get_listen_items(self):
        return [{
            'callback': 'gml',
            'regex': [
                '.*https://archives.gentoo.org/([a-z|-]+)/message/([a-z|0-9]+).*'
            ]
        }]