# -*- coding: utf-8 -*-

"""Console script for coagmet."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for coagmet."""
    click.echo('CLI will be available in the future.')
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
