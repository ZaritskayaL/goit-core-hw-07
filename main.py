from collections import UserDict
from datetime import datetime

class Field:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

class Phone(Field):
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, phone):
        if type(phone) != str:
            raise TypeError("Phone number must be a string.")
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Phone number must contain only digits and be 10 characters long.")
        
        self._value = phone
        
        
class Birthday(Field):
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    
    def value(self, date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY")
        self._value = date_str
   
class Record:
    
    def __init__(self, name):
        if isinstance(name, Name):
            self.name = name
        else:
            self.name = Name(name)
        
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        
    def add_birthday(self, data_str):
        birthday = Birthday(data_str)
        if self.birthday is not None:
            raise ValueError("Birthday already exists.")
        self.birthday = birthday

    def show_birthday(self):
        return self.birthday.value if self.birthday else None
    
    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
    
    def remove_phone(self, phone_value: str):
        for p in self.phones:
            if p.value == phone_value:
                self.phones.remove(p)
                return True
        raise ValueError("Phone number not found.")
    
    def edit_phone(self, old_phone: str, new_phone: str):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return True
        raise ValueError("Old phone number not found.")
    
    def find_phone(self, phone_value: str):
        for p in self.phones:
            if p.value == phone_value:
                return p
        return None
    
    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        birthday_str = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Name: {self.name}, Phones: {phones_str}, Birthday: {birthday_str}"

class AddressBook(UserDict):
    
    def add_phone(self, record: Record):
        self.data[record.name.value] = record

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
            return True
        return False
    
    def find(self, name):
        return self.data.get(name)
    
    def birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            bday_this_year = bday.replace(year=today.year)

            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)

            delta = (bday_this_year - today).days

            if 0 <= delta <= 7:
                upcoming.append((record.name.value, record.birthday.value))

        return upcoming
    
    def __str__(self):
        if not self.data:
            return "Address Book is empty."
        
        return '\n'.join(str(record) for record in self.data.values())

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Error: Contact not found."
        except ValueError as e:
            return str(e)
        except TypeError as e:
            return str(e)
        except IndexError as e:
            return 'Error: Not enough arguments provided.'
    return wrapper

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    
    if record:
        record.add_phone(phone)
        return 'Phone added to existing contact.'
    
    record = Record(name)
    record.add_phone(phone)
    book.add_phone(record)
    return 'New contact added.'

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    
    if not record:
        raise KeyError("Contact not found.")
    
    record.edit_phone(old_phone, new_phone)
    return 'Phone is updated.'

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    
    if not record:
        raise KeyError("Contact not found.")
    
    phones = ', '.join(str(phone) for phone in record.phones)
    return f"{name}: {phones}"

@input_error
def show_all(book):
    return str(book)

@input_error
def add_birthday(args, book):
    name, date_str = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_birthday(date_str)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    if not record.birthday:
        return "Birthday not set."
    return record.birthday.value

@input_error
def birthdays(args, book):
    upcoming = book.birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{name}: {date}" for name, date in upcoming)


def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = AddressBook()
    
    print("Welcome to the Assistant bot!")
    
    while True:
        user_input = input("Enter command: ")
        command, args = parse_input(user_input)
        
        if command in ['exit', 'close', 'goodbye']:
            print("Goodbye!")
            break
        
        elif command == 'hello':
            print("How can I help you?")
        elif command == 'add':
            print(add_contact(args, book))
        elif command == 'change':
            print(change_contact(args, book))
        elif command == 'phone':
            print(show_phone(args, book))
        elif command == 'all':
            print(show_all(book))
        elif command == 'add-birthday':
            print(add_birthday(args, book))
        elif command == 'show-birthday':
            print(show_birthday(args, book))
        elif command == 'birthdays':
            print(birthdays(args, book))
        else:
            print("Invalid command")
            

if __name__ == "__main__":
    main()


