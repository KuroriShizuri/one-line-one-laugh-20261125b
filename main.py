#!/usr/bin/env python3
"""One Line, One Laugh — emit the funny line into entry.txt.

Usage:
    python3 main.py                write entry.txt (into $MAKEFUN_OUTPUT_DIR
                                   when set, else the current directory)
    python3 main.py --check        validate the line, write nothing
    python3 main.py --self-test    run the built-in checks

The line is the whole entry: one funny line, at most 200 characters.
The program checks the length before writing and then checks the file
it just wrote, so a bad line can never slip through silently.
"""

import os
import sys
import tempfile

LINE = "My smart fridge emailed me about my eating habits, so now even my leftovers judge me."

CHAR_MAX = 200


def die(message):
    sys.stderr.write("error: %s\n" % message)
    return 1


def line_problems(text):
    """Return gate violations for `text`, or an empty list when it is legal."""
    problems = []
    if text.strip() == "":
        problems.append("line is blank")
    if text != text.strip():
        problems.append("line has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        problems.append("line must be a single line")
    if len(text) < 1 or len(text) > CHAR_MAX:
        problems.append(
            "line is %d characters, allowed 1-%d" % (len(text), CHAR_MAX)
        )
    return problems


def do_check():
    bad = line_problems(LINE)
    if bad:
        for item in bad:
            sys.stderr.write("check failed: %s\n" % item)
        return 1
    sys.stdout.write("check ok: %d characters\n" % len(LINE))
    return 0


def do_write(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(LINE + "\n")
    with open(path, encoding="utf-8") as handle:
        saved = handle.read()
    if saved != LINE + "\n":
        return die("entry.txt does not match the line")
    bad = line_problems(saved[:-1])
    if bad:
        for item in bad:
            sys.stderr.write("check failed: %s\n" % item)
        return 1
    if len(saved) > CHAR_MAX + 1:
        return die("entry.txt is longer than the gate allows")
    sys.stdout.write("wrote %s\n" % path)
    return 0


def do_self_test():
    if do_check():
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        if do_write(tmp):
            return 1
        with open(os.path.join(tmp, "entry.txt"), encoding="utf-8") as handle:
            if handle.read() != LINE + "\n":
                return die("self-test: round-trip mismatch")
    for bad_line in ("", "  padded  ", "a" * (CHAR_MAX + 1), "one\ntwo"):
        if not line_problems(bad_line):
            return die("self-test: bad input accepted: %r" % bad_line[:20])
    sys.stdout.write("self-test ok\n")
    return 0


def main(argv):
    flags = set(argv)
    if "--help" in flags or "-h" in flags:
        sys.stdout.write(__doc__)
        return 0
    unknown = flags - {"--check", "--self-test"}
    if unknown:
        return die("unknown option: %s" % sorted(unknown)[0])
    if "--self-test" in flags:
        return do_self_test()
    if "--check" in flags:
        return do_check()
    return do_write(os.environ.get("MAKEFUN_OUTPUT_DIR", "."))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
