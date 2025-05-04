import argparse
from myvcs import commands

def main():
    parser = argparse.ArgumentParser(
        prog="myvcs",
        description="A basic version control system")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("file")

    rm_parser = subparsers.add_parser("rm")
    rm_parser.add_argument("file")

    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument("-m", required=True, help="Commit message")

    subparsers.add_parser("log")

    diff_parser = subparsers.add_parser("diff")
    diff_parser.add_argument("file")

    args = parser.parse_args()

    match args.command:
        case "init":
            commands.init()

        case "add":
            commands.add(args.file)

        case "rm":
            commands.remove(args.file)

        case "commit":
            commands.commit(args.m)

        case "log":
            commands.log()

        case "diff":
            commands.diff(args.file)

        case "branch":
            commands.branch(args.name)

        case _:
            parser.print_help()