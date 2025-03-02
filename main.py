from collections import UserDict
import re


'''
Додаток, який буде працювати з книгою контактів та календарем

1) Зберігати ім'я та номер телефону
2) Знаходити номер телефону за ім'ям
3) Змінювати записаний номер телефону
4) Виводити в консоль всі записи, які збереглись

{"name": "John", "phone": "80977333967"}

'''

contacts_file = "contacts.txt"

commands = """
1) add [name] [number] - to add a new contact
2) change [name] [old number] [new number] - to change contact's phone number
3) phone [name] - to print name 
4) all - will show all number from the contacts
5) exit - to exit the application
"""

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone):
        if phone in [p.value for p in self.phones]:
            raise ValueError("This phone number is already added")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found")

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

    def save_contacts(self):
        with open(contacts_file, 'w', encoding="utf-8") as file:
            for record in self.data.values():
                phones = ";".join(p.value for p in record.phones)
                file.write(f'{record.name.value}: {phones}\n')

    def read_contacts(self):
        try:
            with open(contacts_file, 'r', encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(': ', 1)
                    if len(parts) != 2:
                        print(f'Skipping invalid line in contacts file: {line}')
                        continue
                    name, phones = parts
                    record = Record(name)
                    for phone in phones.split(";"):
                        try:
                            record.add_phone(phone)
                        except ValueError:
                            print(f'Skipping invalid phone number "{phone}" for contact {name}')
                    self.add_record(record)
        except FileNotFoundError:
            open(contacts_file, 'w', encoding="utf-8").close()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me a valid name and phone number please"
        except KeyError:
            return "User not found."
        except IndexError:
            return "Enter user name."
        except TypeError:
            return "Invalid command format."
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(book, args):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return f"Contact {name} added"


@input_error
def change_contact(book, args):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Contact {name} updated"
    return "Contact not found"

@input_error
def show_phone(book, args):
    name = args[0]
    record = book.find(name)
    if record:
       return str(record)
    return "Contact not found"

@input_error
def show_all(book):
    return str(book)


def main():
    book = AddressBook()
    book.read_contacts()
    print ("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(book, args))
        elif command == "change":
            print(change_contact(book, args))
        elif command == "phone":
            print (show_phone(book, args))
        elif command == "all":
            print(show_all(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":

    book = AddressBook()
    #Created a record for John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    #Add Jon's record to the address book
    book.add_record(john_record)

    #Created and add a new record for Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    #Print all records in the book
    for record in book.data.values():
        print(record)

    #Find and edit a phone for John
    john = book.find("John")
    if john:
        john.edit_phone("1234567890", "1112223333")
        print(john)

    #Search for a specific phone in John's record
    found_phone = john.find_phone("5555555555")
    if found_phone:
        print(f"{john.name}: {found_phone}")

    #Delete Jane's record
    book.delete('Jane')
