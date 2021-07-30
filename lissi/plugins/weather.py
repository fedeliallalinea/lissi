import json, logging, requests

from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Weather(Plugin):

    def cmd_weather(self, params, user, channel, msg):
        logger.info('Catched command \'weather\', \'wttr\' or \'wx\'')
        text = self._get_from_wttr_in('+'.join(params))
        if text is not None:
            self.irc.privmsg(channel, '%s: %s' % (user, text))

    def cmd_wttr(self, params, user, channel, msg):
        self.cmd_weather(params, user, channel, msg)

    def cmd_wx(self, params, user, channel, msg):
        self.cmd_weather(params, user, channel, msg)

    def _get_from_wttr_in(self, location):
        base_url = "http://wttr.in/%s?format=%s"
        url = base_url % (location, 'j1')
        resp = requests.get(url)

        if resp.status_code == 200:
            obj = json.loads(resp.text)
            real_location = obj['nearest_area'][0]['areaName'][0]['value']
            url = base_url % (real_location, '%c+%C+|+%t+|+%w+|+%p+|+%P')

            resp = requests.get(url)
            if resp.status_code == 200:
                return location + ' (' + real_location + ') - ' + resp.text
            else:
                logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
                return 'The url \'%s\' return status code %d' % (url, resp.status_code)
        else:
            logger.error('The url \'%s\' return status code %d' % (url, resp.status_code))
            return 'The url \'%s\' return status code %d' % (url, resp.status_code)