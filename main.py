from collections import UserDict
from datetime import datetime, timedelta

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
        self.name = Name(name) if not isinstance(name, Name) else name
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        
    def add_birthday(self, data_str):
        if self.birthday:
            raise ValueError("Birthday already exists.")
        self.birthday = Birthday(data_str)

    def show_birthday(self):
        return self.birthday.value if self.birthday else None
    
    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
        
    def find_phone(self, phone_value: str):
        for p in self.phones:
            if p.value == phone_value:
                return p
        return None
    
    def remove_phone(self, phone_value: str):
        for p in self.phones:
            if p.value == phone_value:
                self.phones.remove(p)
                return True
        raise ValueError("Phone number not found.")
    
    def edit_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Old phone number not found.")

        Phone(new_phone)

        phone_obj.value = new_phone
        return True
    
    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        return f"Name: {self.name}  Phones: {phones_str}"

class AddressBook(UserDict):
    
    def add_record(self, record: Record):
        self.data[record.name.value.lower()] = record

    def delete(self, name: str):
        return self.data.pop(name, None) is not None
    
    def find(self, name):
        self.name = Name(name) if not isinstance(name, Name) else name
        return self.data.get(self.name.value.lower())
    
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
                congratulate_date = bday_this_year

                if congratulate_date.weekday() == 5:  
                    congratulate_date += timedelta(days=2)
                elif congratulate_date.weekday() == 6:  
                    congratulate_date += timedelta(days=1)

                upcoming.append((record.name.value, congratulate_date.strftime("%d.%m.%Y")))

        return upcoming
    
    def __str__(self):
        if not self.data:
            return "Address Book is empty."
        return '\n'.join(str(record) for record in self.data.values())

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError:
            return 'This contact does not exist.'
        except KeyError:
            return 'Contact not found.'
        except ValueError as e:
            msg = str(e)
            
            if 'unpack' in msg or 'not enough values' in msg:
                return 'Invalid number of actions. Please check the command format.'
            
            if 'Phone number' in msg:
                return 'Invalid phone number. It must contain only digits and be 10 characters long.'
            
            if 'Birthday' in msg:
                return 'Invalid birthday format. It must be in the format DD.MM.YYYY.'
            return msg
        
        except IndexError:
            return 'Please provide the required information for the command.'
        
        except TypeError:
            return 'Invalid input type. Please check the command format.'
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
    book.add_record(record)
    return 'New contact added.'

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    phones = ', '.join(str(phone) for phone in record.phones)
    return f"{name}: {phones}"

@input_error
def show_all(book):
    return str(book)

@input_error
def add_birthday(args, book):
    name, date_str = args
    record = book.find(name)
    record.add_birthday(date_str)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
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
    if not user_input.strip():
        return None, []
    parts = user_input.strip().split()
    return parts[0].lower(), parts[1:]

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
            print("Hello! How can I help you?")
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


