from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from datetime import datetime as DT
# http://twistedmatrix.com/documents/current/core/howto/clients.html

# timeout handling mixin.
from twisted.protocols.policies import TimeoutMixin

PLUGINDIR = 'plugins'

def dyn_import( plugin_name, plugin_dir=PLUGINDIR ):
    """import and reload plugin modules by name"""
    import sys
    module = "%s.%s" % ( plugin_dir, plugin_name )
    try:
        reload( sys.modules[ module ] )
    except KeyError:
        try:
             __import__( module )
        except ImportError:
            return False
    return sys.modules[ module ]

def loggit( *messages ):
    """Handle Logging to standard out."""
    NOW = DT.now().strftime( "%Y-%m-%d %H:%M:%S " )
    output = NOW + ' '.join( map( str, messages ) )
    print(output)


class Foxbot(irc.IRCClient, TimeoutMixin):

    def run_plugin( self, plugin, user='', channel='', msg='' ):
        """Accept a plugin string name, load and run"""
        mod = dyn_import( plugin ) # attempt to load module by name
        if mod:
            result = mod.main( msg )
            if result: # speak the string result
                if channel:
                    self.msg( channel, result ) 
                return True
        return False

    def _get_nickname( self ):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join( self.factory.channel, self.factory.key )
        loggit( "Signed on as %s." % (self.nickname) )

    def joined(self, channel):
        loggit( "Joined %s." % (channel) )

    def privmsg(self, user, channel, msg):
        loggit( user, msg )
        if '://' in msg:
            loggit( "URI detected!" )
            self.run_plugin( 'urinfo', user, channel, msg )

    def action(self, user, channel, msg ):
        """Called when the bot sees a user do an action"""
        loggit( user, msg )
        plugin = msg.split()[0] # use first word as plugin name
        self.run_plugin( plugin, user, channel, msg ) # try to run

    def kickedFrom(self, channel, kicker, message):
        """Called when kicked from channel"""
        loggit( "Kicked by %s: %s" % ( kicker, message ) )
        self.join( self.factory.channel, self.factory.key )

    def modeChanged(self, user, channel, set, modes, args):
        loggit( "mode changed:", user, channel, set, modes, args)
        if set and 'k' in modes:
            self.factory.key = args
        elif not set and 'k' in modes:
            self.factory.key = None


class FoxbotFactory( protocol.ClientFactory ):
    protocol = Foxbot

    def __init__(self, channel, nickname='foxbot', password=None, key=None):
        self.key = key
        self.channel = channel
        self.nickname = nickname
        self.password = password

    def clientConnectionLost(self, connector, reason):
        loggit( "Lost connection (%s), reconnecting." % (reason) )
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        loggit( "Could not connect: %s" % (reason) )

    # from twisted.protocols.policies import TimeoutMixin.
    def timeoutConnection(self):
        self.transport.abortConnection()


def main():
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('-s', '--server', dest='server')
    p.add_option('-p', '--port', dest='port', default=6667)
    p.add_option('-c', '--channel', dest='channel')
    p.add_option('-k', '--key', dest='key')
    p.add_option('-n', '--nick', dest='nick', default='foxbot')
    p.add_option('-P', '--password', dest='password', default=None)
    p.add_option('-q', '--quiet', dest='quiet', default=False,
        action='store_true'
    )
    o, args = p.parse_args()

    if o.server and o.channel:

        reactor.connectTCP(
          o.server, 
          int(o.port), 
          FoxbotFactory( o.channel, o.nick, o.password, o.key )
        )
        reactor.run()

    else:
        print("Provide server and channel (foxbot --help)")

if __name__ == "__main__":
    main()
