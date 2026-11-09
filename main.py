import pickle
import sys
from functools import wraps

from addressbook import Record
from storage import load_data, save_data


def input_error(func):
    """Показує помилку введення, щоб бот міг прийняти наступну команду."""
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as error:
            return str(error)
        except IndexError:
            return "Enter user name."
    return inner


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args


def require_args(args, count, usage):
    if len(args) != count:
        raise ValueError(f"Usage: {usage}")


def find_record(book, name):
    record = book.find(name.lower())
    if record is None:
        raise KeyError(name)
    return record


@input_error
def add_contact(args, book):
    require_args(args, 2, "add <name> <phone>")
    name, phone = args
    name = name.lower()
    record = book.find(name)
    if record is None:
        record = Record(name)
        # Перевіряємо телефон до додавання контакту до книги.
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args, book):
    require_args(args, 3, "change <name> <old_phone> <new_phone>")
    name, old_phone, new_phone = args
    find_record(book, name).edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book):
    require_args(args, 1, "phone <name>")
    record = find_record(book, args[0])
    return "; ".join(str(phone) for phone in record.phones) or "No phones."


@input_error
def show_all(args, book):
    require_args(args, 0, "all")
    return str(book)


@input_error
def add_birthday(args, book):
    require_args(args, 2, "add-birthday <name> <DD.MM.YYYY>")
    find_record(book, args[0]).add_birthday(args[1])
    return "Birthday added."


@input_error
def show_birthday(args, book):
    require_args(args, 1, "show-birthday <name>")
    birthday = find_record(book, args[0]).birthday
    return str(birthday) if birthday is not None else "Birthday not set."


@input_error
def birthdays(args, book):
    require_args(args, 0, "birthdays")
    rows = (
        f"{item['name']}: {item['birthday']}"
        for item in book.get_upcoming_birthdays()
    )
    return "\n".join(rows) or "No upcoming birthdays."


@input_error
def hello(args, book):
    require_args(args, 0, "hello")
    return "How can I help you?"


@input_error
def close(args, book):
    require_args(args, 0, "close or exit")
    return "Good bye!"


def main():
    try:
        book = load_data()
    except (OSError, ValueError, pickle.UnpicklingError, EOFError,
            AttributeError, ImportError) as error:
        # Не перезаписуємо файл, якщо його не вдалося прочитати.
        print(f"Cannot load the address book: {error}", file=sys.stderr)
        return 1
    print("Welcome to the assistant bot!")
    while True:
        try:
            user_input = input("Enter a command: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            break
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(close(args, book))
            if not args:
                break
        elif command == "hello":
            print(hello(args, book))
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

    # Сюди потрапляємо також після Ctrl+C або завершення вводу.
    try:
        save_data(book)
    except OSError as error:
        print(f"Cannot save the address book: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
