import psycopg2


# Подключение к базе данных
def create_connection():
    connection = psycopg2.connect(
        dbname="your_database",
        user="your_username",
        password="your_password",
        host="your_host",
        port="your_port"
    )
    return connection


# Функция, создающая структуру БД (таблицы)
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                phone VARCHAR(20)
            )
        ''')
    conn.commit()


# Функция, позволяющая добавить нового клиента
def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone in phones:
                add_phone(conn, client_id, phone)


# Функция, позволяющая добавить телефон для существующего клиента
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO phones (client_id, phone)
            VALUES (%s, %s)
        ''', (client_id, phone))


# Функция, позволяющая изменить данные о клиенте
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute('''
                UPDATE clients
                SET first_name = %s
                WHERE id = %s
            ''', (first_name, client_id))
        if last_name:
            cur.execute('''
                UPDATE clients
                SET last_name = %s
                WHERE id = %s
            ''', (last_name, client_id))
        if email:
            cur.execute('''
                UPDATE clients
                SET email = %s
                WHERE id = %s
            ''', (email, client_id))
        if phones:
            cur.execute('''
                DELETE FROM phones
                WHERE client_id = %s
            ''', (client_id,))
            for phone in phones:
                add_phone(conn, client_id, phone)


# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM phones
            WHERE client_id = %s AND phone = %s
        ''', (client_id, phone))


# Функция, позволяющая удалить существующего клиента
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM clients
            WHERE id = %s
        ''', (client_id,))


# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = '''
            SELECT c.id, c.first_name, c.last_name, c.email, p.phone
            FROM clients c
            LEFT JOIN phones p ON c.id = p.client_id
            WHERE 
        '''
        conditions = []
        params = []
        if first_name:
            conditions.append('c.first_name = %s')
            params.append(first_name)
        if last_name:
            conditions.append('c.last_name = %s')
            params.append(last_name)
        if email:
            conditions.append('c.email = %s')
            params.append(email)
        if phone:
            conditions.append('p.phone = %s')
            params.append(phone)

        query += ' AND '.join(conditions)
        cur.execute(query, tuple(params))
        result = cur.fetchall()
        return result


# Демонстрация работы функций
if __name__ == "__main__":
    conn = create_connection()
    create_db(conn)
    add_client(conn, "John", "Doe", "john.doe@example.com", ["89920078998", "89126982929"])
    change_client(conn, 1, first_name="Jane")
    print(find_client(conn, first_name="Jane"))
    delete_phone(conn, 1, "89920078998")
    delete_client(conn, 1)
    conn.close()