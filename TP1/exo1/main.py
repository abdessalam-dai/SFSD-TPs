def get_ids():
    with open("database.txt", "r") as f:
        ids = []
        for line in f.readlines():
            ID = int(line.split(";")[0])
            ids.append(ID)
        return ids


def read_student_info():
    student_id = input("Enter student's ID: ").strip()
    while not student_id.isdigit():
        student_id = input("Enter student's ID (integers only are accepted !): ").strip()

    while int(student_id) in get_ids():
        print("ID already exits !")
        student_id = input("Enter student's ID: ").strip()
    student_id = int(student_id)

    first_name = input("Enter student's first name: ").strip().title()
    while not first_name.isalpha():
        print("Enter letters only !")
        first_name = input("Enter student's first name: ").strip().title()

    last_name = input("Enter student's last name: ").strip().upper()
    while not last_name.isalpha():
        print("Enter letters only !")
        last_name = input("Enter student's last name: ").strip().upper()

    speciality = input("Enter student's specialization: ").strip()

    return student_id, first_name, last_name, speciality


def add_student_to_database(ID, first_name, last_name, speciality):
    with open("database.txt", "a") as f:
        f.write(f"{ID};{first_name};{last_name};{speciality}\n")
        print(f"Student {ID} added to database !")


def print_students():
    with open("database.txt", "r") as f:
        for line in f.readlines():
            ID, first_name, last_name, speciality = line.split(";")
            print(f"{ID} : {first_name} {last_name} - speciality : {speciality}")


N = int(input("Enter number of students you want to add: "))
for i in range(N):
    ID, first_name, last_name, speciality = read_student_info()
    add_student_to_database(ID, first_name, last_name, speciality)


print_students()
