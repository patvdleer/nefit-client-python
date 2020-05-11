import os
import sys
import signal

from nefit import NefitClientCli
from nefit import version

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
            sys.exit(signum)

    def __init__(self):
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

        self.parser = parser = argparse.ArgumentParser(
            description='Nefit client',
            prog="Nefit client",
            usage='%(prog)s [options]'
        )

        parser.add_argument(
            "--serial",
            help='Serial, 9 number digit',
            default=os.environ.get("NEFIT_SERIAL"),
            required=True
        )
        parser.add_argument(
            "--access-key",
            dest="access_key",
            help='Access key, 12 long',
            default=os.environ.get("NEFIT_ACCESS_KEY"),
            required=True
        )
        parser.add_argument(
            "--password",
            help='Password, usually postalcode + housenumber',
            default=os.environ.get("NEFIT_PASSWORD"),
            required=True
        )
        parser.add_argument("--status", help="Status", action="store_true")
        parser.add_argument("--display-code", dest="display_code", help="Display code", action="store_true")
        parser.add_argument("--location", help="Display location", action="store_true")
        parser.add_argument("--outdoor", help="Display outdoor", action="store_true")
        parser.add_argument("--pressure", help="Display pressure", action="store_true")
        parser.add_argument("--program", help="Display program", action="store_true")
        parser.add_argument("--actual", help="Display actual supply temperature", action="store_true")
        parser.add_argument(
            "--get-year-total",
            dest="year_total",
            help="Display the current total gas usage",
            action="store_true"
        )
        parser.add_argument("--set-temperature", dest="set_temperature", help="Display code", type=float)
        parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
        parser.add_argument('--version', action='version', version='%(prog)s '+version)

    def parse(self, args=None):
        args = self.parser.parse_args(args)
        return args

    def run(self):
        args = self.parse()

        if args.verbose:
            NefitClientCli.set_verbose()

        client = NefitClientCli(args.serial, args.access_key, args.password)
        client.connect()

        if args.status:
            print(client.get_status())

        if args.display_code:
            print(client.get_display_code())

        if args.location:
            print(client.get_location())

        if args.outdoor:
            print(client.get_outdoor())

        if args.pressure:
            print(client.get_pressure())

        if args.program:
            print(client.get_program())

        if args.actual:
            print(client.get_actualSupplyTemperature())

        if args.year_total:
            print(client.get_year_total())

        if args.set_temperature:
            client.set_temperature(args.set_temperature)
            print("Temperature set to %3.1f" % args.set_temperature)

        client.disconnect()


def main():
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
