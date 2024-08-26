import psycopg2


conn = psycopg2.connect(
    dbname="test10",
    user="postgres",
    password="mysecretpassword",
    host="localhost"
)

cursor = conn.cursor()


try:
    with open('/Users/anastasiiazavialova/PycharmProjects/sql/query_06.sql', 'r') as file:
        sql_query = file.read().strip()
        if not sql_query:
            raise ValueError("SQL-запит порожній!")
except FileNotFoundError:
    print("Файл не знайдено. Перевірте шлях до файлу.")
    exit(1)
except ValueError as e:
    print(e)
    exit(1)


try:
    cursor.execute(sql_query)

    results = cursor.fetchall()
    for row in results:
        print(row)
except psycopg2.ProgrammingError as e:
    print(f"Помилка при виконанні запиту: {e}")

finally:
    cursor.close()
    conn.close()