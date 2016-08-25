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
    pass


@click.command()
@click.option('--install_rabbitmq', help='Installs RabbitMQ using brew if not already installed')
@click.option('--run_rabbit_server', help="Starts RabbitMQ Server")
def cli(install_rabbitmq, run_rabbit_server):
    if install_rabbitmq:
        install_rabbit_if_necessary()

    if run_rabbit_server:
        start_rabbit_server()


if __name__ == '__main__':
    cli()






