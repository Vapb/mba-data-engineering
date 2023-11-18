import psycopg2


class PostgreSQLConnection:
    def __init__(self, dbname, user, password, host="localhost", port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Connected to PostgreSQL database.")
        
        except psycopg2.Error as e:
            print(f"Unable to connect to the database. Error: {e}")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing the query. Error: {e}")
            self.connection.rollback()

    def insert_department(self, dep_id, url, hierarchy):
        query = f"""
            INSERT INTO departamento (id, url, hierarquia)
            VALUES ('{dep_id}', '{url}', '{hierarchy}')
            ON CONFLICT (id) DO NOTHING;
        """
        try:
            self.execute_query(query)
        except Exception as e:
            print(f"Error inserting department. Error: {e}")

    def insert_product(self, sku, name, brand):
        query = f"""
            INSERT INTO produto (id, nome, marca)
            VALUES ('{sku}', '{name}', '{brand}')
            ON CONFLICT (id) DO NOTHING;
        """
        try:
            self.execute_query(query)
        except Exception as e:
            print(f"Error inserting produto. Error: {e}")
            

    def insert_advertisement(self, market_id, dep_id, sku, best_price, regular_price, date):
        query = f"""
            INSERT INTO anuncio (id_supermercado, id_departamento, id_produto, preco_promocional, preco_regular, tempo)
            VALUES ({market_id}, '{dep_id}', '{sku}', {best_price}, {regular_price}, '{date}')
            ON CONFLICT (id_anuncio) DO NOTHING;
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error inserting anuncio. Error: {e}")
            self.connection.rollback()

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Connection to PostgreSQL database closed.")


