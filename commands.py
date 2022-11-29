# file: commands.py
import os

import click
from click import pass_context
from flask.cli import with_appcontext, run_command

from flask import current_app

@click.command('serve', context_settings={"ignore_unknown_options": True})
@with_appcontext
@click.argument('args', nargs=-1)
def serve(args):
    """Alias for 'flask run'."""
    os.environ['FLASK_ENV'] = current_app.config['ENV']
    ctx = run_command.make_context('serve', list(args))
    run_command.invoke(ctx)