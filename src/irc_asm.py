from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
import random, datetime
import time, sys, re
from ibasm import Runtime, ParseError

SERVER = sys.argv[1]
NICKNAME = sys.argv[2]
CHANNELS_AUTOJOIN = sys.argv[3:]

class GhettoAsmBot(irc.IRCClient):
    nickname = NICKNAME
    def connectionMade(self, *args, **kwargs):
        self._runtime = Runtime()
        irc.IRCClient.connectionMade(self, *args, **kwargs)

    def signedOn(self):
        for ch in CHANNELS_AUTOJOIN:
            self.join(ch)

    def privmsg(self, user, channel, message):
        nick = user.split('!', 1)[0]
        if message.startswith('= '):
            try:
                for submsg in re.split(";\s{0,}", message[2:]):
                    if not submsg: next
                    retval = self._runtime.do_instruction(submsg)
                    if retval is not None:
                        self.say(channel, "%s: %s" % (nick, str(retval)))
            except ParseError as e:
                self.say(channel, str(e))
        if message.startswith('=$ '):
            for submsg in re.split(";\s{0,}", message[2:]):
                retval = self._runtime.do_compiled_instruction(int(submsg))
                if retval is not None:
                    self.say(channel, "%s: %s" % (nick, str(retval)))

class AsmBotFactory(protocol.ClientFactory):
    protocol = GhettoAsmBot
    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    reactor.connectTCP(SERVER, 6667, AsmBotFactory())
    reactor.run()
