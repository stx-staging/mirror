#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

# Clone (or update) the repository
if os.path.isdir("statix_manifest"):
    print("Updating statix_manifest repository...")
    statix_manifest = git.Repo("statix_manifest")
    statix_manifest.remote("origin").fetch()
else:
    print("Downloading statix_manifest repository...")
    statix_manifest = git.Repo.clone_from("https://github.com/StatiXOS/android_manifest", "statix_manifest")

# Get all the refs
refs = [re.search(r'remotes/(\S+)', tag).group(1) for tag in statix_manifest.git.branch(a=True).splitlines() if "remotes/" in tag]

repos = set()

# Look for repo names in each ref
for index, ref in enumerate(refs, 1):
    print("[{}/{}] Parsing `{}`...".format(index, len(refs), ref))

    xml_todo = ['include.xml']

    # Load the XML
    while len(xml_todo) != 0:
        xml_name = xml_todo.pop(0)
        print("  - {}".format(xml_name))

        xml = ET.fromstring(statix_manifest.git.show("{}:{}".format(ref, xml_name)))

        for child in xml:
            if child.tag == "include":
                xml_todo.append(child.attrib["name"])
                continue

            # Skip all non-project tags
            if child.tag != "project":
                continue

            # Ignore non-Lineage projects
            if child.attrib["remote"] != "statix":
                continue

            repos.add("StatiXOS/" + child.attrib["name"])


file = open("statix-minimal.xml", "w")
file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
file.write("<manifest>\n")
file.write("\n")
file.write("  <remote  name=\"github\"\n")
file.write("           fetch=\"..\" />\n")
file.write("  <default revision=\"master\"\n")
file.write("           remote=\"github\"\n")
file.write("           sync-j=\"4\" />\n")
file.write("\n")

for repo in sorted(repos):
    file.write("  <project name=\"" + repo + "\" />\n")

file.write("</manifest>\n")
file.close()
