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
from types import SimpleNamespace

import click
import envoy

exit_status = SimpleNamespace(success=0, error=1)


def install_rabbit_if_necessary():
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


def start_rabbit_server():
    start_server = envoy.run('sudo rabbitmq-server -detached')
    print(start_server.std_out)
    print(start_server.std_err)


def stop_rabbit_server():
    stop_server = envoy.run('sudo rabbitmqctl stop')
    print(stop_server.std_out)
    print(stop_server.std_err)


def setup_rabbit():
    # setup user name and password
    username = input("Please enter a username: ")
    pw = input("Please enter password: ")
    add_user = envoy.run('rabbitmqctl add_user {username} {password}'.format(username=username, pw=pw))
    print(add_user.std_out)
    print(add_user.std_err)

    # setup virtual host
    virtual_host = input("Please enter a name for the virtual host: ")
    add_vhost = envoy.run("rabbitmqctl add_vhost {v_host}".format(v_host=virtual_host))
    print(add_vhost.std_out)
    print(add_vhost.std_err)

    # set user tags
    print(" [*] Setting user tags...")
    user_tag = username + '_tag'
    set_user_tags = envoy.run("rabbitmqctl set_user_tags {user} {user_tag}".format(user=username, user_tag=user_tag))
    print(set_user_tags.std_out)
    print(set_user_tags.std_err)

    # set permisions
    print(" [*] Setting user permissions...")
    set_permissions = envoy.run(
        'rabbitmqctl set_permissions -p {virt_host} {username} ".*" ".*" ".*"'.format(username=username,
                                                                                      virt_host=virtual_host))
    print(set_permissions.std_out)
    print(set_permissions.std_err)



@click.command()
@click.option('--install_rabbitmq', is_flag=True, help='Installs RabbitMQ using brew if not already installed')
@click.option('--run_rabbit', is_flag=True, help="Starts RabbitMQ Server")
@click.option("--kill_rabbit", is_flag=True, help="Stops RabbitMQ Server")
@click.option("--setup_rabbit", is_flag=True, help="Setups up RabbitMQ to work with Celery")
def cli(install_rabbitmq, run_rabbit, kill_rabbit, setup_rabbit):
    """
    Tool for installing and managing RabbitMQ.
    """
    if install_rabbitmq:
        install_rabbit_if_necessary()

    if run_rabbit:
        click.echo("Starting RabbitMQ server")
        start_rabbit_server()

    if kill_rabbit:
        click.echo("Stopping RabbitMQ server")
        stop_rabbit_server()

    if setup_rabbit:
        click.echo("Setting up RabbitMQ: ")
        click.echo("You will be prompted for everything needed to integrate celery with RabbitMQ")


if __name__ == '__main__':
    cli()
