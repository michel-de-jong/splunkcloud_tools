#!/usr/bin/env python3

"""
This script will take a Splunk app package and fix some common packaging mistakes, including:

  * Removes PAX headers
  * Removes macOS ._ files
  * Fix packages created with `tar czf package.tar.gz ./appname` instead of `tar czf package.tar.gz appname`
  * Forces uid/gid to 0 instead of whatever the owner uid/gid was on the source system
  * Fixes permissions on files and directories
"""

import argparse
import gzip
import os
import shutil
import tarfile
import tempfile


ap = argparse.ArgumentParser()
ap.add_argument("--dry-run", action="store_true", default=False)
ap.add_argument("file")
args = ap.parse_args()


if not os.path.isfile(args.file):
    print(f"{args.file} is not a file")
    exit()

with open(args.file, "rb") as f:
    magic = f.read(2)

if magic != b"\x1f\x8b":
    print("Not a gzip file")
    exit()


with gzip.GzipFile(args.file, "rb") as fo1:
    with tarfile.TarFile(fileobj=fo1) as tf1:
        with tempfile.NamedTemporaryFile(delete=False) as outfile:
            with gzip.GzipFile(fileobj=outfile.file, mode="w") as fo2:
                with tarfile.TarFile(fileobj=fo2, mode="w", format=tarfile.USTAR_FORMAT) as tf2:
                    app_dir = None

                    for m in tf1.getmembers():
                        ###
                        # Remove PAX headers for older/non-POSIX tar implementations
                        ###
                        if m.pax_headers:
                            print(f"Removing PAX headers for {m.name}")
                            m.pax_headers = {}

                        ###
                        # Remove ._ files created on macOS
                        ###
                        if m.name.startswith("._") or os.path.basename(m.name).startswith("._"):
                            print(f"Removing macOS ._ file {m.name}")
                            continue

                        ###
                        # Fix tar files created with `tar czf package.tar.gz ./appname`
                        ###
                        if m.name.startswith("./"):
                            m.name = m.name[2:]

                        # Figure out what the app directory is based on the first entry in the tarball
                        if app_dir is None:
                            if "/" in m.name:
                                app_dir, _ = m.name.split("/", 1)
                            else:
                                app_dir = m.name

                        ###
                        # Bail if there's a local directory, or a local.meta file
                        ###
                        if m.name.startswith(f"{app_dir}/local") or m.name == f"{app_dir}/meta/local.meta":
                            print(f"ERROR: local path ({m.name}) found. Unable to correct this.")
                            exit()

                        ###
                        # Force the uid/gid to 0 instead of whatever was given to us
                        ###
                        m.uid = m.gid = 0

                        ###
                        # Normalize permissions
                        ###
                        if m.type == tarfile.DIRTYPE or (m.name.startswith(f"{app_dir}/bin") and not m.name.endswith("/README")):
                            if m.mode != 0o755:
                                print(f"Fixing perms on {m.name} to 755 (was {oct(m.mode)})")
                                m.mode = 0o755
                        else:
                            if m.mode != 0o644:
                                print(f"Fixing perms on {m.name} to 644 (was {oct(m.mode)})")
                                m.mode = 0o644

                        mf = tf1.extractfile(m)
                        tf2.addfile(m, mf)

        if not args.dry_run:
            base, _, ext = args.file.rpartition(".")
            fn2 = f"{base}-fixed.{ext}"
            shutil.move(outfile.name, fn2)