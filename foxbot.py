import socket
import sys
import importlib
import os
from datetime import datetime as DT

PLUGINDIR = "plugins"


class PluginManager:
    def __init__(self, plugin_dir=PLUGINDIR):
        self.plugin_dir = plugin_dir
        self.plugins = {}

    def load_plugins(self):
        """Scan plugin directory and load all plugins."""
        loggit("Loading plugins...")
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]
                self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name):
        """Load a specific plugin by name."""
        module = f"{self.plugin_dir}.{plugin_name}"
        try:
            if module in sys.modules:
                loggit(f"Reloading plugin: {module}")
                importlib.reload(sys.modules[module])
            else:
                loggit(f"Loading plugin: {module}")
                __import__(module)
            self.plugins[plugin_name] = sys.modules[module]
        except Exception as e:
            loggit(f"Failed to load plugin {plugin_name}: {e}")

    def run_plugin(self, plugin_name, msg):
        """Run the main function of a plugin if available."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, "main"):
                try:
                    result = plugin.main(msg)
                    return result
                except Exception as e:
                    loggit(f"Error running plugin {plugin_name}: {e}")
        else:
            loggit(f"Plugin {plugin_name} not loaded.")
        return None


def loggit(*messages):
    """Handle Logging to standard out."""
    NOW = DT.now().strftime("%Y-%m-%d %H:%M:%S ")
    output = NOW + " ".join(map(str, messages))
    print(output)


class Foxbot:
    def __init__(
        self, server, port, channel, nickname, plugin_manager, password=None, key=None
    ):
        self.server = server
        self.port = port
        self.channel = channel
        self.nickname = nickname
        self.password = password
        self.key = key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.plugin_manager = plugin_manager

    def connect(self):
        """Connect to the IRC server and join the channel."""
        loggit(f"Connecting to {self.server}:{self.port}")
        self.sock.connect((self.server, self.port))
        self.send(f"NICK {self.nickname}")
        self.send(f"USER {self.nickname} 0 * :{self.nickname}")
        if self.password:
            self.send(f"PASS {self.password}")
        self.join_channel(self.channel)

    def join_channel(self, channel):
        """Join the specified IRC channel."""
        self.send(f"JOIN {channel}")
        loggit(f"Joined {channel}")

    def send(self, message):
        """Send a message to the IRC server."""
        loggit(f">> {message}")
        self.sock.send((message + "\r\n").encode())

    def receive(self):
        """Receive messages from the IRC server."""
        buffer = ""
        while True:
            data = self.sock.recv(4096).decode()
            buffer += data
            lines = buffer.split("\r\n")
            buffer = lines.pop()
            for line in lines:
                loggit(f"<< {line}")
                self.handle_message(line)

    def handle_message(self, message):
        """Process a message from the server."""
        results = []
        if message.startswith("PING"):
            # Respond to server PINGs to keep the connection alive
            self.send(f"PONG {message.split()[1]}")
        else:
            parts = message.split(" ")
            if len(parts) > 3 and parts[1] == "PRIVMSG":
                user = parts[0][1:].split("!")[0]
                channel = parts[2]
                msg = " ".join(parts[3:])[1:]

                # Check if it's an ACTION ("/me")
                if msg.startswith("\x01ACTION") and msg.endswith("\x01"):
                    action_msg = msg[8:-1].strip()  # Extract the action message
                    loggit(f"Action from {user}: {action_msg}")
                    plugin_name = action_msg.split()[0]  # The first word as plugin name
                    result = self.plugin_manager.run_plugin(plugin_name, action_msg)
                    if result is not None:
                        results.append(result)
                else:
                    loggit(f"Message from {user}: {msg}")

                    # Detect URLs and run the urinfo plugin if a URL is found
                    urls = [word for word in msg.split() if "://" in word]
                    if urls:
                        for url in urls:
                            loggit(f"URI detected: {url}")
                            result = self.plugin_manager.run_plugin("urinfo", url)
                            if result is not None:
                                results.append(result.decode("utf-8"))

                    if msg.startswith(self.nickname):
                        try:
                            plugin_name = msg.split()[1]
                        except KeyError:
                            plugin_name = None
                        if plugin_name:
                            result = self.plugin_manager.run_plugin(plugin_name, msg)
                            if result is not None:
                                results.append(result)

                # Send results if there are any valid non-None results
                if results:
                    self.send(f"PRIVMSG {channel} :{''.join(results)}")

    def run(self):
        """Start the bot."""
        try:
            self.connect()
            self.receive()
        except KeyboardInterrupt:
            loggit("Disconnecting...")
            self.sock.close()
            sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="A simple IRC bot.")
    parser.add_argument("--server", required=True, help="IRC server to connect to")
    parser.add_argument(
        "--port", type=int, default=6667, help="Port to connect to (default 6667)"
    )
    parser.add_argument("--channel", required=True, help="Channel to join")
    parser.add_argument("--nick", default="foxbot", help="Bot nickname")
    parser.add_argument("--password", help="Optional password for server or channel")
    args = parser.parse_args()

    plugin_manager = PluginManager()
    plugin_manager.load_plugins()

    bot = Foxbot(
        args.server, args.port, args.channel, args.nick, plugin_manager, args.password
    )
    bot.run()
