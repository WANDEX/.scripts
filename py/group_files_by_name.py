#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import pathlib
from os import sep, walk
from sys import stdout
from time import sleep
from itertools import count
from shutil import copyfile, move, rmtree
from re import split
from operator import itemgetter

l_fullpath = []
l_group = []
l_subdirs = []
dots = []
c_prefix = count()
c_file = count()
c_dir = count()
postfix_cp = "_cp"
postfix_mv = "_mv"


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=0,
        help="number of files to process.",
    )
    parser.add_argument(
        "-f",
        "--full",
        default=False,
        help="if specified, display the full path when copying.",
        action="store_true"
    )
    parser.add_argument(
        "-p",
        "--path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).absolute().parent,
        help="path to the source directory.",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=float,
        default=0.0,
        help="float number to wait between progress bar iterations, by def 0.0"
    )
    return parser.parse_args()


def dots_anim():
    """ Silly dots animation effect. """
    if len(dots) < 3:
        dots.append(".")
    else:
        dots.clear()
    return "".join(dots)


def progress_bar(count, total, status='', sleep_sec_float=0.0, bar_len=37):
    filled_len = int(round(bar_len * (count + 1) / float(total)))
    percents = round(100.0 * (count + 1) / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)
    stdout.write("\033[K")  # erase to end of line
    stdout.write("[{}] [{:^4}/{:^4}] {:>5}{} {}{}\r".format(
        bar, (count + 1), total, percents, '%', status, dots_anim())
    )
    stdout.flush()
    sleep(sleep_sec_float)


def sort_natural(l, key=itemgetter(1)):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda item: [convert(c) for c in split('([0-9]+)', key(item))]
    return l.sort(key=alphanum_key)


def validate_path(s_path):
    abs_path = pathlib.Path.absolute(s_path)
    if pathlib.Path.is_dir(abs_path):
        print("Provided path is directory:\n{0}".format(str(abs_path)))
    else:
        print("Provided path is not directory:\n{0}".format(str(abs_path)))
        print("Exiting.")
        quit()


def get_file_paths(s_path):
    d_fullpath = {}
    for (dirpath, dirnames, filenames) in walk(s_path):
        for filename in filenames:
            d_fullpath.update({dirpath + sep: filename})
            l_fullpath.extend(d_fullpath.items())
    sort_natural(l_fullpath)


def get_common_start(seq):
    if not seq:
        return ""
    s1, s2 = min(seq), max(seq)
    length = min(len(s1), len(s2))
    if length == 0:
        return ""
    for i in range(length):
        if s1[i] != s2[i]:
            return s1[0:i]
    return s1[0:length]


def count_words(str):
    c = 1
    for i in range(1, len(str) - 1):
        if (
                (str[i+1] and str[i] == "_") or
                (str[i+1] and str[i].isspace()) or
                (str[i+1] and str[i+1].isupper())
        ):
            c += 1
    return c


def str_filter(string):
    bad_chars = ["_", ";", ":", "!", ",", "*"]
    # numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    # bad_chars.extend(numbers)
    # string = string[:string.find(".")]  # remove all characters after "."
    l_filter = list(filter(lambda i: i not in bad_chars, string))
    filtered = str().join(l_filter)
    return filtered


def str_rstrip(string):
    bad_chars = ["_", " "]
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    bad_chars.extend(numbers)
    result = str().join(bad_chars)
    return string.rstrip(result)


def get_prefixes(f_list, l_output):
    d_group = {}
    previous_file = ""
    previous_prefix = ""
    for current_file in f_list:
        if previous_file:
            prev_with_curr = [previous_file[1], current_file[1]]
            current_prefix = str_rstrip(str(get_common_start(prev_with_curr)))
            if (
                (len(current_prefix) > len(previous_file[1]) // 2) and
                (len(previous_prefix) > len(current_prefix))
            ):
                d_group.update({previous_file: previous_prefix})
                d_group.update({current_file: current_prefix})
            elif len(current_prefix) >= len(previous_file[1]) // 2:
                d_group.update({previous_file: current_prefix})
                d_group.update({current_file: current_prefix})
            elif len(current_prefix) == len(previous_prefix):
                d_group.update({previous_file: current_prefix})
                d_group.update({current_file: current_prefix})
            elif len(current_prefix) <= len(previous_prefix):
                d_group.update({previous_file: previous_prefix})
                # last in group
                d_group.update({current_file: previous_prefix})
            else:
                # unique/uncaught files
                d_group.update({previous_file: "(unique)"})
                d_group.update({current_file:  "(unique)"})
            previous_prefix = current_prefix
        previous_file = current_file
        # progress_bar(next(c_prefix), len(f_list), "getting prefixes", _parse_args().sleep)
    l_output.extend(d_group.items())


def processed_files(range=0):
    """ Simple output message. """
    if range <= 0:
        range = len(l_fullpath)
    processed = "Number of files processed: {0}".format(str(range))
    total = "Total number of files in path: {0}".format(str(len(l_fullpath)))
    msg = "\n{0}\n{1}".format(processed, total)
    return msg


def file_loop(f_list, range=0):
    if range <= 0:
        get_prefixes(l_fullpath, l_group)
    else:
        get_prefixes(l_fullpath[:range], l_group)


def make_new_root_dir():
    old_path = pathlib.PurePath(_parse_args().path)
    new_dir_name = old_path.name + postfix_cp
    new_dir_path = old_path.parent.joinpath(new_dir_name)
    pathlib.Path(new_dir_path).mkdir(exist_ok=True)
    return new_dir_path


def file_copying(l_groups, show_full_path=False):
    width = 20
    new_dir_path = make_new_root_dir()
    print("\nNew dir path is:\n{0}\n".format(new_dir_path))
    for (path, group) in l_groups:
        width = len(group) if len(group) > width else width
        src_path = pathlib.PurePath("".join(path))
        dst_path = pathlib.PurePath.joinpath(new_dir_path, group, path[1])
        pathlib.Path(dst_path.parent).mkdir(parents=True, exist_ok=True)
        copyfile(src_path, dst_path)
        if show_full_path:
            print("dir: {:<{width}} file: {}".format(
                str(group), str(src_path), width=width)
            )
        else:
            print("dir: {:<{width}} file: {:<40}".format(
                str(group), str(src_path.name), width=width)
            )
        progress_bar(next(c_file), len(l_groups), "copying files", _parse_args().sleep)
    print("\nCOPYING COMPLETED")


def group_into_subdirs(s_path):
    l_dirs = []
    pp = pathlib.PurePath
    for directory in walk(s_path):
        l_dirs.append((str(pp(directory[0]).parent), pp(directory[0]).name))
    l_dirs.pop(0)  # remove root dir
    sort_natural(l_dirs)
    get_prefixes(l_dirs, l_subdirs)
    # print(*l_dirs, sep="\n")
    print("\ndirs inside: {}".format(len(l_dirs)))


def dir_mv(s_path, l_groups):
    for (path, group) in l_groups:
        src_path = pathlib.PurePath().joinpath(path[0], path[1])
        dst_path = pathlib.PurePath.joinpath(s_path, group, path[1])
        move(src_path, dst_path)
        print("{}".format(dst_path))
        # print("s:{}\nd:{}".format(src_path, dst_path))
        progress_bar(next(c_dir), len(l_groups), "moving files", _parse_args().sleep)
    print("\nMOVING COMPLETED")


def rm_dir(s_path):
    path = pathlib.Path(s_path)
    if pathlib.Path.is_dir(path):
        rmtree(path, ignore_errors=True)


def main():
    path = _parse_args().path
    path_cp = str(path) + postfix_cp
    path_mv = str(path) + postfix_mv

    rm_dir(path_cp)
    rm_dir(path_mv)

    validate_path(path)
    get_file_paths(path)
    file_loop(l_fullpath, _parse_args().count)
    file_copying(l_group, _parse_args().full)
    print(processed_files(_parse_args().count))

    group_into_subdirs(path_cp)
    dir_mv(pathlib.PurePath(path_mv), l_subdirs)

    # print(*l_fullpath, sep="\n")
    # print(*l_group, sep="\n")
    # print(*l_subdirs, sep="\n")
    # print(count_words("sprSushiGuyShake"))


main()
