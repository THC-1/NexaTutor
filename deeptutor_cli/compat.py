"""Temporary compatibility entry point for the legacy ``deeptutor`` command."""

from __future__ import annotations

import sys

from deeptutor_cli.main import main as nexatutor_main


def main() -> None:
    print(
        "The 'deeptutor' command is deprecated; use 'nexatutor'. Forwarding now.",
        file=sys.stderr,
    )
    nexatutor_main()


if __name__ == "__main__":
    main()
