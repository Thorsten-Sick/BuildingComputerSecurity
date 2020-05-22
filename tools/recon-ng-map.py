#!/usr/bin/env python3

# recon-ng is a OSI hacking tool with lots of modules.
# Those modules generate data from one data-item to the next
# (stupid example host-to-emails: scan a host for email addresses)
# By concating the modules in a smart way the user can get from anywhere
# to anywhere else.
# At least I assume so.
# This tool generates a "subway map" for recon-ng modules

import subprocess

res = 'digraph G {\nsize="200,200"\nnodesep="2"\n'

cmpl = subprocess.run(['recon-cli', '-C', 'show modules'], capture_output = True, text=True)
for aline in cmpl.stdout.split("\n"):
    if "    recon/" in aline:
        aline = aline.replace("    recon/","")
        ft, tool = aline.split("/", 1)
        frm, to = ft.split("-")
        print("{}  does  {} -> {}".format(tool, frm, to))
        res += '{} -> {} [label = "{}"]\n'.format(frm, to, tool)

res += "}\n"

with open("recon_map.dot", "wt") as fh:
    fh.write(res)

cmpl = subprocess.run(['dot', '-T', 'svg', 'recon_map.dot'], capture_output=True, text=True)
with open('recon_map.svg', "wt") as fh:
    fh.write(cmpl.stdout)
