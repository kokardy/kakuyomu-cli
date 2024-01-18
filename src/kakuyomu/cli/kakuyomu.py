import click

from kakuyomu.client import Client

client = Client()


@click.group()
def cli() -> None:
    pass


@cli.command()
def status() -> None:
    print(client.status())


@cli.command()
def logout() -> None:
    client.logout()
    print("logout")


@cli.command()
def login() -> None:
    client.login()
    print(client.status())


@cli.command()
def works() -> None:
    for work in client.get_works().values():
        print(work)


@cli.command()
def episodes() -> None:
    for episode in client.get_episodes().values():
        print(episode)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
