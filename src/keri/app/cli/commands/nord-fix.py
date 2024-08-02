# -*- encoding: utf-8 -*-
"""
KERI
keri.kli.commands module

"""
import argparse

from hio import help
from hio.base import doing

from keri.app.cli.common import existing
from keri.kering import ConfigurationError

logger = help.ogler.getLogger()

parser = argparse.ArgumentParser(description='Fix NordLEI database')
parser.set_defaults(handler=lambda args: handler(args),
                    transferable=True)
parser.add_argument('--name', '-n', help='keystore name and file location of KERI keystore', required=True)
parser.add_argument('--base', '-b', help='additional optional prefix to file location of KERI keystore',
                    required=False, default="")
parser.add_argument('--passcode', '-p', help='22 character encryption passcode for keystore (is not saved)',
                    dest="bran", default=None)  # passcode => bran
parser.add_argument('--force', action="store_true", required=False,
                    help='True means perform fix without prompting the user')


def handler(args):
    if not args.force:
        print()
        print("This command will remove entries from your reply database that have no corresponding eans entry.")
        print("This action cannot be undone.")
        print()
        yn = input("Are you sure you want to continue? [y|N]: ")

        if yn not in ("y", "Y"):
            print("...exiting")
            return []

    kwa = dict(args=args)
    return [doing.doify(fix, **kwa)]


def fix(tymth, tock=0.0, **opts):
    _ = (yield tock)
    args = opts["args"]
    name = args.name
    base = args.base
    bran = args.bran

    try:
        with existing.existingHby(name=name, base=base, bran=bran) as hby:
            print(hby.db.path)
            to_delete = []
            for k, v in hby.db.eans.getItemIter():
                if hby.db.rpys.get(keys=(v.qb64,)) is None:
                    to_delete.append(k)

            print(f"Removing {to_delete}")

            for k in to_delete:
                hby.db.eans.rem(k)

    except ConfigurationError:
        print(f"identifier prefix for {name} does not exist, incept must be run first", )
        return -1
