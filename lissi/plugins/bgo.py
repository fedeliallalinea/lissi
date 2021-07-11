import logging, requests

from bs4 import BeautifulSoup
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Bgo(Plugin):
    
    def cmd_bug(self, params, user, channel, msg):
        if len(params) >= 1:
            if msg.startswith('!'):
                logger.info('Catched command \'bug\' with parameters \'%s\'' % params)
            
            if params[0].startswith('#'):
                params[0] = params[0][1:]
            self._parse(
                'https://bugs.gentoo.org/show_bug.cgi?id=%s' % params[0], 
                params[0],
                user, channel)
            
    def listen_bug(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[0]['regex'])
        self.cmd_bug(params, user, channel, msg)
                
    def _parse(self, url, param, user, channel):
        resp = requests.get(url, allow_redirects=False)

        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            logger.debug(html)
            
            error = html.find('div', {'id': 'error_msg'})
            
            if error is None:
                description = html.find('span', {'id': 'short_desc_nonedit_display'}).text.strip()
                status = html.find('span', {'id': 'static_bug_status'}).text.strip()
                assignee = html.find('span', {'class': 'fn'}).text.strip()
                
                self.irc.privmsg(channel, '%s: Bug %s - %s' % (user, param, description))
                self.irc.privmsg(channel, '%s: Status: %s, Assignee: %s' % (user, status, assignee))
                self.irc.privmsg(channel, '%s: https://bugs.gentoo.org/%s' % (user, param))
            else:
                self.irc.privmsg(channel, '%s: %s' % (user, error.text.strip()))
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            self.irc.privmsg(channel, '%s: the page return status code %d' % (user, resp.status_code))
    
    def get_listen_items(self):
        return [{
            'callback': 'bug',
            'regex': [
                '.*https://bugs.gentoo.org/([0-9]+).*',
                '.*https://bugs.gentoo.org/show_bug.cgi?id=([0-9]+).*'
            ]
        }]