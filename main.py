import logging
from faker import Faker
import random
import psycopg2
from psycopg2 import DatabaseError

fake = Faker()

# Підключення до бази даних
conn = psycopg2.connect(host="localhost", database="test10", user="postgres", password="mysecretpassword")
cur = conn.cursor()

try:
    # Додавання груп
    group_names = [fake.word() for _ in range(3)]
    for name in group_names:
        cur.execute("INSERT INTO groups (name) VALUES (%s)", (name,))

    # Додавання викладачів
    teacher_ids = []
    for _ in range(5):
        cur.execute("INSERT INTO teachers (fullname) VALUES (%s) RETURNING id", (fake.name(),))
        teacher_ids.append(cur.fetchone()[0])

    # Додавання предметів із вказівкою викладача
    subject_ids = []
    for _ in range(8):
        teacher_id = random.choice(teacher_ids)
        cur.execute("INSERT INTO subjects (name, teacher_id) VALUES (%s, %s) RETURNING id",
                    (fake.word(), teacher_id))
        subject_ids.append(cur.fetchone()[0])

    # Додавання студентів і оцінок
    for _ in range(50):  # 30-50 студентів
        group_id = random.choice(range(1, 4))  # 3 групи
        cur.execute("INSERT INTO students (fullname, group_id) VALUES (%s, %s) RETURNING id",
                    (fake.name(), group_id))
        student_id = cur.fetchone()[0]

        for subject_id in subject_ids:
            for _ in range(random.randint(5, 20)):  # до 20 оцінок
                cur.execute("INSERT INTO grades (student_id, subject_id, grade, grade_date) VALUES (%s, %s, %s, %s)",
                            (student_id, subject_id, random.randint(0, 100), fake.date_this_decade()))

    # Збереження змін
    conn.commit()
except DatabaseError as e:
    logging.error(e)
    conn.rollback()
finally:
    # Закриття підключення
    cur.close()
    conn.close()