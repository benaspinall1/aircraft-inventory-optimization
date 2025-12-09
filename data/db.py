import sqlite3
import csv


class Database:
    def __init__(self, csv_file, db_file):
        self.parts_csv = csv_file
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_parts_table()
        self.csv_to_db()

    def csv_to_db(self):

        self.cursor.execute("DELETE FROM parts")
        with open(self.parts_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # ✅ MUST be DictReader

            rows = []
            for row in reader:
                rows.append((
                    int(row["part_id"]),
                    row["part_code"],
                    row["category"],
                    row["description"],
                    row["ata_chapter"],
                    row["criticality"],
                    float(row["unit_cost_usd"]),
                    int(row["lead_time_days"])
                ))

        self.cursor.executemany("""
            INSERT INTO parts (
                part_id,
                part_code,
                category,
                description,
                ata_chapter,
                criticality,
                unit_cost_usd,
                lead_time_days
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

        self.conn.commit()

    def create_parts_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            part_id INTEGER PRIMARY KEY,
            part_code TEXT,
            category TEXT,
            description TEXT,
            ata_chapter INTEGER,
            criticality TEXT,
            unit_cost_usd REAL,
            lead_time_days INTEGER
        )
        """)

    def read_parts(self):
        # Read Data
        self.cursor.execute("SELECT * FROM parts")
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)
        self.conn.close()

