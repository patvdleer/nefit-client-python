import time
import sys
import signal

from nefit import NefitClient

try:
    import argparse
except ImportError:
    print("The Python module argparse is required")
    sys.exit(1)


class CLI:
    nefit_client = None

    @staticmethod
    def sig_handler(signum=None, frame=None):
        if signum is not None:
            pass

    def __init__(self):
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

        self.parser = parser = argparse.ArgumentParser(
            description='Nefit client',
            prog="Nefit client",
            usage='%(prog)s [options]'
        )
        parser.add_argument("--serial", help='Serial, 9 number digit')
        parser.add_argument("--access-key", dest="access_key", help='Access key, 12 long')
        parser.add_argument("--password", help='Password, usually postalcode + housenumber')
        parser.add_argument("--status", help="Status", action="store_true")
        parser.add_argument("--display-code", dest="display_code", help="Display code", action="store_true")
        parser.add_argument("--set-temperature", dest="set_temperature", help="Display code", type=float)
        parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
        parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    def parse(self, args=None):
        args = self.parser.parse_args(args)
        return args

    def run(self):
        args = self.parse()

        if args.verbose:
            NefitClient.set_verbose()

        client = NefitClient(args.serial, args.access_key, args.password)
        client.connect()

        if args.status:
            for k, v in client.get_status().items():
                if isinstance(v, bool):
                    print("%s: %s" % (k, "Yes" if v else "No"))
                else:
                    print("%s: %s" % (k, v))
        if args.display_code:
            print(client.get_display_code())

        if args.set_temperature:
            client.set_temperature(args.set_temperature)
            print("Temperature set to %3.1f" % args.set_temperature)

        client.disconnect()

if __name__ == "__main__":
    cli = CLI()
    cli.run()
