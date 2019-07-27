#!/usr/bin/env python3

import os, sys

if __name__ == "__main__":

    if len(sys.argv) != 5:
        sys.stderr.write("Usage: %s <output directory> <key file> "
            "<certificate file> <package file>\n" % sys.argv[0])
        sys.exit(1)

from DUCK.Tools import makeresources, makeandroidmanifest, makepackage

app_name = "Hello"
package_name = "python.hello"
class_name = "android.PythonActivity"

features = []
permissions = []
output_dir = sys.argv[1]

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

key_file, cert_file, package_file = sys.argv[2:]

res_files = {"drawable": {"ic_launcher": "icon.svg"}}
sdk_version = 4
version = "1.0"

res_info = makeresources.create_file(".", app_name, package_name, res_files,
    os.path.join(output_dir, "resources.arsc"), sdk_version=sdk_version)

manifest_desc = {"package": package_name, "android:versionName": version}

manifest = makeandroidmanifest.create_activity_manifest(
    package_name, class_name, manifest_desc, activity_desc = {})

manifest_file = os.path.join(output_dir, "AndroidManifest.xml")

makeandroidmanifest.create_file(manifest, res_info, features, permissions,
                                manifest_file, sdk_version)

makepackage.create_file(output_dir, key_file, cert_file, package_file)
