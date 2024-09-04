from hw.models import Author, Quote
from models import Author, Quote


def search_quotes():
    while True:
        command = input("Command: ")
        if command.startswith("name:"):
            author_name = command.split(":", 1)[1].strip()
            author = Author.objects(fullname=author_name).first()
            if author:
                quotes = Quote.objects(author=author)
                for quote in quotes:
                    print(quote.quote)
            else:
                print('Author doesnt exists')

        elif command.startswith("tag:"):
            tag = command.split(":", 1)[1].strip()
            quotes = Quote.objects(tags=tag)
            for quote in quotes:
                print(quote.quote)

        elif command.startswith("tags:"):
            tags = command.split(":", 1)[1].strip().split(',')
            quotes = Quote.objects(tags__in=tags)
            for quote in quotes:
                print(quote.quote)

        elif command == "exit":
            break
        else:
            print("not right command")


if __name__ == "__main__":
    search_quotes()