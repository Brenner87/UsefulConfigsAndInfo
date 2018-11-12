"""
This script parses all *.log files in profided folder for string "Username = user_name,"
and returns set of unique user_name with some statistic.
Usage:
python log_parser.py "path_to_folder"
Last slash "\" in the folder name should be omited.
Tested on Windows only.
"""

import os
import sys


def parse_log(file_name):
    line_cnt = 0
    users = set()

    for line in open(file_name):
        pos1 = line.find('Username')
        line_cnt += 1
        if pos1 >= 0:
            pos2 = line.find("= ", pos1)
            username = line[pos2 + 2:line.find(',', pos2)]
            users.add(username)
    return users


def main():
    if len(sys.argv) != 2:
        print("Wrong parameter(s). Usage 'python log_parser.py \"dir_name\"' (with double quotes but without last slash '\\')")
        sys.exit(0)

    work_folder = os.path.normpath(sys.argv[1])
    all_users = set()
    files_num = 0

    print("Started...")
    print("-" * 20)

    for file in os.listdir(work_folder):
        files_num += 1
        if file.endswith(".log"):
            print('Processing file: {}'.format(file))
            all_users = all_users | parse_log(os.path.join(sys.argv[1], file))

    print('-' * 20)
    print("Composing data...")
    print('-' * 20)
    for usr in sorted(all_users):
        print(usr)

    print('-' * 20)
    print('Num of Files: {}'.format(files_num))
    print('Num of unique Users: {}'.format(len(all_users)))


if __name__ == '__main__':
    main()
