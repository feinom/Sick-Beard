# Author: Svein-Erik Larsen <larsen.sveinerik@gmail.com>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import irclib
import threading
import time

import sickbeard

from sickbeard import logger
from sickbeard import common


class IRCNotifier(irclib.IRC, threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        irclib.IRC.__init__(self)

    def run(self):
        threading.Thread.run(self)
        threading.currentThread().name = "IRC"
        self.srv = self.server()
        self.server_addr, self.server_port = sickbeard.IRC_SERVER.split(":")
        self.connect()
        self.process_forever()

    def stop(self):
        self.disconnect_all(message="SickBeard")

    def connect(self):
        logger.log(u"Connecting to IRC server %s:%s" % (self.server_addr, self.server_port))
        try:
            self.srv.connect(self.server_addr, int(self.server_port), sickbeard.IRC_NICKNAME,\
                                password = sickbeard.IRC_SERVER_PASSWORD, ssl=sickbeard.IRC_SERVER_ENCRYPTION)
        except irclib.ServerConnectionError:
            logger.log(u"Unable to connect to IRC server.")
            time.sleep(5)
            self.connect()

        while (self.srv.is_connected() == 0):
            time.sleep(1)
        
        logger.log(u"Joining IRC channel %s" % sickbeard.IRC_CHANNEL)
        self.srv.join(sickbeard.IRC_CHANNEL, key=sickbeard.IRC_CHANNEL_KEY)

    def notify_snatch(self, ep_name):
        if sickbeard.IRC_NOTIFY_ONSNATCH:
            self.notify(None, "%s: %s" % (common.notifyStrings[common.NOTIFY_SNATCH], ep_name))

    def notify_download(self, ep_name):
        if sickbeard.IRC_NOTIFY_ONDOWNLOAD:
            self.notify(None, "%s: %s" % (common.notifyStrings[common.NOTIFY_DOWNLOAD], ep_name))

    def test_notify(self, host, password, ssl, nickname, channel, channel_key):
        try:
            self.start()
            self.notify(None, "Testing IRC notifications from Sick Beard")
            self.stop()
            return True
        except:
            return False

        #return "IRC test not implemented yet... Please restart sickbeard to test."
        #self.srv = self.server()
        #self.server_addr, self.server_port = host.split(":")
        #self.srv.connect(self.server_addr, int(self.server_port), nickname,\
        #                    password = password, ssl=ssl)
        #time.sleep(10)
        #self.srv.join(channel, key=channel_key)
        #time.sleep(1)
        #self.srv.privmsg(channel, "Test Notification: Testing IRC notifications from Sick Beard")
        #self.srv.disconnect("SickBeard")

    def notify(self, type, msg):
        logger.log(u"Sending IRC notification to %s: %s" % (sickbeard.IRC_CHANNEL, msg))
        try:
            self.srv.privmsg(sickbeard.IRC_CHANNEL, msg)
        except irclib.ServerNotConnectedError:
            self.connect()
            self.srv.privmsg(sickbeard.IRC_CHANNEL, msg)

notifier = IRCNotifier
