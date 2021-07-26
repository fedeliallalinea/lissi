import logging, re, requests

from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Wgo(Plugin):
    
    def cmd_project(self, params, user, channel, msg):
        if len(params) >= 1:
            if msg.startswith('!'):
                logger.info('Catched command \'project\' with parameters \'%s\'' % params)
    
            projectName = self._best_project_match(' '.join(params))
            self._parse(
                'https://wiki.gentoo.org/wiki/Project:%s' % projectName, 
                ' '.join(params), 
                user, 
                channel)
            
    def listen_project(self, params, user, channel, msg):
        logger.info('Catched an entry that match %s' % self.get_listen_items()[0]['regex'])
        self._parse(
            'https://wiki.gentoo.org/wiki/Project:%s' % params[0], 
            params[0], 
            user, 
            channel)
    
    def _best_project_match(self, text):
        url = 'https://wiki.gentoo.org/wiki/Category:Gentoo_Projects'
        resp = requests.get(url)

        projectName = None
        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            projects = []
        
            links = html.find('div', {'class','mw-category'}).find_all('a')
            for link in links:
                m = re.match("Project:(.*)", link.text.strip())
                if m:
                    projects.append(m.group(1))
            
            bestRatio = 0.0
            for project in projects:
                ratio = SequenceMatcher(None, project.lower(), text.lower()).ratio()
                if ratio > 0.6 and ratio > bestRatio:
                    bestRatio = ratio
                    projectName = project
                    logger.info('%s compared to %s return ratio %s' % (text, project, ratio))
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            
        return projectName
               
    def _parse(self, url, param, user, channel):
        resp = requests.get(url)

        if resp.status_code == 200:
            html = BeautifulSoup(resp.text, 'lxml')
            table = html.find('table', {'class', 'table table-condensed'})

            title = table.find('th').text.strip()
            self.irc.privmsg(channel, '%s: Project name - %s' % (user, title))
            #print('Project name - %s' % title)
            
            for key in ['Description','Project email','IRC channel','Lead','Member']:
                titleRow = table.find(lambda tag: (tag.name == 'th' or tag.name == 'span'), text=re.compile('^'+key))
                text = key + ' - '
                if titleRow:
                    content = titleRow.find_next('td')
                    listItems = content.find_all('li')
                    if listItems:
                        members = ''
                        for listItem in listItems:
                            for i in listItem.select('i'):
                                i.extract()
                            members = members + ', ' + listItem.text.strip().replace('\n',' ')
                        text = text + members[2:]
                    else:
                        text = text + content.text.strip().replace(' (webchat)','')
                    
                    self.irc.privmsg(channel, '%s: %s' % (user, text))
            
            self.irc.privmsg(channel, '%s: %s' % (user, url))
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            self.irc.privmsg(channel, '%s: A project page with name \'%s\' doesn\'t exist' % (user, param))
    
    def get_listen_items(self):
        return [{
            'callback': 'project',
            'regex': [
                '.*https://wiki.gentoo.org/wiki/Project:(\w+).*'
            ]
        }]