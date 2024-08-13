import random
import names

majors = ['Business', 'Finance', 'Accounting', 'Science', 'Computer Science', 'Math', 'Statistics', 'Engineering', 'Other']
major_weights = [5, 20, 10, 2, 5, 8, 8, 3, 1]

years = [year for year in range(1991, 2021)]

years_oe = [year for year in range(1, 36)]

cities = ['Toronto', 'New York', 'Hong Kong', 'Miami', 'Chicago', 'Montreal', 'London', 'Boston', 'Shanghai', 'Berlin', 'Rome']

def generate_random_entries(num_rows):
    results = []

    for i in range(num_rows):
        current_person = []
        
        major = random.choices(majors, weights = major_weights)[0]
        year_joined = random.choices(years)[0]
        yoe = max(2024 - year_joined, random.choices(years_oe)[0])
        name = names.get_full_name()
        city = random.choices(cities)[0]

        current_person.append(name)
        current_person.append(year_joined)
        current_person.append(city)
        current_person.append(yoe)
        current_person.append(major)

        results.append(current_person)

    return results

def create_sql_insert(people):
    string = 'INSERT INTO portfolio_managers (name, year_joined, city, yoe, uni_major) VALUES '
    string_lst = []

    for i in range(len(people)):
        current_lst = people[i]
        current_string = f"('{current_lst[0]}', {current_lst[1]}, '{current_lst[2]}', {current_lst[3]}, '{current_lst[4]}')"
        string_lst.append(current_string)
    
    return string + ', '.join(string_lst)

people = generate_random_entries(100)
test = create_sql_insert(people)

print(test)