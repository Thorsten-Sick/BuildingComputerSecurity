#!/usr/bin/env python3

# Verify leanpub code
#

import os
import re
import requests
from collections import defaultdict
from pprint import pprint
import argparse
import json
import csv

class Link():
    def __init__(self, title, link, infile=None):
        """An outgoing link

        @infile: Name of the file the link is in
        """
        self.title = title
        self.link = link.strip() if link else None
        self.local = True if link.startswith("#") else False
        if infile:
            self.infile = str(infile)
        else:
            self.infile = None

    def is_reachable(self):
        try:
            res = requests.get(self.link)
        except UnicodeError:
            print("Error with link parsing {}".format(self.link))
        except requests.exceptions.SSLError:
            print("Error SSL Error in {}".format(self.link))
        except:
            print("Error Unkown connection error {}".format(self.link))
        else:
            if res.status_code == requests.codes.ok:
                return True
            else:
                return False
        return False

class Chapter():
    def __init__(self, title, link, level = 1, infile=None, part=None):
        """
        A major chapter in the book (one #).
        Later: With the level we can also handle other chapters.

        @title: The title of the chapter
        @link: a link to the chapter
        @level: The level of the chapter
        @infile: file of the chapter
        @part: part of the book the chapter iss in. As filename
        """
        self.title = title
        self.link = link.strip() if link else None
        self.level = level
        self.infile = infile
        self.part = part
        self.todos = 0
        self.words = 0

    def __str__(self):
        return "{}: {} {}".format(self.part,self.title, self.link)

    def setTodos(self, todos):
        """ Set todos in chapter """
        self.todos = todos

    def setWords(self, words):
        """
        @words: Number of words
        """
        self.words = words

    def getTodos(self):
        return self.todos

class LeanpubVerify():

    # common words
    common = ["","the","to","*","a","is","and","of","you","for","it",
              "your","in","are","can","be","not", "that","with","this",
              "on","will","if","have","there","do","more","they","but"]

    def __init__(self, basefile, basedir="../manuscript", verbose=False):
        self.basefile = basefile
        self.basedir = basedir
        self.chapterfiles = []
        self.chapters = []
        self.outgoingLinks = []
        self.webLinks = []
        self.wordstatistics = defaultdict(int)
        self.totalwords = 0
        self.verbose=verbose
        self.getBookFiles()
        self.getChapters()
        self.getOutgoingLinks()
        self.getWebLinks()

    def getBookFiles(self):
        """find all txt files in manuscriptdir"""
        self.chapterfiles = []

        with open(self.basefile) as fh:
            for line in fh:
                self.chapterfiles.append(line.strip())
        return self.chapterfiles

    def getChapters(self):
        """
        Go through all the books and extract the main chapters.
        """

        part = ""
        self.wordstatistics = defaultdict(int)
        self.totalwords = 0

        for afile in self.chapterfiles:
            if "/part_" in afile:
                part = afile.split("/")[1]
                part = part.replace("part_","").replace(".txt","")
            todos = 0
            chapterwords = 0
            newchapter=None
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    link = None
                    if line.startswith("#"):
                        level = 1
                        todos = 0
                        if line.startswith("# "):
                            level = 1
                        if line.startswith("## "):
                            level = 2
                        if line.startswith("### "):
                            level = 3
                        if line.startswith("#### "):
                            level = 4
                        if "{" in line:
                            title, link = line[level+1:].split("{")
                            link = link.replace("}","")
                        else:
                            title = line[level+1:]
                        title = title.strip()
                        newchapter = Chapter(title, link, level, afile, part)
                        self.chapters.append(newchapter)
                        if self.verbose:
                            print(newchapter)
                    todos += line.lower().count("todo:")
                    # wordstats
                    parts = re.split("\s|(?<!\d)[,.](?!\d)", line)
                    self.totalwords += len(parts)
                    chapterwords += len(parts)
                    for p in parts:
                        if not p.lower() in self.common:
                            self.wordstatistics[p.lower()] += 1

                    if newchapter:
                        newchapter.setTodos(todos)
                        newchapter.setWords(chapterwords)


    def checkChapters(self, up_to_level=1):
        """
        Check that chapters with the up_to_level and smaller have a link
        """

        for c in self.chapters:
            if c.level <= up_to_level:
                if c.link == None:
                    print("Error: Chapter has no link: {} ({})".format(c.title, c.infile))

    def checkLinksLocal(self):
        """Check if local links lead somewhere
        """

        for l in self.outgoingLinks:
            if l.local:
                good = False
                for c in self.chapters:
                    if c.link == l.link:
                        good = True
                if not good:
                    print("Error: Local link has no chapter: {}".format(l.link))

    def checkWebLinks(self):
        """Check web link

        All web links need a description
        """

        # TODO: web links must be reachable

        for l in self.webLinks:
            if not l.local:
                if not l.title:
                    print("Error: Web link has no description: {} ({})".format(l.link, l.infile))
            if not l.is_reachable():
                print("Error: Web link not reachable: {} ({})".format(l.link, l.infile))

    def getOutgoingLinks(self):
        """ Collect all link to somewhere
        """

        linkpattern = re.compile("\[(.*?)\]\((.*?)\)")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    matches = linkpattern.findall(line)
                    for a in matches:
                        if self.verbose:
                            print("{}->{}".format(a[0],a[1]))
                        self.outgoingLinks.append(Link(a[0], a[1]))

    def wordstats(self, filename = "wordstats.json"):
        """ Create word statistics """

        # TODO: Create nice word clouds
        # TODO: Statistics by chapter and in total !

        self.wordstatistics = defaultdict(int)
        self.totalwords = 0
        if self.verbose:
            print("Creating word statistics")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    parts = re.split("\s|(?<!\d)[,.](?!\d)", line)
                    self.totalwords += len(parts)
                    for p in parts:
                        if not p.lower() in self.common:
                            self.wordstatistics[p.lower()] += 1
        sorted_by_value = sorted(self.wordstatistics.items(), key=lambda kv: kv[1])
        pprint(sorted_by_value)
        print("Total words: %s".format(self.totalwords))
        data = {"total": self.totalwords,
                "distribution": self.wordstatistics}
        with open(filename, "wt") as fh:
            json.dump(data, fh, indent = 4)

    def todostats(self, filename = "todostats.json"):
        """ Print todos per chapter """

        data = defaultdict(defaultdict)
        for c in self.chapters:
            data[c.infile][c.title] = c.getTodos()
        with open(filename, "wt") as fh:
            json.dump(data, fh, indent = 4)

    def totalstats(self, filename="totalstats.csv"):
        """ Generate full statistics CSV file
        """
        for c in self.chapters:
            print ("{} {} {} {} {} {}".format(c.part, c.title, c.level, c.todos, c.words, c.link))

        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
            spamwriter.writerow(["part", "title", "level","todos", "words", "link"])
            for c in self.chapters:
                spamwriter.writerow([c.part, c.title, c.level, c.todos, c.words, c.link])

    def getWebLinks(self):
        """ Collect all web links
        """

        if self.verbose:
            print("Searching links")
        linkpattern = re.compile("(\[.*?\]\()?(?P<url>https?://[^\s]+)")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    matches = linkpattern.findall(line)
                    for a in matches:
                        desc = None
                        lnk = a[1]
                        if a[0]:
                            desc = a[0][1:][:-2]
                            if lnk.endswith("),"):
                                lnk = lnk[:-2]
                            if lnk.endswith(")."):
                                lnk = lnk[:-2]
                            if lnk.endswith(")"):
                                lnk = lnk[:-1]
                        if self.verbose:
                            print("{}->{}".format(desc, lnk))
                        self.webLinks.append(Link(desc, lnk, infile=afile))




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Checking the book-code for errors')
    parser.add_argument('--statistics', default=False, action="store_true", help="Create statistics")
    parser.add_argument('--alltests', default=False, action="store_true", help="Run all tests")
    parser.add_argument('--chaptertests', default=False, action="store_true", help="Chapter tests - tests consistency")
    parser.add_argument('--linktests', default=False, action="store_true", help="Check consistent structure of internal links")
    parser.add_argument('--weblinktests', default=False, action="store_true", help="Check if web pages are reachable")
    parser.add_argument('--verbose', default=False, action="store_true", help="Verbose output")


    args = parser.parse_args()

    lpbase="../manuscript/Book.txt"
    lpv = LeanpubVerify(lpbase, verbose=args.verbose)
    if args.alltests or args.chaptertests:
        lpv.checkChapters()
    if args.alltests or args.linktests:
        lpv.checkLinksLocal()
    if args.alltests or args.weblinktests:
        lpv.checkWebLinks()
    if args.statistics:
        lpv.wordstats()
        lpv.todostats()
        lpv.totalstats()
