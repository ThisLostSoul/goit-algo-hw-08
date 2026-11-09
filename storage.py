import pickle

from addressbook import AddressBook


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        # Під час першого запуску збереженої книги ще немає.
        return AddressBook()
