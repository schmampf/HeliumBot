from re import search, match


def notifications_arg_handler(args):
    arguments = {"notifications": None, "alarm": None, "refresh_rate": None, "level": None}
    description = "/notify arguments, separated by ' ' and followed by:\n"
    description = description + "n|notify|notifications:1|True|0|False\n"
    description = description + "al|alarm:1|True|0|False\n"
    description = description + "rr|refresh_rate:3600 #s\n"
    description = description + "lv|level:17.5 #L"

    substrings = args.split(" ")
    for substring in substrings:
        n = match(r"(n|notify|notifications)(.*)", substring)
        if n is not None:
            arguments["notifications"] = bool(eval(search(r":(.*)", n.group()).group()[1:]))

        a = match(r"(al|alarm)(.*)", substring)
        if a is not None:
            arguments["alarm"] = bool(eval(search(r":(.*)", a.group()).group()[1:]))

        rr = match(r"(rr|refresh_rate)(.*)", substring)
        if rr is not None:
            arguments["refresh_rate"] = float(search(r":(.*)", rr.group()).group()[1:])

        al = match(r"(lv|level)(.*)", substring)
        if al is not None:
            arguments["level"] = float(search(r":(.*)", al.group()).group()[1:])
    return arguments, description


"""
# Test
notification_arg_handler('refresh_rate:01.4 al:22.32 a:1 n:1')
"""


def plot_arg_handler_scheer_2(args):
    arguments = {"time": None, "before": None, "y_zoom": None, "consumption": None}

    description = "/plot arguments, separated by ' ' and followed by:\n"
    description = description + "h|t|hour|time:24 #h\n"
    description = description + "bf|before:12 #h\n"
    description = description + "c|con|consumption:1|True|0|False\n"
    description = description + "y|yzoom|y_zoom:1|True|0|False"

    substrings = args.split(" ")
    for substring in substrings:
        y = match(r"(y|yzoom|y_zoom)(.*)", substring)
        if y is not None:
            arguments["y_zoom"] = bool(eval(search(r":(.*)", y.group()).group()[1:]))

        c = match(r"(c|con|consumption)(.*)", substring)
        if c is not None:
            arguments["consumption"] = bool(eval(search(r":(.*)", c.group()).group()[1:]))

        h = match(r"(h|t|hour|time)(.*)", substring)
        if h is not None:
            arguments["time"] = float(search(r":(.*)", h.group()).group()[1:])

        bf = match(r"(bf|before)(.*)", substring)
        if bf is not None:
            arguments["before"] = float(search(r":(.*)", bf.group()).group()[1:])
    return arguments, description
