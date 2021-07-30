import logging, os, random, struct, time

from lissi.plugins.plugin import Plugin

logger = logging.getLogger(__name__)

class Fortune(Plugin):

    def cmd_fortune(self, params, user, channel, msg):
        logger.info('Catched command \'fortune\'')
        text = self._fortune()
        if text is not None:
            for line in text.splitlines():
                self.irc.privmsg(channel, '%s: %s' % (user, line))
                time.sleep(0.5)

    def _fortune(self):
        path = self.config.get('path','/usr/share/fortune')
        if not path:
            path = '/usr/share/fortune'

        if not os.path.isdir(path):
            logger.error('The path \'%s\' does not exist or is not a folder' % path)
            return None

        files = []
        for file in os.listdir(path):
            if file.endswith(".dat"):
                files.append(os.path.join(path, file))

        if len(files) < 1:
            logger.error('The path \'%s\' does not contain fortune files' % path)
            return None

        rand = random.randint(1, len(files))
        fortune_file_dat = files[rand - 1]
        fortune_file = os.path.splitext(fortune_file_dat)[0]
        logger.info('Read random fortune from file \'%s\'' % fortune_file)

        try:
            with open(fortune_file_dat, 'rb') as dat:
                # (version, numstr, len of longest string, len of shortest string, flags, delimiter, )
                header = struct.unpack(">IIIIIcxxx", dat.read(24))
                offsets = []  # for offsets from dat file
                for i in range(header[1] + 1):  # str_numstr + 1 == no. of offsets (starting from 0 to str_numstr)
                    offsets.append(struct.unpack(">I", dat.read(4)))

            for attempt in range(0,10):
                rand = random.randint(1, header[1])
                with open(fortune_file) as file:
                    fortunes_all = file.read()
                    fortune = fortunes_all[offsets[rand - 1][0]:offsets[rand][0] - 2]  # -2 to remove '%\n'

                if len(fortune.splitlines()) < 7:
                    break;
                
                logger.info('The attempt %s failed the string is too long: %s' % (attempt, fortune))
                
            logger.debug(fortune)
            return fortune
        except Exception as e:
            logger.error("Unexpected error:", e)

        return None
