def main(argv=None) -> None:
    from aurora_svmat_lab.cli import main as cli_main

    return cli_main(argv=argv)


if __name__ == "__main__":
    import sys

    main(argv=sys.argv[1:])
