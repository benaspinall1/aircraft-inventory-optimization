import sqlite3
from csv import DictReader

import os
import pandas as pd
import data.table_metadata as tmd

DB_FILE = "data/supply_chain.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_insert_sql(table_name: str, columns_dict: dict) -> str:
    column_names = []
    for col_name, col_type in columns_dict.items():
        column_names.append(f"{col_name}")

    # Join all columns with comma, new-line, and tab
    columns_sql = ",\n    ".join(column_names)

    question_marks = ["?"] * len(column_names)
    qm_sql = ", ".join(question_marks)  # for the "VALUES(?, ?, ?, ?, ?)" syntax

    insert_sql = f"""
    INSERT INTO {table_name} (
        {columns_sql}
    )
    VALUES({qm_sql})
    """

    return insert_sql


def build_create_table_sql(table_name: str, columns_dict: dict) -> str:
    column_definitions = []
    for col_name, col_type in columns_dict.items():
        column_definitions.append(f"{col_name} {col_type}")

    # Join all columns with comma, new-line, and tab
    sql_statements = column_definitions + tmd.foreign_key_relationships[table_name]
    sql_statements = ",\n    ".join(sql_statements)
    foreign_keys = ",\n    ".join(tmd.foreign_key_relationships[table_name])
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {sql_statements}
    );
    """

    return create_sql


def convert_value(value, column_type: str) -> int | float | str | None:
    # print("Value to convert", value)
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
    table_names = tmd.table_type_data.keys()
    for name in table_names:
        print(name)


def delete_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # delete entire DB file


class Database:
    def __init__(self, corruptor_chain):
        delete_db()
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self.corruptor_chain = corruptor_chain
        table_names = tmd.table_type_data.keys()

        for table in table_names:
            self.corruptor_chain.set_table_name(table)
            self.create_table(table)
            self.seed_table(table)

    def close(self):
        self.conn.close()

    def create_table(self, table_name: str):
        columns = tmd.table_type_data[table_name]
        create_sql = build_create_table_sql(table_name, columns)
        #        print(create_sql)
        self.cursor.execute(create_sql)
        self.conn.commit()

    def seed_table(self, table_name: str):
        self.cursor.execute(f"DELETE FROM {table_name}")
        #       print(f"Seeding Table: {table_name}")
        with open(os.path.join(BASE_DIR, f"ai_generated/{table_name}.csv"), newline="", encoding="utf-8") as file:
            reader = DictReader(file)

            rows = []
            columns = tmd.table_type_data[table_name]
            column_names = list(columns.keys())

            for row in reader:
                #              print(row)
                row_tuple = tuple(
                    convert_value(row[col_name], columns[col_name])
                    for col_name in column_names
                )
                rows.append(row_tuple)

            if table_name in tmd.corruptible_tables:
                self.corruptor_chain.set_table_name(table_name)
                rows_df = pd.DataFrame(rows, columns=columns)
                dirty_df, audit = self.corruptor_chain.run(rows_df)
                print("Table Name: ", table_name)
                print(dirty_df)
                print("Audit")
                for log in audit:
                    print(log)
                print()

        insert_sql = build_insert_sql(table_name, columns)
        self.cursor.executemany(insert_sql, rows)

        self.conn.commit()

    def read_table(self, table_name: str):
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
