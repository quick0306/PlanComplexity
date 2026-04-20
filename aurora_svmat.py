def main(*, run_loop: bool = False) -> None:
    from aurora_svmat_lab.gui import main as gui_main

    return gui_main(run_loop=run_loop)


if __name__ == "__main__":
    main(run_loop=True)
