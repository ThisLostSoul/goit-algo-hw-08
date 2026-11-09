import re
from collections import UserDict
from datetime import date, datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must not be empty.")
        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{10}", value):
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        valid_format = isinstance(value, str) and re.fullmatch(
            r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", value
        )
        if not valid_format:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError as error:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from error
        # Дату перевірили, але зберігаємо рядком за умовою завдання.
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        value = Phone(phone)
        if self.find_phone(phone) is None:
            self.phones.append(value)

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise ValueError("Phone not found.")
        self.phones.remove(found)

    def edit_phone(self, old_phone, new_phone):
        replacement = Phone(new_phone)
        found = self.find_phone(old_phone)
        if found is None:
            raise ValueError("Phone not found.")
        duplicate = self.find_phone(new_phone)
        if duplicate is not None and duplicate is not found:
            raise ValueError("This phone already exists.")
        self.phones[self.phones.index(found)] = replacement

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def __str__(self):
        phones = "; ".join(phone.value for phone in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phones}"
        if self.birthday is not None:
            result += f", birthday: {self.birthday}"
        return result


class AddressBook(UserDict):
    def get_upcoming_birthdays(self, today=None):
        """Дні народження на найближчі сім днів, включно із сьогодні."""
        today = today or date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday is None:
                continue
            birthday = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()

            def anniversary(year):
                try:
                    return birthday.replace(year=year)
                except ValueError:
                    # У невисокосний рік вітаємо народжених 29 лютого на день раніше.
                    return date(year, 2, 28)

            next_birthday = anniversary(today.year)
            if next_birthday < today:
                next_birthday = anniversary(today.year + 1)
            if 0 <= (next_birthday - today).days < 7:
                congratulations = next_birthday
                if congratulations.weekday() >= 5:
                    # Привітання у вихідні переносимо на понеділок.
                    days_to_monday = 7 - congratulations.weekday()
                    congratulations += timedelta(days=days_to_monday)
                upcoming.append({
                    "name": record.name.value,
                    "birthday": congratulations.strftime("%d.%m.%Y"),
                })
        return sorted(upcoming, key=lambda item: (
            datetime.strptime(item["birthday"], "%d.%m.%Y"), item["name"]))

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def __str__(self):
        rows = (str(record) for record in self.data.values())
        return "\n".join(rows) or "No contacts."
