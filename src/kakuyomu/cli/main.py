from utils.web import Client


def main() -> None:
    client = Client("cookie")
    status =client.status()
    print(status)


if __name__ == "__main__":
    main()
