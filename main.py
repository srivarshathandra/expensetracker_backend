# uvicorn :-- server name
# FstALP():-- api creator in backend
from fastapi import FastAPI, Form
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

#---CORS Policy---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

conn_obj = mysql.connector.connect(
    host=os.getenv("db_host"),
    user=os.getenv("db_user"),
    port=os.getenv("db_port"),
    password=os.getenv("db_password"),
    database=os.getenv("db_name")
)

cursor_obj = conn_obj.cursor()

# ---------------- TABLE ----------------
cursor_obj.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    category VARCHAR(100),
    amount FLOAT,
    payment_method VARCHAR(50),
    description VARCHAR(255)
)
""")

conn_obj.commit()


@app.get("/")
def home():

    return {
        "message": "Expense Tracker API Running Successfully"
    }


# ---------------- ADD EXPENSE ----------------
@app.post("/add_expense")
def add_expense(
    date: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    description: str = Form(...)
):

    query = """
    INSERT INTO expenses
    (date, category, amount, payment_method, description)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (date, category, amount, payment_method, description)

    cursor_obj.execute(query, values)
    conn_obj.commit()

    return {"message": "Expense added successfully!"}
# ---------------- VIEW EXPENSES ----------------
@app.get("/view_expenses")
def view_expenses():

    query = "SELECT * FROM expenses"
    cursor_obj.execute(query)
    data = cursor_obj.fetchall()
    expenses = []
    for row in data:
        expenses.append({
            "Expense ID": row[0],
            "Date": str(row[1]),
            "Category": row[2],
            "Amount": row[3],
            "Payment Method": row[4],
            "Description": row[5]
        })
    return expenses

# ---------------- UPDATE EXPENSE ----------------
from fastapi import Form

@app.put("/update_expense/{expense_id}")
def update_expense(
    expense_id: int,
    date: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    description: str = Form(...)
):

    query = """
    UPDATE expenses
    SET date=%s, category=%s, amount=%s, payment_method=%s, description=%s
    WHERE expense_id=%s
    """

    values = (date, category, amount, payment_method, description, expense_id)

    cursor_obj.execute(query, values)
    conn_obj.commit()

    return {"message": "Expense updated successfully!"}

# ---------------- DELETE EXPENSE ----------------
@app.delete("/delete_expense/{expense_id}")
def delete_expense(expense_id: int):

    query = "DELETE FROM expenses WHERE expense_id = %s"
    cursor_obj.execute(query, (expense_id,))
    conn_obj.commit()
    # check if anything was actually deleted
    if cursor_obj.rowcount == 0:
        return {
            "message": "No expense found with this ID"
        }
    return {
        "message": "Expense deleted successfully!"
    }
# ---------------- SEARCH EXPENSES ----------------
@app.get("/search_expenses")
def search_expenses(category: str):
    cursor_obj.execute("""
    SELECT * FROM expenses
    WHERE category = %s
    """, (category,))
    data = cursor_obj.fetchall()
    expenses = []
    for row in data:

        expenses.append({
            "Expense ID": row[0],
            "Date": str(row[1]),
            "Category": row[2],
            "Amount": row[3],
            "Payment Method": row[4],
            "Description": row[5]
        })
    return expenses     
# ---------------- SORT EXPENSES ----------------
@app.get("/sort_expenses")
def sort_expenses(sort_by: str,order: str):
    if sort_by not in ["date", "amount", "category"]:
        return {
            "error": "Invalid sort field"
        }
    if order not in ["asc", "desc"]:
        return {
            "error": "Invalid order"
        }
    query = f"""
    SELECT * FROM expenses
    ORDER BY {sort_by} {order}
    """
    cursor_obj.execute(query)
    data = cursor_obj.fetchall()
    expenses = []
    for row in data:
        expenses.append({
            "Expense ID": row[0],
            "Date": str(row[1]),
            "Category": row[2],
            "Amount": row[3],
            "Payment Method": row[4],
            "Description": row[5]
        })
    return expenses
#----------------- FILTER ----------------

@app.get("/filter_expenses")
def filter_expenses(
    category: str,
    min_amount: float,
    max_amount: float
):
    query = """
    SELECT * FROM expenses
    WHERE category = %s
    AND amount BETWEEN %s AND %s
    """
    values = (category,min_amount,max_amount)
    cursor_obj.execute(query, values)
    data = cursor_obj.fetchall()
    expenses = []
    for row in data:
        expenses.append({
            "Expense ID": row[0],
            "Date": str(row[1]),
            "Category": row[2],
            "Amount": row[3],
            "Payment Method": row[4],
            "Description": row[5]
        })
    return expenses

# ---------------- GENERATE REPORT ----------------
@app.get("/generate_report")
def generate_report(report_type: str):
    cursor_obj.execute("SELECT * FROM expenses")
    data = cursor_obj.fetchall()
    expenses = []
    for row in data:
        expenses.append({
            "Expense ID": row[0],
            "Date": str(row[1]),
            "Category": row[2],
            "Amount": row[3],
            "Payment Method": row[4],
            "Description": row[5]
        })
    cursor_obj.execute(
        "SELECT SUM(amount) FROM expenses"
    )
    total_amount = cursor_obj.fetchone()[0]
    return {
        "report_type": report_type,
        "total_amount": total_amount,
        "expenses": expenses
    }

# ---------------- ANALYZE SPENDING ----------------
@app.get("/analyze_spending")
def analyze_spending():
    # Category-wise Analysis
    cursor_obj.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)
    category_data = cursor_obj.fetchall()
    category_analysis = []
    for row in category_data:
        category_analysis.append({
            "Category": row[0],
            "Total Amount": row[1]
        })
    # Payment Method Analysis
    cursor_obj.execute("""
    SELECT payment_method, SUM(amount)
    FROM expenses
    GROUP BY payment_method
    """)
    payment_data = cursor_obj.fetchall()
    payment_analysis = []
    for row in payment_data:
        payment_analysis.append({
            "Payment Method": row[0],
            "Total Amount": row[1]
        })
    # Total Spending
    cursor_obj.execute("""
    SELECT SUM(amount)
    FROM expenses
    """)
    total_spending = cursor_obj.fetchone()[0]
    return {
        "total_spending": total_spending,
        "category_analysis": category_analysis,
        "payment_analysis": payment_analysis
    }