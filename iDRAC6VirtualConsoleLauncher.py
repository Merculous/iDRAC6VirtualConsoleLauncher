#!/usr/bin/env python3

import os
import subprocess
import sys
from argparse import ArgumentParser
from urllib.request import urlopen, urlretrieve
from zipfile import ZipFile


def checkForLibs(address: str) -> None:

    data = {
        'linux': {
            'platform': 'Linux64',
            'dynlibex': '.so'
        },
        'win': {
            'platform': 'Win64',
            'dynlibex': '.dll'
        },
        'darwin': {
            'platform': 'Mac64',
            'dynlibex': '.jnilib'
        }
    }

    if not os.path.exists('lib'):
        os.makedirs('lib')

    if not os.path.exists('jre/bin'):
        os.makedirs('jre/bin')

    # Figure out which libraries we need to pull from our server

    for system in data:
        if sys.platform.startswith(system):

            names = (
                'avctVM{}.jar'.format(data[system]['platform']),
                'avctKVMIO{}.jar'.format(data[system]['platform']),
                'avctKVM.jar'
            )

            for name in names:
                url = 'http://{}/software/{}'.format(address, name)

                # Check if the files exist

                try:
                    urlopen(url)
                except Exception:
                    print('Something went wrong reading server files!')
                    raise

                base = os.path.basename(url)
                path = 'lib/{}'.format(base)

                if not os.path.exists(path):
                    print('Downloading: {}'.format(base))
                    urlretrieve(url, path)

                if data[system]['platform'] in path:
                    with ZipFile(path) as f:
                        files = f.namelist()
                        for lib in files:
                            if lib.endswith(data[system]['dynlibex']):
                                lib_file = 'lib/{}'.format(lib)
                                if not os.path.exists(lib_file):
                                    with open(lib_file, 'wb') as ff:
                                        file_data = f.read(lib)
                                        ff.write(file_data)


def launch(username: str, password: str, address: str, port: int) -> None:

    ########

    checkForLibs(address)

    ########

    java_path = 'jre/bin/java'

    if sys.platform.startswith('win'):
        java_path = java_path + '.exe'

    cmd = (
        java_path,  # java 8 path (I have mine symlinked)
        '-cp',
        'lib/avctKVM.jar',
        '-Djava.library.path=lib',
        'com.avocent.idrac.kvm.Main',
        'ip={}'.format(address),
        'kmport={}'.format(port),
        'vport={}'.format(port),
        'user={}'.format(username),
        'passwd={}'.format(password),
        'apcp=1',
        'version=2',
        'vmprivilege=true',
        '"helpurl=https://{}/help/contents.html"'.format(address)
    )

    subprocess.run(cmd)


def main() -> None:
    parser = ArgumentParser(
        description='iDRAC 6 Virtual Console Launcher'
    )

    parser.add_argument('--username', nargs=1, type=str, metavar='\b')
    parser.add_argument('--password', nargs=1, type=str, metavar='\b')
    parser.add_argument('--address', nargs=1, type=str, metavar='\b')
    parser.add_argument('--port', nargs=1, type=int, metavar='\b')

    args = parser.parse_args()

    if args.username and args.password and args.address:

        if args.port:
            port = args.port[0]
        else:
            port = 5900

        launch(args.username[0], args.password[0], args.address[0], port)

    else:
        sys.exit(parser.print_help(sys.stderr))


if __name__ == '__main__':
    main()
