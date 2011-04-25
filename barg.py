#!/usr/bin/python
# -*- coding: utf-8 -*-

# barg.py - barg - create simple ASCII bar graphs from CSV data
#
# Copyright (C) 2011, Stefan Schramm <mail@stefanschramm.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

# concept:
# barg -l 0 -l 1 -b 1 -l 2 -b 2
# -l: label
# -b: bar (value must be convertible to float)
# TODO: how to cope with negative values? is determining the minimum neccessary or can we simply assume 0?

def terminal_size():
    """
    returns (lines:int, cols:int)
    """
    # taken from http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    import os, struct
    def ioctl_GWINSZ(fd):
        import fcntl, termios
        return struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
    # try stdin, stdout, stderr
    for fd in (0, 1, 2):
        try:
            return ioctl_GWINSZ(fd)
        except:
            pass
    # try os.ctermid()
    try:
        fd = os.open(os.ctermid(), os.O_RDONLY)
        try:
            return ioctl_GWINSZ(fd)
        finally:
            os.close(fd)
    except:
        pass
    # try `stty size`
    try:
        return tuple(int(x) for x in os.popen("stty size", "r").read().split())
    except:
        pass
    # try environment variables
    try:
        return tuple(int(os.getenv(var)) for var in ("LINES", "COLUMNS"))
    except:
        pass
    # i give up. return default.
    return (25, 80)

# defaults
filename = None
delimiter = "\t"
barchar = "|"
autodetect = False
(con_height, con_width) = terminal_size()

bars = []
labels = []
columntypes = []

# parse command line arguments, syntax check
args = iter(sys.argv[1:])
while True:
    try:
        arg = args.next()
    except StopIteration:
        break
    if arg == '-w':
        # graph width (instead of terminal width)
        try:
            con_width = int(args.next())
            continue
        except StopIteration:
            sys.exit("Missing argument for -w (filename)")
        except ValueError:
            sys.exit("Invalid argument for -w (must be numeric!)")
    if arg == '-f':
        # filename
        try:
            filename = args.next()
            continue
        except StopIteration:
            sys.exit("Missing argument for -f (filename)")
    if arg == '-d':
        # delimiter
        try:
            delimiter = args.next()
            continue
        except StopIteration:
            sys.exit("Missing argument for -d (field delimiter)")
    if arg == '-c':
        # bar character
        try:
            barchar = args.next()
            continue
        except StopIteration:
            sys.exit("Missing argument for -c (bar character)")
    if arg == '-a':
        # use autodetection
        autodetect = True
        continue
    if arg == '-b':
        # bar
        try:
            bars.append(int(args.next()))
            columntypes.append("b");
            continue
        except StopIteration:
            sys.exit("Missing argument for -b (column number)")
        except ValueError:
            sys.exit("Invalid argument for -b (must be numeric!)")
    if arg == '-l':
        # label column
        try:
            labels.append(int(args.next()))
            columntypes.append("l");
            continue
        except StopIteration:
            sys.exit("Missing argument for -l (column number)")
        except ValueError:
            sys.exit("Invalid argument for -l (must be numeric!)")
    sys.exit("Unknown option: " + arg)

# determine data source (file or stdin)
if filename != None and filename != "-":
    try:
        lines = open(filename)
    except IOError:
        sys.exit("IOError: Unable to open " + filename + " for reading")
else:
    lines = sys.stdin

# read lines
data = []
for line in lines:
    fields = line.rstrip().split(delimiter)
    data.append(fields)

# autodetection of columntypes
if autodetect:
    if labels != [] or bars != []:
        sys.exit("Error: Cannot use -a (autodetection) in combination with -l or -b.")
    labels = []
    bars = []
    numeric = range(0,len(data[0]))
    for fields in data:
        for i in numeric:
            try:
                float(fields[i])
            except ValueError:
                numeric.remove(i)
    for i in range(0,len(data[0])):
        columntypes.append("l")
        labels.append(i)
        if i in numeric:
            columntypes.append("b")
            bars.append(i)

# get maximum values and lengths
max_bar_value = {}
max_label_length = {}
for fields in data:
    for bar in bars:
        try:
            if not max_bar_value.has_key(bar) or float(fields[bar]) > max_bar_value[bar]:
                try:
                    max_bar_value[bar] = float(fields[bar])
                except ValueError:
                    sys.exit("ValueError: Unable to convert value of field in column " + str(bar) + " to float.")
        except IndexError:
                sys.exit("IndexError: Column " + str(bar) + " doesn't seem to exist.")
    for label in labels:
        try:
            if not max_label_length.has_key(label) or len(fields[label]) > max_label_length[label]:
                max_label_length[label] = len(fields[label])
        except IndexError:
            sys.exit("IndexError: Column " + str(label) + " doesn't seem to exist.")

max_label_length_sum = reduce(lambda s, l: s + max_label_length[l] + 1, labels, 0)

max_bar_width = (con_width - max_label_length_sum) / len(bars) - 1 if len(bars) > 0 else 0

# output
for row in data:
    l = 0
    b = 0
    for ct in columntypes:
        if ct == "l":
            label = labels[l]
            sys.stdout.write(row[label] + " " * (max_label_length[label] - len(row[label])) + " ")
            l += 1
        if ct == "b":
            bar = bars[b]
    	    bar_width = int((float(row[bar]) / max_bar_value[bar]) * max_bar_width)
            sys.stdout.write(barchar * bar_width + " " * (max_bar_width - bar_width) + " ")
            b += 1
    print

