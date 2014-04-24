"""Utilities for notetaker.
- count_lines: Takes a string, length returns approximate number of lines."""

def count_lines(line, wanted_length=77):
    """Returns an approximate line count gives a string"""
    lines = line.split("\n")
    count = len(lines) - 1
    for row in lines:
        length = len(row)/wanted_length
        if length < 1.0:
            continue
        count += int(length)
    return count
