#!/usr/bin/env python

"""An object to store/access results associated with Bandit tests."""

from collections import OrderedDict
import linecache
from sys import stdout
from datetime import datetime

import utils


class BanditResultStore():
    resstore = OrderedDict()
    count = 0
    skipped = None

    def __init__(self, logger):
        self.count = 0
        self.skipped = []
        self.logger = logger

    def skip(self, filename, reason):
        self.skipped.append((filename, reason))

    def add(self, context, issue):
        filename, lineno = context['filename'], context['lineno']
        (issue_type, issue_text) = issue
        if filename in self.resstore:
            self.resstore[filename].append((lineno, issue_type, issue_text))
        else:
            self.resstore[filename] = [(lineno, issue_type, issue_text), ]
        self.count += 1

    def report(self, scope, lines=0, level=1, output_filename=None):
        is_tty = False if output_filename is not None else stdout.isatty()

        if level >= len(utils.sev):
            level = len(utils.sev) - 1
        tmpstr = ""
        if is_tty:
            tmpstr += "%sRun started:%s\n\t%s\n" % (
                utils.color['HEADER'],
                utils.color['DEFAULT'],
                datetime.utcnow()
            )
        else:
            tmpstr += "Run started:\n\t%s\n" % datetime.utcnow()
        if self.count > 0:
            if is_tty:
                tmpstr += "%sFiles tested (%s):%s\n\t" % (
                    utils.color['HEADER'], len(scope),
                    utils.color['DEFAULT']
                )
            else:
                tmpstr += "Files tested (%s):\n\t" % (len(scope))

            tmpstr += "%s\n" % "\n\t".join(scope)

            if is_tty:
                tmpstr += "%sFiles skipped (%s):%s" % (
                    utils.color['HEADER'], len(self.skipped),
                    utils.color['DEFAULT']
                )
            else:
                tmpstr += "Files skipped (%s):" % len(self.skipped)

            for (fname, reason) in self.skipped:
                tmpstr += "\n\t%s (%s)" % (fname, reason)

            if is_tty:
                tmpstr += "\n%sTest results:%s\n" % (
                    utils.color['HEADER'], utils.color['DEFAULT']
                )
            else:
                tmpstr += "Test results:\n"

            for filename, issues in self.resstore.items():
                for lineno, issue_type, issue_text in issues:
                    if utils.sev.index(issue_type) >= level:
                        if is_tty:
                            tmpstr += "%s>> %s\n - %s::%s%s\n" % (
                                utils.color.get(
                                    issue_type, utils.color['DEFAULT']
                                ),
                                issue_text, filename, lineno,
                                utils.color['DEFAULT']
                            )
                        else:
                            tmpstr += ">> %s\n - %s::%s\n" % (
                                issue_text, filename, lineno
                            )
                        for i in utils.mid_range(lineno, lines):
                            line = linecache.getline(filename, i)
                            # linecache returns '' if line does not exist
                            if line != '':
                                tmpstr += "\t%3d  %s" % (
                                    i, linecache.getline(filename, i)
                                )
            if output_filename is not None:
                with open(output_filename, 'w') as fout:
                    fout.write(tmpstr)
                print("Output written to file: %s" % output_filename)
            else:
                print(tmpstr)

        else:
            self.logger.error("no results - %s files scanned" % self.count)