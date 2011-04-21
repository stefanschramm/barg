#!/usr/bin/python
# -*- coding: utf-8 -*-

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

# get maximum values, lengths and collect data
data = []
max_bar_value = {}
max_label_length = {}
for line in lines:
    fields = line.rstrip().split(delimiter)
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
    data.append(fields)

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

