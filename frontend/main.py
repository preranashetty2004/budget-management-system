import streamlit as st
import requests

st.title("Budget Management System")

# Add Income Form
st.header("Add Income")
with st.form("income_form"):
    user_id = st.number_input("User ID")
    amount = st.number_input("Amount")
    source = st.text_input("Source")
    date = st.date_input("Date")
    submitted = st.form_submit_button("Submit")
    if submitted:
        income_data = {
            "user_id": user_id,
            "amount": amount,
            "source": source,
            "date": str(date),
        }
        response = requests.post("http://localhost:5000/api/income", json=income_data)
        st.success("Income added successfully!")

# Add Expense Form
st.header("Add Expense")
with st.form("expense_form"):
    user_id = st.number_input("User ID")
    amount = st.number_input("Amount")
    category = st.text_input("Category")
    date = st.date_input("Date")
    submitted = st.form_submit_button("Submit")
    if submitted:
        expense_data = {
            "user_id": user_id,
            "amount": amount,
            "category": category,
            "date": str(date),
        }
        response = requests.post("http://localhost:5000/api/expenses", json=expense_data)
        st.success("Expense added successfully!")