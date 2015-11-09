# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import click
from oscli import makemodel as _makemodel
from oscli import checkmodel as _checkmodel
from oscli import checkdata as _checkdata
from oscli import auth as _auth
from oscli import upload as _upload
from oscli import utilities
from oscli import exceptions
from oscli import compat


@click.group()
def cli():
    """Open Spending CLI."""


@cli.command()
def version():
    """Display the version and exit.
    """

    msg = 'There is no version tracking yet.'
    click.echo(msg)


@cli.command()
@click.argument('action', default='read', type=click.Choice(['read', 'locate', 'ensure']))
def config(action):
    """Interact with .openspendingrc

    Args:
    * action: one of 'read', 'locate' or 'ensure'
        * 'read' will return the currently active config
        * 'locate' will return the location of the currently active config
        * 'ensure' will check a config exists, and write one in $HOME if not

    """

    if action == 'read':
        click.echo(json.dumps(utilities.read_config(), ensure_ascii=False))

    if action == 'locate':
        click.echo(json.dumps(utilities.locate_config(), ensure_ascii=False))

    if action == 'ensure':
        click.echo(json.dumps(utilities.ensure_config(), ensure_ascii=False))


@cli.command()
@click.argument('subcommand', type=click.Choice(['package', 'data']))
@click.argument('datapackage')
@click.option('--interactive', is_flag=True)
def validate(subcommand, datapackage, interactive):
    """Validate an Open Spending Data Package descriptor/data.

    Subcommands:
    * package
    * data
    """

    # Vaildate package
    if subcommand == 'package':
        MSG_SUCCESS = ('Congratulations, the data package looks good!')
        MSG_ERROR = ('While checking the data, we found some found some '
                     'issues: \n{0}\nRead more about required fields in '
                     'Open Spending Data Package here: {1}')
        url = 'https://github.com/openspending/oscli-poc#open-spending-data-package'
        service = _checkmodel.Checker(datapackage)
        service.run()
        if service.success:
            click.echo(click.style(MSG_SUCCESS))
        else:
            click.echo(click.style(MSG_ERROR.format(service.error, url)))

    # Validate data
    else:
        MSG_SUCCESS = ('\nCongratulations, the data looks good! You can now move on\n'
                       'to uploading your new data package to Open Spending!')
        MSG_CONTINUE = ('While checking the data, we found some found some issues\n'
                        'that need addressing. Shall we take a look?')
        MSG_CONTEXT = ('IMPORTANT: Not all errors are necessarily because of\n'
                       'invalid data. It could be that the schema needs adjusting\n'
                       'in order to represent the data more accurately.')
        MSG_GUIDE = ('\nWould you like to see our short guide on common schema\n'
                     'errors and solutions? (Launches a web page in your browser)')
        MSG_EDIT = ('\nWould you like to edit the schema for this data now? \n'
                    '(Opens the file in your editor)')
        MSG_END_CONTINUE = ('\nThat is all for now. Once you have made changes to\n'
                            'your data and/or schema, try running the ensure process again.')
        GUIDE_URL = 'https://github.com/openspending/oscli-poc/blob/master/oscli/checkdata/guide.md'
        DESCRIPTOR = 'datapackage.json'

        datapackage = os.path.abspath(datapackage)
        service = _checkdata.Checker(datapackage)
        success = service.run()

        if success:
            click.echo(click.style(MSG_SUCCESS, fg='green'))

        else:

            report = _checkdata.display_report(service.reports)
            if interactive:
                if click.confirm(click.style(MSG_CONTINUE, fg='red')):
                    click.clear()
                    click.echo(click.style(report, fg='blue'))
                    click.echo(click.style(MSG_CONTEXT, fg='yellow'))

                if click.confirm(click.style(MSG_GUIDE, fg='yellow')):
                    click.launch(GUIDE_URL)

                if click.confirm(click.style(MSG_EDIT, fg='yellow')):
                    click.edit(filename=os.path.join(datapackage, DESCRIPTOR))

            else:
                click.echo(click.style(report, fg='blue'))
                click.echo(click.style(MSG_CONTEXT, fg='yellow'))
                click.echo('Read the guide for help:\n')
                click.echo(GUIDE_URL)

            click.echo(click.style(MSG_END_CONTINUE, fg='green'))


@cli.command()
@click.argument('datapackage', default='.', type=click.Path(exists=True))
def upload(datapackage):
    """Upload an Open Spending Data Package to storage. Requires auth.
    """

    # don't proceed without a config
    if not utilities.locate_config():
        _msg = ('Uploading requires a config file. See the configuration '
                'section of the README for more information: '
                'https://github.com/openspending/oscli-poc')
        click.echo(click.style(_msg, fg='red'))
        return

    # is data package
    _valid, _msg = utilities.is_datapackage(datapackage)
    if not _valid:
        click.echo(click.style(_msg, fg='red'))
        return

    if isinstance(datapackage, compat.bytes):
        datapackage = datapackage.decode('utf-8')

    # is open spending data package
    checker = _checkmodel.Checker(datapackage)
    checker.run()
    if not checker.success:
        _msg = ('While checking the data, we found some found some '
                'issues: \n{0}\nRead more about required fields '
                'in Open Spending Data Packages here: {1}')
        url = 'https://github.com/openspending/oscli-poc#open-spending-data-package'
        click.echo(click.style(_msg.format(checker.error, url), fg='red'))
        return

    try:
        service = _upload.Upload()
    except (exceptions.ConfigNotFoundError, exceptions.ConfigValueError) as e:
        click.echo(click.style(e.msg, fg='red'))
        return

    click.echo(click.style('Your data is now being uploaded to Open Spending.\n',
                           fg='green'))
    service.run(datapackage)
    click.echo(click.style('Your data is now live on Open Spending!',
                           fg='green'))


if __name__ == '__main__':
    cli()
