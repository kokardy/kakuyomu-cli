import click

from kakuyomu.client import Client

client = Client()


@click.group()
def cli():
    pass


@cli.command()
def status():
    print(client.status())


@cli.command()
def logout():
    client.logout()
    print("logout")


@cli.command()
def login():
    client.login()
    print(client.status())


@cli.command()
def works():
    for work in client.get_works().values():
        print(work)


@cli.command()
def episodes():
    for episode in client.get_episodes().values():
        print(episode)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
