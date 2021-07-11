import logging, re, requests

from bs4 import BeautifulSoup
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Fgo2(Plugin):
    
    def cmd_topic(self, params, user, channel, msg):
        if len(params) >= 1:
            if msg.startswith('!'): 
                logger.info('Catched command \'topic\' with parameters \'%s\'' % params)
            
            self._manage_response(
                'https://forums.gentoo.org/viewtopic-t-%s.html' % params[0], 
                self._parse_tp_info,
                user, channel)
            
    def listen_topic(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[0]['regex'])
        self.cmd_topic(params, user, channel, msg)
                
    def cmd_post(self, params, user, channel, msg):
        if len(params) >= 1: 
            if msg.startswith('!'): 
                logger.info('Catched command \'post\' with parameters \'%s\'' % params)
            
            self._manage_response(
                'https://forums.gentoo.org/viewtopic-p-%s.html' % params[0], 
                self._parse_tp_info,
                user, channel)
            
    def listen_post(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[1]['regex'])
        self.cmd_post(params, user, channel, msg)
            
    def cmd_profile(self, params, user, channel, msg):
        if len(params) >= 1: 
            if msg.startswith('!'): 
                logger.info('Catched command \'profile\' or \'user\' with parameters \'%s\'' % params)
            
            self._manage_response(
                'https://forums.gentoo.org/profile.php?mode=viewprofile&u=%s' % params[0], 
                self._parse_profile_info,
                user, channel)
            
    def cmd_user(self, params, user, channel, msg):
        self.cmd_profile(params, user, channel, msg)
    
    def listen_profile(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[2]['regex'])
        self.cmd_profile(params, user, channel, msg)
                
    def _manage_response(self, url, parser_fn, user, channel):
        try:
            resp = self._get_response(url)
            text = parser_fn(resp)
            self.irc.privmsg(channel, '%s: %s' % (user, text))
            self.irc.privmsg(channel, '%s: %s' % (user, url))
        except requests.exceptions.RequestException as err:
            self.irc.privmsg(channel, '%s: %s' % (user, err))
                
    def _parse_tp_info(self, resp):
        html = BeautifulSoup(resp, 'lxml')
        
        logger.debug(html)
        
        title = html.find('a', attrs={'class': 'maintitle'}).text
        a_tags = html.find_all('span', attrs={'class': 'nav'})[1].find_all('a')
        forum = ''
        for a in a_tags[1:]:
            forum += ' -> ' + a.text
        forum = forum[4:]
        return forum + ' - ' + title
    
    def _parse_profile_info(self, resp):
        html = BeautifulSoup(resp, 'lxml')
        foo = html.find('th', attrs={'class': 'thHead'}).text
        nickname = re.match('.* :: (.*)', foo).group(1)
        info_table = html.find('table', attrs={'class': 'forumline'}).find_all('td',attrs={'class': 'row1'})[1]
        info_rows = info_table.find_all('tr')
        join_date = info_rows[0].find_all('span',attrs={'class': 'gen'})[1].text
        total_posts = info_rows[1].find_all('span',attrs={'class': 'gen'})[1].text
        return nickname + ' (' + join_date + ' - ' + total_posts + ' posts)'
        
    def _get_response(self, url):
        resp = requests.get(url, allow_redirects=False)
        if resp.status_code > 300 and resp.status_code < 400:
            raise requests.exceptions.RequestException('No permission to see this topic')
        elif resp.status_code == 200:
            if 'The topic or post you requested does not exist' in resp.text:
                raise requests.exceptions.RequestException('The topic or post you requested does not exist')
            else:
                return resp.text
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
    
    def get_listen_items(self):
        return [{
            'callback': 'topic',
            'regex': [
                '.*https:\/\/forums\.gentoo\.org\/viewtopic-t-([0-9]+).*',
                '.*https:\/\/forums\.gentoo\.org\/viewtopic.php\?t=([0-9]+).*'
            ]
        },{
            'callback': 'post',
            'regex': [
                '.*https:\/\/forums\.gentoo\.org\/viewtopic-p-([0-9]+).*',
                '.*https:\/\/forums\.gentoo\.org\/viewtopic.php\?p=([0-9]+).*'
            ]
        },{
            'callback': 'profile',
            'regex': [
                '.*https:\/\/forums\.gentoo\.org\/profile.php\?mode=viewprofile&u=([0-9]+).*'
            ]
        }]