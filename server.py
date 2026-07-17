from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import psycopg2
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from psycopg2.extras import RealDictCursor


# ---------------------------------------------------------
# ENVIRONMENT CONFIGURATION
# ---------------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Add it to the .env file.\n"
        "Example:\n"
        "DATABASE_URL=postgresql://postgres:password@localhost:5432/employee"
    )


# ---------------------------------------------------------
# MCP SERVER
# ---------------------------------------------------------

mcp = FastMCP("Employee Knowledge Assistant")


# ---------------------------------------------------------
# DATABASE HELPERS
# ---------------------------------------------------------

def get_db_connection():
    """Create and return a PostgreSQL connection."""

    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor,
    )


def serialize_value(value: Any) -> Any:
    """Convert PostgreSQL values into JSON-compatible values."""

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    return value


def serialize_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert a PostgreSQL row into a JSON-compatible dictionary."""

    if row is None:
        return None

    return {
        key: serialize_value(value)
        for key, value in dict(row).items()
    }


def serialize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert multiple PostgreSQL rows into JSON-compatible dictionaries."""

    return [
        serialize_row(row)
        for row in rows
        if row is not None
    ]


# ---------------------------------------------------------
# BASIC MCP TEST TOOLS
# ---------------------------------------------------------

@mcp.tool()
def hello() -> str:
    """Verify that the MCP server is working."""

    return "Hello from the PostgreSQL Employee Knowledge Assistant!"


@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""

    cleaned_name = name.strip()

    if not cleaned_name:
        return "Please provide a valid name."

    return f"Hello, {cleaned_name}!"


# ---------------------------------------------------------
# EMPLOYEE READ TOOLS
# ---------------------------------------------------------

@mcp.tool()
def list_employees() -> dict[str, Any]:
    """Return all employees from PostgreSQL."""

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    designation,
                    manager,
                    location,
                    phone,
                    hire_date,
                    skills,
                    salary
                FROM employees
                ORDER BY id;
                """
            )

            employees = cursor.fetchall()

        return {
            "success": True,
            "count": len(employees),
            "employees": serialize_rows(employees),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Unable to list employees: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


@mcp.tool()
def get_employee_by_id(employee_id: str) -> dict[str, Any]:
    """Return one employee using an employee ID such as EMP001."""

    cleaned_employee_id = employee_id.strip()

    if not cleaned_employee_id:
        return {
            "success": False,
            "error": "Please provide an employee ID.",
        }

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    designation,
                    manager,
                    location,
                    phone,
                    hire_date,
                    skills,
                    salary
                FROM employees
                WHERE LOWER(employee_id) = LOWER(%s);
                """,
                (cleaned_employee_id,),
            )

            employee = cursor.fetchone()

        if employee is None:
            return {
                "success": False,
                "error": f"No employee found with ID {cleaned_employee_id}.",
            }

        return {
            "success": True,
            "employee": serialize_row(employee),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Unable to retrieve employee: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


@mcp.tool()
def search_employee(name: str) -> dict[str, Any]:
    """Search employees using a full or partial employee name."""

    cleaned_name = name.strip()

    if not cleaned_name:
        return {
            "success": False,
            "error": "Please provide an employee name.",
        }

    connection = None

    try:
        connection = get_db_connection()

        search_pattern = f"%{cleaned_name}%"

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    designation,
                    manager,
                    location,
                    phone,
                    hire_date,
                    skills,
                    salary
                FROM employees
                WHERE
                    first_name ILIKE %s
                    OR last_name ILIKE %s
                    OR CONCAT(first_name, ' ', last_name) ILIKE %s
                ORDER BY first_name, last_name;
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
                ),
            )

            employees = cursor.fetchall()

        return {
            "success": True,
            "search": cleaned_name,
            "count": len(employees),
            "employees": serialize_rows(employees),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Unable to search employees: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


@mcp.tool()
def search_employees(keyword: str) -> dict[str, Any]:
    """
    Search employees by employee ID, name, email, department,
    designation, manager, location, or skills.
    """

    cleaned_keyword = keyword.strip()

    if not cleaned_keyword:
        return {
            "success": False,
            "error": "Please provide a search keyword.",
        }

    connection = None

    try:
        connection = get_db_connection()
        search_pattern = f"%{cleaned_keyword}%"

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    designation,
                    manager,
                    location,
                    phone,
                    hire_date,
                    skills,
                    salary
                FROM employees
                WHERE
                    employee_id ILIKE %s
                    OR first_name ILIKE %s
                    OR last_name ILIKE %s
                    OR CONCAT(first_name, ' ', last_name) ILIKE %s
                    OR email ILIKE %s
                    OR department ILIKE %s
                    OR designation ILIKE %s
                    OR manager ILIKE %s
                    OR location ILIKE %s
                    OR skills ILIKE %s
                ORDER BY first_name, last_name;
                """,
                tuple([search_pattern] * 10),
            )

            employees = cursor.fetchall()

        return {
            "success": True,
            "keyword": cleaned_keyword,
            "count": len(employees),
            "employees": serialize_rows(employees),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Unable to search employees: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


@mcp.tool()
def search_by_department(department: str) -> dict[str, Any]:
    """Return employees belonging to a department."""

    cleaned_department = department.strip()

    if not cleaned_department:
        return {
            "success": False,
            "error": "Please provide a department name.",
        }

    connection = None

    try:
        connection = get_db_connection()
        search_pattern = f"%{cleaned_department}%"

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    designation,
                    manager,
                    location,
                    phone,
                    hire_date,
                    skills,
                    salary
                FROM employees
                WHERE department ILIKE %s
                ORDER BY first_name, last_name;
                """,
                (search_pattern,),
            )

            employees = cursor.fetchall()

        return {
            "success": True,
            "department": cleaned_department,
            "count": len(employees),
            "employees": serialize_rows(employees),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Unable to filter employees: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


# ---------------------------------------------------------
# EMPLOYEE WRITE TOOLS
# ---------------------------------------------------------

@mcp.tool()
def add_employee(
    employee_id: str,
    first_name: str,
    last_name: str,
    email: str,
    department: str,
    designation: str,
    manager: str = "",
    location: str = "",
    phone: str = "",
    hire_date: str | None = None,
    skills: str = "",
    salary: float | None = None,
) -> dict[str, Any]:
    """Add a new employee to PostgreSQL."""

    required_values = {
        "employee_id": employee_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "department": department,
        "designation": designation,
    }

    missing_fields = [
        field
        for field, value in required_values.items()
        if not value.strip()
    ]

    if missing_fields:
        return {
            "success": False,
            "error": (
                "Missing required fields: "
                + ", ".join(missing_fields)
            ),
        }

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employees (
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    designation,
                    manager,
                    location,
                    phone,
                    hire_date,
                    skills,
                    salary
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                RETURNING *;
                """,
                (
                    employee_id.strip(),
                    first_name.strip(),
                    last_name.strip(),
                    email.strip(),
                    department.strip(),
                    designation.strip(),
                    manager.strip() or None,
                    location.strip() or None,
                    phone.strip() or None,
                    hire_date or None,
                    skills.strip() or None,
                    salary,
                ),
            )

            employee = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Employee added successfully.",
            "employee": serialize_row(employee),
        }

    except psycopg2.errors.UniqueViolation:
        if connection is not None:
            connection.rollback()

        return {
            "success": False,
            "error": (
                f"Employee ID {employee_id} or email {email} "
                "already exists."
            ),
        }

    except Exception as exc:
        if connection is not None:
            connection.rollback()

        return {
            "success": False,
            "error": f"Unable to add employee: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


@mcp.tool()
def update_employee(
    employee_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    manager: str | None = None,
    location: str | None = None,
    phone: str | None = None,
    hire_date: str | None = None,
    skills: str | None = None,
    salary: float | None = None,
) -> dict[str, Any]:
    """Update an existing employee."""

    cleaned_employee_id = employee_id.strip()

    if not cleaned_employee_id:
        return {
            "success": False,
            "error": "Please provide an employee ID.",
        }

    updates: list[str] = []
    values: list[Any] = []

    fields = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "department": department,
        "designation": designation,
        "manager": manager,
        "location": location,
        "phone": phone,
        "hire_date": hire_date,
        "skills": skills,
        "salary": salary,
    }

    for column, value in fields.items():
        if value is not None:
            updates.append(f"{column} = %s")

            if isinstance(value, str):
                values.append(value.strip() or None)
            else:
                values.append(value)

    if not updates:
        return {
            "success": False,
            "error": "No update values were provided.",
        }

    values.append(cleaned_employee_id)

    connection = None

    try:
        connection = get_db_connection()

        query = f"""
            UPDATE employees
            SET {", ".join(updates)}
            WHERE LOWER(employee_id) = LOWER(%s)
            RETURNING *;
        """

        with connection.cursor() as cursor:
            cursor.execute(query, tuple(values))
            employee = cursor.fetchone()

        if employee is None:
            connection.rollback()

            return {
                "success": False,
                "error": f"Employee {cleaned_employee_id} was not found.",
            }

        connection.commit()

        return {
            "success": True,
            "message": "Employee updated successfully.",
            "employee": serialize_row(employee),
        }

    except Exception as exc:
        if connection is not None:
            connection.rollback()

        return {
            "success": False,
            "error": f"Unable to update employee: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


@mcp.tool()
def delete_employee(employee_id: str) -> dict[str, Any]:
    """Delete an employee using an employee ID."""

    cleaned_employee_id = employee_id.strip()

    if not cleaned_employee_id:
        return {
            "success": False,
            "error": "Please provide an employee ID.",
        }

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM employees
                WHERE LOWER(employee_id) = LOWER(%s)
                RETURNING employee_id, first_name, last_name;
                """,
                (cleaned_employee_id,),
            )

            deleted_employee = cursor.fetchone()

        if deleted_employee is None:
            connection.rollback()

            return {
                "success": False,
                "error": f"Employee {cleaned_employee_id} was not found.",
            }

        connection.commit()

        return {
            "success": True,
            "message": f"Employee {cleaned_employee_id} deleted successfully.",
            "employee": serialize_row(deleted_employee),
        }

    except Exception as exc:
        if connection is not None:
            connection.rollback()

        return {
            "success": False,
            "error": f"Unable to delete employee: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


# ---------------------------------------------------------
# SUMMARY TOOL
# ---------------------------------------------------------

@mcp.tool()
def employee_summary() -> dict[str, Any]:
    """Return employee totals, departments, locations, and salary statistics."""

    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) AS total_employees
                FROM employees;
                """
            )
            total_result = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    COALESCE(department, 'Unknown') AS department,
                    COUNT(*) AS employee_count
                FROM employees
                GROUP BY COALESCE(department, 'Unknown')
                ORDER BY employee_count DESC, department;
                """
            )
            department_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    COALESCE(location, 'Unknown') AS location,
                    COUNT(*) AS employee_count
                FROM employees
                GROUP BY COALESCE(location, 'Unknown')
                ORDER BY employee_count DESC, location;
                """
            )
            location_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    ROUND(AVG(salary), 2) AS average_salary,
                    MIN(salary) AS minimum_salary,
                    MAX(salary) AS maximum_salary
                FROM employees
                WHERE salary IS NOT NULL;
                """
            )
            salary_result = cursor.fetchone()

        return {
            "success": True,
            "total_employees": total_result["total_employees"],
            "department_counts": serialize_rows(department_rows),
            "location_counts": serialize_rows(location_rows),
            "salary_statistics": serialize_row(salary_result),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Unable to generate employee summary: {exc}",
        }

    finally:
        if connection is not None:
            connection.close()


# ---------------------------------------------------------
# START MCP SERVER
# ---------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")