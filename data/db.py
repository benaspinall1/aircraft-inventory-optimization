import sqlite3
import csv
import os

DB_FILE = "inventory.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "aircraft_parts.csv")


class Database:
    def __init__(self):
        self.parts_csv = CSV_FILE
        self.conn = sqlite3.connect(DB_FILE)
        print("Connected to DB")
        self.cursor = self.conn.cursor()

    def read_parts_csv(self):
        with open(CSV_FILE, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                print(row)

    def close(self):
        print("Closing DB connection")
        self.conn.close()


# self.cursor.executemany("""
# INSERT INTO parts (part_code, description, unit_cost, lead_time_days)
# VALUES (?, ?, ?, ?)
# """, rows)
#
# conn.commit()
# conn.close()
#
# print("✅ CSV data inserted successfully!")
