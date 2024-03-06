from datetime import datetime, timedelta
from collections import defaultdict

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not self.value.isdigit() or len(self.value) != 10:
            raise ValueError("Phone number must consist of 10 digits.")

# додаємо клас Birthday з полем для дня народження
class Birthday(Field):
    def __init__(self, value):
        super().__init__(datetime.strptime(value, '%d.%m.%Y'))

    @property
    def date(self):
        return self.value.date()

# додаємо функціонал роботи з Birthday
class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone)] if phone else []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        if any(phone.value == p.value for p in self.phones):
            raise ValueError("Phone number already exists for this contact")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return "Phone number updated."
        return "Phone not found."

    # додаємо функцію add_birthday, яка додає день народження до контакту
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

# Додаємо функціонал до класу AddressBook
class AddressBook:
    def __init__(self):
        self._records = {}

    def add_record(self, record):
        self._records[record.name.value] = record

    def get_record(self, name):
        return self._records.get(name)

    def get_all_contacts(self):
        return "\n".join([f"{name}: {record.phones[0].value if record.phones else 'No phone number.'}" for name, record in self._records.items()])

    # додаємо функцію з попереднього завдання get_birthdays_per_week
    def get_birthdays_per_week(self):
        today = datetime.now().date()
        upcoming_birthdays = defaultdict(list)
        for name, record in self._records.items():
            if record.birthday:
                birthday_this_year = record.birthday.date.replace(year=today.year)
                if today <= birthday_this_year <= today + timedelta(days=7):
                    upcoming_birthdays[birthday_this_year.strftime("%A")].append(name)
        return "\n".join([f"{day}: {', '.join(names)}" for day, names in upcoming_birthdays.items()])

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

@input_error
def add_contact_command(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Not enough arguments. Usage: add [name] [phone]")
    name, phone = args[0], args[1]
    if name in book._records:
        try:
            book._records[name].add_phone(Phone(phone))
            return "Phone number added to the existing contact."
        except ValueError as e:
            return str(e)
    else:
        book.add_record(Record(name, phone))
        return "Contact added."

# Додаємо функціонал для роботи з днем народження
@input_error
def add_birthday_command(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Usage: add-birthday [name] [birthday in DD.MM.YYYY]")
    name, birthday = args
    record = book.get_record(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

# доповнюємо та оновлюємо функції для команд
def get_contact_phone_command(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: phone [name]"
    name = args[0]
    record = book.get_record(name)
    if record:
        return record.phones[0].value if record.phones else "No phone number."
    else:
        return "Contact not found."

def hello_command(args):
    return "How can I help you?"

def show_all_contacts_command(args, book: AddressBook):
    return book.get_all_contacts()

def show_birthday_command(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: show-birthday [name]"
    name = args[0]
    record = book.get_record(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    elif record and not record.birthday:
        return "Birthday not set for this contact."
    else:
        return "Contact not found."

def edit_contact_command(args, book: AddressBook):
    if len(args) != 3 or args[1] != "phone":
        return "Usage: edit [name] phone [new phone]"
    name, _, new_phone = args
    record = book.get_record(name)
    if record:
        return record.edit_phone(new_phone)
    else:
        return "Contact not found." 

# впроваджуємо функцію main зі всіма командами
def main():
    book = AddressBook()
    commands = {
        "add": lambda args: add_contact_command(args, book),
        "add-birthday": lambda args: add_birthday_command(args, book),
        "birthdays": lambda args: print(book.get_birthdays_per_week()),
        "phone": lambda args: get_contact_phone_command(args, book),
        "hello": lambda args: hello_command(args),
        "all": lambda args: show_all_contacts_command(args, book),
        "show-birthday": lambda args: show_birthday_command(args, book),
        "edit": lambda args: edit_contact_command(args, book),
    }

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").lower().split()
        command, args = user_input[0], user_input[1:]

        if command in ["exit", "close"]:
            print("Good bye!")
            break

        handler = commands.get(command)
        if not handler:
            print("Invalid command.")
            continue

        result = handler(args)
        if result:
            print(result)

if __name__ == "__main__":
    main()

