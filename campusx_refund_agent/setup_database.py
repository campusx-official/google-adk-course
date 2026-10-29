import sqlite3

from datetime import datetime, timedelta, timezone
from pathlib import Path


# Create the database alongside this script.
DB_PATH = Path(__file__).resolve().parent / "campusx.db"


def setup_database():
    # Prevent accidental overwriting of existing data.
    if DB_PATH.exists():
        raise SystemExit(
            f"Database already exists: {DB_PATH}\n"
            "No changes were made."
        )

    now = datetime.now(timezone.utc)

    def purchased_days_ago(days):
        return (
            now - timedelta(days=days)
        ).isoformat()

    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            connection.execute("PRAGMA foreign_keys = ON")

            # ----------------------------------
            # 1. Create the three tables
            # ----------------------------------

            connection.executescript("""
                CREATE TABLE students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL COLLATE NOCASE UNIQUE
                );

                CREATE TABLE courses (
                    course_id TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0)
                );

                CREATE TABLE enrollments (
                    enrollment_id TEXT PRIMARY KEY,

                    student_id TEXT NOT NULL
                        REFERENCES students(student_id),

                    course_id TEXT NOT NULL
                        REFERENCES courses(course_id),

                    purchased_at TEXT NOT NULL,

                    amount_paid INTEGER NOT NULL
                        CHECK (amount_paid >= 0),

                    completion_percent REAL NOT NULL
                        CHECK (
                            completion_percent BETWEEN 0 AND 100
                        ),

                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK (
                            status IN (
                                'active',
                                'refund_requested',
                                'refunded'
                            )
                        ),

                    refund_reason TEXT
                );
            """)

            # ----------------------------------
            # 2. Insert 3 courses
            # Prices are in whole INR.
            # ----------------------------------

            courses = [
                ("C001", "Google ADK", 1999),
                ("C002", "LLMOps", 2499),
                ("C003", "Advanced RAG", 1999),
            ]

            connection.executemany(
                """
                INSERT INTO courses (
                    course_id,
                    course_name,
                    price
                )
                VALUES (?, ?, ?)
                """,
                courses,
            )

            # ----------------------------------
            # 3. Insert 5 students
            # ----------------------------------

            students = [
                ("STU001", "Rahul Sharma", "rahul@example.com"),
                ("STU002", "Priya Singh", "priya@example.com"),
                ("STU003", "Aman Gupta", "aman@example.com"),
                ("STU004", "Neha Verma", "neha@example.com"),
                ("STU005", "Vikram Mehta", "vikram@example.com"),
            ]

            connection.executemany(
                """
                INSERT INTO students (
                    student_id,
                    name,
                    email
                )
                VALUES (?, ?, ?)
                """,
                students,
            )

            # ----------------------------------
            # 4. Insert 10 enrollments
            # Each student has two enrollments.
            # ----------------------------------

            enrollments = [
                # Rahul: eligible, with a discounted purchase.
                (
                    "ENR001", "STU001", "C001",
                    purchased_days_ago(2),
                    1499, 15, "active", None,
                ),

                # Rahul: outside the 7-day window.
                (
                    "ENR002", "STU001", "C002",
                    purchased_days_ago(10),
                    2499, 5, "active", None,
                ),

                # Priya: eligible.
                (
                    "ENR003", "STU002", "C001",
                    purchased_days_ago(1),
                    1999, 10, "active", None,
                ),

                # Priya: completion exceeds 20%.
                (
                    "ENR004", "STU002", "C003",
                    purchased_days_ago(3),
                    1999, 45, "active", None,
                ),

                # Aman: refund already requested.
                (
                    "ENR005", "STU003", "C002",
                    purchased_days_ago(2),
                    2499, 10,
                    "refund_requested",
                    "Purchased the wrong course",
                ),

                # Aman: already refunded.
                (
                    "ENR006", "STU003", "C003",
                    purchased_days_ago(4),
                    1999, 5,
                    "refunded",
                    "Changed my learning plans",
                ),

                # Neha: exactly 20% completion, eligible.
                (
                    "ENR007", "STU004", "C001",
                    purchased_days_ago(6),
                    1999, 20, "active", None,
                ),

                # Neha: both limits exceeded.
                (
                    "ENR008", "STU004", "C002",
                    purchased_days_ago(12),
                    2499, 60, "active", None,
                ),

                # Vikram: eligible, no content consumed.
                (
                    "ENR009", "STU005", "C003",
                    purchased_days_ago(1),
                    1999, 0, "active", None,
                ),

                # Vikram: recent purchase, too much completion.
                (
                    "ENR010", "STU005", "C002",
                    purchased_days_ago(2),
                    2499, 80, "active", None,
                ),
            ]

            connection.executemany(
                """
                INSERT INTO enrollments (
                    enrollment_id,
                    student_id,
                    course_id,
                    purchased_at,
                    amount_paid,
                    completion_percent,
                    status,
                    refund_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                enrollments,
            )

        print(f"Database created: {DB_PATH}")

        for table in ("courses", "students", "enrollments"):
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count}")

    finally:
        connection.close()


if __name__ == "__main__":
    setup_database()