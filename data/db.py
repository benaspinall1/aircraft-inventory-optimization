import sqlite3
import csv
import os

# table_name: {column_name: column_type}
table_meta_data = {
    "aircraft_parts": {
        "part_id": "INTEGER PRIMARY KEY",
        "part_code": "TEXT NOT NULL",
        "category": "TEXT",
        "description": "TEXT NOT NULL",
        "ata_chapter": "INTEGER",
        "criticality": "TEXT",
        "unit_cost_usd": "REAL NOT NULL",
        "lead_time_days": "INTEGER NOT NULL"
    },

    "warehouse_locations": {
        "location_id": "TEXT PRIMARY KEY",
        "facility_code": "TEXT NOT NULL",
        "location_type": "TEXT NOT NULL",
        "max_capacity_units": "INTEGER NOT NULL",
        "temperature_control": "TEXT",  # Yes/No
        "hazmat_rating": "TEXT",  # None/Class I/II/III
        "is_secure": "TEXT", # Yes/No
        "notes": "TEXT"
    },

    "supplier_lead_times": {
        "lead_time_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "part_id": "INTEGER NOT NULL",
        "supplier_name": "TEXT NOT NULL",
        "min_lead_time_days": "INTEGER",
        "avg_lead_time_days": "INTEGER NOT NULL",
        "max_lead_time_days": "INTEGER",

        # FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)
    },

    "daily_demand": {
        "demand_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "part_id": "INTEGER NOT NULL",
        "location_id": "TEXT NOT NULL",
        "demand_date": "TEXT NOT NULL",
        "demand_quantity": "INTEGER NOT NULL",

        # FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)
        # FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id)
    },

    "stock_levels": {
        "stock_level_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "part_id": "INTEGER NOT NULL",
        "location_id": "TEXT NOT NULL",
        "quantity_on_hand": "INTEGER NOT NULL",
        "snapshot_date": "TEXT NOT NULL",  # ISO date string: YYYY-MM-DD

        # Foreign keys (SQLite allows them in CREATE TABLE)
        # These will be added in the SQL, not stored as data types:
        # FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)
        # FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id)
    },

    "orders": {
        "order_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "part_id": "INTEGER NOT NULL",
        "location_id": "TEXT",  # warehouse fulfilling the order
        "order_date": "TEXT NOT NULL",
        "quantity_ordered": "INTEGER NOT NULL",
        "order_type": "TEXT",  # "customer" or "replenishment"
        "due_date": "TEXT",  # when needed or expected delivery

        # FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)
        # FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id)
    }
}
foreign_key_relationships = {
    "aircraft_parts": [],
    "warehouse_locations": [],
    "supplier_lead_times": [
        "FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)"
    ],
    "daily_demand": [
        "FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)",
        "FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id)"
    ],
    "stock_levels": [
        "FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)",
        "FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id)"
    ],
    "orders": [
        "FOREIGN KEY(part_id) REFERENCES aircraft_parts(part_id)",
        "FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id)"
    ]
}


DB_FILE = "data/supply_chain.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_insert_sql(table_name, columns_dict):
    column_names = []
    for col_name, col_type in columns_dict.items():
        column_names.append(f"{col_name}")

    # Join all columns with comma, new-line, and tab
    columns_sql = ",\n    ".join(column_names)

    question_marks = ["?"] * len(column_names)
    qm_sql = ", ".join(question_marks) # for the "VALUES(?, ?, ?, ?, ?)" syntax

    insert_sql = f"""
    INSERT INTO {table_name} (
        {columns_sql}
    )
    VALUES({qm_sql})
    """

    return insert_sql


def build_create_table_sql(table_name, columns_dict):
    column_definitions = []
    for col_name, col_type in columns_dict.items():
        column_definitions.append(f"{col_name} {col_type}")

    # Join all columns with comma, new-line, and tab
    sql_statements = column_definitions + foreign_key_relationships[table_name]
    sql_statements = ",\n    ".join(sql_statements)
    foreign_keys = ",\n    ".join(foreign_key_relationships[table_name])
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {sql_statements}
    );
    """

    return create_sql


def convert_value(value, column_type):
    if value is None:
        return None

    t = column_type.upper()

    if "INTEGER" in t:
        return int(value)
    if "REAL" in t or "FLOAT" in t or "DOUBLE" in t:
        return float(value)
    if "TEXT" in t:
        return str(value)
    return value  # This is technically TEXT also


def read_table_names():
    table_names = table_meta_data.keys()
    for name in table_names:
        print(name)


def delete_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # delete entire DB file


class Database:
    def __init__(self):
        delete_db()
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        table_names = table_meta_data.keys()
        for table in table_names:
            self.create_table(table)
            self.seed_table(table)

    def close(self):
        self.conn.close()

    def create_table(self, table_name):
        columns = table_meta_data[table_name]
        create_sql = build_create_table_sql(table_name, columns)
        print(create_sql)
        self.cursor.execute(create_sql)
        self.conn.commit()

    def seed_table(self, table_name):
        self.cursor.execute(f"DELETE FROM {table_name}")
        print(f"Seeding Table: {table_name}")
        with open(os.path.join(BASE_DIR, f"{table_name}.csv"), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            rows = []
            columns = table_meta_data[table_name]
            column_names = list(columns.keys())

            for row in reader:
                print(row)
                row_tuple = tuple(
                    convert_value(row[col_name], columns[col_name])
                    for col_name in column_names
                )
                rows.append(row_tuple)

        insert_sql = build_insert_sql(table_name, columns)
        self.cursor.executemany(insert_sql, rows)

        self.conn.commit()

    def read_table(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)
        self.conn.close()

    def get_daily_demand_with_part_and_location(self):
        sql = """
            SELECT 
                d.demand_date,
                d.demand_quantity,
                p.part_code,
                w.facility_code,
                w.location_type
            FROM daily_demand d
            JOIN aircraft_parts p 
                ON d.part_id = p.part_id
            JOIN warehouse_locations w 
                ON d.location_id = w.location_id;
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()
