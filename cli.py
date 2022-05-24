#! /usr/bin/env python3

# need sys to grab args
import sys

from springboard.entry import EntryPoint

# Helper debug script to test without having to compile


def main():
    dothething = EntryPoint()
    dothething.run(*sys.argv[1:])

# main, bro.
if __name__ == "__main__":
    main()
