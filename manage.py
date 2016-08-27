"""
A service that will install RabbitMQ if necessary.

MIT License

Copyright (c) 2016 Alex Bielen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from getpass import getpass
from types import SimpleNamespace

import click
import envoy

exit_status = SimpleNamespace(success=0, error=1)


def _install_rabbit_if_necessary():
    """
    Install rabbitmq if it is not already installed. Very primitive right now.
    Works only for OS X and even then it's not very good.
    :return: None
    """
    print('Checking for RabbitMQ...')
    check_for_rabbit = envoy.run('which rabbitmq')
    status = check_for_rabbit.status_code

    if status == exit_status.error:
        print(' [*] RabbitMQ not found!')
        should_install = input("Would you like to install it now? (Y/n): ")

        if should_install == 'Y':
            print(" [*] Installing RabbitMQ using brew...")
            install_rabbit = envoy.run('brew install rabbitmq')

            error = install_rabbit.std_err
            success = install_rabbit.std_out

            if install_rabbit.status_code != exit_status.success:
                print(error)
            else:
                print(success)
                print("Please set PATH=$PATH:/usr/local/sbin in your shell's .bash_profile or equivalent")

        else:
            print("Skipping installation and exiting!")

    else:
        print("RabbitMQ is already installed")


def _run_rabbit():
    start_server = envoy.run('sudo rabbitmq-server -detached')
    print(start_server.std_out)
    print(start_server.std_err)


def _kill_rabbit():
    stop_server = envoy.run('sudo rabbitmqctl stop')
    print(stop_server.std_out)
    print(stop_server.std_err)


def _setup_rabbit():
    # setup user name and password
    username = input("Please enter a username: ")
    pw = getpass("Please enter password: ")
    add_user = envoy.run('sudo rabbitmqctl add_user {username} {pw}'.format(username=username, pw=pw))
    print(add_user.std_out)
    print(add_user.std_err)

    # setup virtual host
    virtual_host = input("Please enter a name for the virtual host: ")
    add_vhost = envoy.run("sudo rabbitmqctl add_vhost {v_host}".format(v_host=virtual_host))
    print(add_vhost.std_out)
    print(add_vhost.std_err)

    # set user tags
    print(" [*] Setting user tags...")
    user_tag = username + '_tag'
    set_user_tags = envoy.run("sudo rabbitmqctl set_user_tags {user} {user_tag}".format(user=username, user_tag=user_tag))
    print(set_user_tags.std_out)
    print(set_user_tags.std_err)

    # set permissions
    print(" [*] Setting user permissions...")
    set_permissions = envoy.run(
        'sudo rabbitmqctl set_permissions -p {virt_host} {username} ".*" ".*" ".*"'.format(username=username,
                                                                                      virt_host=virtual_host))
    print(set_permissions.std_out)
    print(set_permissions.std_err)


def _get_rabbit_status():
    get_status = envoy.run('sudo rabbitmqctl status')
    print(get_status.std_out)
    print(get_status.std_err)




@click.command()
@click.option('--install_rabbitmq', is_flag=True, help='Installs RabbitMQ using brew if not already installed')
@click.option('--run_rabbit', is_flag=True, help="Starts RabbitMQ Server")
@click.option("--kill_rabbit", is_flag=True, help="Stops RabbitMQ Server")
@click.option("--setup_rabbit", is_flag=True, help="Setups up RabbitMQ to work with Celery")
@click.option("--get_rabbit_status", is_flag=True, help="Get the status from a running RabbitMQ instance")
def cli(install_rabbitmq, run_rabbit, kill_rabbit, setup_rabbit, get_rabbit_status):
    """
    Tool for installing and managing RabbitMQ.
    """
    if install_rabbitmq:
        _install_rabbit_if_necessary()

    if run_rabbit:
        click.echo("Starting RabbitMQ server")
        _run_rabbit()

    if kill_rabbit:
        click.echo("Stopping RabbitMQ server")
        _kill_rabbit()

    if setup_rabbit:
        click.echo("Setting up RabbitMQ: ")
        click.echo("You will be prompted for everything needed to integrate celery with RabbitMQ")
        _setup_rabbit()

    if get_rabbit_status:
        click.echo("Getting RabbitMQ Status...")
        _get_rabbit_status()



if __name__ == '__main__':
    cli()
