# table_name: {column_name: column_type}
table_type_data = {
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
        "is_secure": "TEXT",  # Yes/No
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

corruptible_tables = {
    "daily_demand": {"demand_quantity": "INTEGER NOT NULL",
                     "demand_date": "TEXT NOT NULL",
                     "location_id": "TEXT NOT NULL"
                     },
    "orders": {"location_id": "TEXT",
               "order_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
               "quantity_ordered": "INTEGER NOT NULL",
               "order_type": "TEXT",
               "due_date": "TEXT"
               },
    "stock_levels": {"quantity_on_hand": "INTEGER NOT NULL",
                     "snapshot_date": "TEXT NOT NULL",
                     "location_id": "TEXT"
                     },
    "supplier_lead_times": {"min_lead_time_days": "INTEGER",
                            "max_lead_time_days": "INTEGER",
                            "avg_lead_time_days": "INTEGER NOT NULL",
                            },
}

negatable_columns = {
    "daily_demand": ["demand_quantity"],
    "orders": ["quantity_ordered"],
    "stock_levels": ["quantity_on_hand"],
    "supplier_lead_times": ["min_lead_time_days", "max_lead_time_days", "avg_lead_time_days"],
}

global_outlier_columns = {
    "daily_demand": ["demand_quantity"],
    "orders": ["quantity_ordered"],
    "stock_levels": ["quantity_on_hand"],
    "supplier_lead_times": ["avg_lead_time_days"],
}

