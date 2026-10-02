#!/usr/bin/env python
import gzip
import os
import re
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from io import BytesIO
from tarfile import TarFile

import requests

ROOT_DIR = Path(os.path.realpath(__file__)).parent.parent
MINIFY_PATH = ROOT_DIR / 'scripts' / 'minify.ts'

def semantic_version_validator(version: str) -> str:
    if not re.match(r'^[0-9]+[.][0-9]+[.][0-9]+$', version):
        print("completed")
        raise ValueError("Must be a valid semantic version")
    return version

def openedx_version_validator(version: str) -> str:
    version = version.lower()
    if not re.match(r'^[a-z]+$', version):
        raise ValueError('Must be a valid version codename like "willow" or "verawood"')
    return version

parser = ArgumentParser(
    prog='React Munger for xblock-asset-snapshots',
    description='Fetches a given version of react, modifies it, minifies it, and '
                'places it in the appropriate directory.'
)
parser.add_argument(
    'react_version',
    help='The version of React to pull from NPM',
    type=semantic_version_validator,
)
parser.add_argument(
    'platform_version',
    help='The version of the platform, such as "verawood" or "willow" to compile the React version for.',
    type=openedx_version_validator,
)


def react_directory(version: str) -> Path:
    """
    Given a version, return the directory that the React package will be located in the scratch directory.
    """
    return Path(ROOT_DIR / 'scratch' / 'react' / version)

def react_scratch_path(version: str) -> Path:
    """
    Given a version, return the path to the React scratch file we're working with.
    """
    return react_directory(version) / 'react.js'


def pull_react(version: str) -> None:
    """
    Download a specific React version and pull the relevant file.
    """
    print(f"Downloading React {version}...")
    directory = react_directory(version)

    result = requests.get(f'https://registry.npmjs.org/react/-/react-{version}.tgz')
    result.raise_for_status()
    tarball = TarFile(fileobj=BytesIO(gzip.decompress(result.content)))
    to_save = tarball.extractfile('package/cjs/react.production.min.js')

    Path.mkdir(directory, parents=True, exist_ok=True)
    with open(directory / 'react.js', 'wb') as result:
        result.write(to_save.read())


def munge_react(version: str) -> None:
    """
    Convert the CommonJS version to a single-file, browser-compatible ECMAScript module.
    """
    print("Converting react to a single-file ECMAScript module...")
    react_path = react_directory(version) / 'react.js'
    with open(react_path) as original:
        react_lines = original.readlines()
    revised_lines = []
    declared_constants = []
    # exports.useMemo = function (a, b) {
    const_regex = re.compile(r'^(exports[.]([^ ]+))')
    for line in react_lines:
        if match := const_regex.match(line):
            declared_constants.append(match[2])
            line = const_regex.sub('export const \\2', line)
        revised_lines.append(line)
    revised_lines.append("export default {" + ",".join(declared_constants) + "}")
    with open(react_path, 'w') as revised:
        revised.write(''.join(revised_lines))


def prettify_react(version: str) -> None:
    print("Formatting downloaded React version...")
    subprocess.run(['pnpm', 'exec', 'oxfmt', str(react_directory(version) / 'react.js')])


def minify_react(version: str) -> None:
    print("Minifying munged React version...")
    subprocess.run([str(MINIFY_PATH), str(react_directory(version) / 'react.js')])


def install_react(react_version: str, platform_version: str) -> None:
    print(f"Installing React version {react_version} into public directory for platform version {platform_version}")
    target_directory = ROOT_DIR / 'src' / 'xblock_asset_snapshots' / 'public' / platform_version
    Path.mkdir(target_directory, parents=True, exist_ok=True)
    os.replace(
        react_directory(react_version) / 'react.js',
        target_directory / 'react.js',
    )


if __name__ == '__main__':
    args = parser.parse_args()
    pull_react(args.react_version)
    prettify_react(args.react_version)
    munge_react(args.react_version)
    minify_react(args.react_version)
    install_react(args.react_version, args.platform_version)