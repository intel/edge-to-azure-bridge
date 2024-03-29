# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: MIT

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Python script to serialize the EII ETCD pre-load JSON file into the Azure
IoT Edge deployment manifest template.
"""
import os
import json
import argparse
import sys


# Parse command line arguments
ap = argparse.ArgumentParser()
ap.add_argument('manifest', help='Azure manifest template')
ap.add_argument('config', help='EII pre-load configuration path')
args = ap.parse_args()

# Verify arguments (Prevent path traversal per Checkmarx recommendation)
if not isinstance(args.config, str):
    raise AssertionError('{} is not a path string'.format(args.config))
else:
    argConfig = args.config
if not isinstance(args.manifest, str):
    raise AssertionError('{} is not a path string'.format(args.manifest))
else:
    argManifest = args.manifest

# Verify the input files exist
if not os.path.exists(argConfig):
    raise AssertionError('{} does not exist'.format(argConfig))
if not os.path.exists(argManifest):
    raise AssertionError('{} does not exist'.format(argManifest))

print('[INFO] Populating EII configuration into Azure manifest')


def is_safe_path(basedir, path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((basedir, matchpath))

# Load JSON files
with open(argConfig, 'r') as f:
    config = json.load(f)

with open(argManifest, 'r') as f:
    manifest = json.load(f)

# Serialize and populate the manifest
config_str = json.dumps(config)
eii_azure_bridge = manifest['modulesContent']['edge_to_azure_bridge']
eii_azure_bridge['properties.desired']['eii_config'] = config_str

if is_safe_path(os.getcwd(), argManifest):
    with open(argManifest, 'w') as f:
        json.dump(manifest, f, indent=4)

print('[INFO] Azure manifest populated')
