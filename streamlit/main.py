import streamlit as st
import requests
from datetime import datetime
from jose import jwt
import os
import pandas as pd
import base64
from io import BytesIO

# Configuration: Use Docker service names
AUTH_SERVICE_URL = "http://auth-service:8003"
TRANSACTION_SERVICE_URL = "http://transaction-service:8000"
WALLET_SERVICE_URL = "http://wallet-service:8002"
ML_SERVICE_URL = "http://ml-service:8001"

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")

st.set_page_config(page_title="ML Text Analyzer", layout="centered")

# --- Auth Functions ---
def login(username, password):
    response = requests.post(
        f"{AUTH_SERVICE_URL}/login",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Ошибка авторизации")
        return None

def register_user(email, name, login, password, phone=None):
    payload = {
        "email": email,
        "name": name,
        "login": login,
        "password": password
    }
    if phone:
        payload["phone"] = phone

    response = requests.post(f"{AUTH_SERVICE_URL}/register", json=payload)
    if response.status_code == 200:
        st.success("Регистрация прошла успешно!")
    else:
        st.error(response.json().get("detail", "Registration failed"))

def get_me(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{AUTH_SERVICE_URL}/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ошибка при получении информации о пользователе")
        return None

# --- Wallet Functions ---
def get_wallet(token, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{WALLET_SERVICE_URL}/wallet/{user_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.warning("Не удалось получить информацию о кошельке")
        return None

def topup_wallet(token, user_id, amount):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{WALLET_SERVICE_URL}/wallet/{user_id}/topup",
        headers=headers,
        json={"amount": amount}
    )
    if response.status_code == 200:
        st.success("Кошелек успешно пополнен!")
        wallet_data = response.json()
        st.session_state['balance'] = wallet_data['balance']
        return wallet_data
    else:
        st.error(response.json().get("detail", "Пополнение кошелька не удалось"))
        return None

# --- Model Management ---
def get_models(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ML_SERVICE_URL}/models", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ошибка при получении списка моделей")
        return []

# --- ML Analysis Function ---
def analyze_text(token, texts, model_id):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"texts": texts, "model_id": model_id}
    
    try:
        response = requests.post(
            f"{TRANSACTION_SERVICE_URL}/analyze",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            # Read CSV data into DataFrame for preview
            df = pd.read_csv(BytesIO(response.content))
            return {
                "success": True,
                "data": df,
                "csv_data": response.content
            }
        else:
            return {
                "success": False,
                "error": response.json().get("detail", "Analysis failed")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
def get_history(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{TRANSACTION_SERVICE_URL}/history", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ошибка при получении истории")
        return []

# --- UI Logic ---
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.models = []
    st.session_state.balance = None

if not st.session_state.token:
    st.title("ML Text Analyzer")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Логин")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            token = login(username, password)
            if token:
                st.session_state.token = token
                st.session_state.user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = int(st.session_state.user["sub"])
                wallet = get_wallet(token, user_id)
                st.session_state.balance = wallet['balance'] if wallet else 0
                st.rerun()

    with tab2:
        st.subheader("Регистрация")
        name = st.text_input("Имя", key="reg_name")
        login = st.text_input("Login", key="reg_login")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        phone = st.text_input("Phone (optional)", key="reg_phone")

        if st.button("Регистрация"):
            if not name or not login or not password:
                st.warning("Пожалуйста, заполните все поля")
            else:
                register_user(email=email, name=name, login=login, password=password, phone=phone)

else:
    st.sidebar.title("Меню")
    if st.sidebar.button("Выйти"):
        st.session_state.clear()
        st.rerun()

    user_data = get_me(st.session_state.token)
    if user_data:
        st.sidebar.write(f"Вошли как {user_data['login']}")

    user_id = int(st.session_state.user["sub"])
    wallet = get_wallet(st.session_state.token, user_id)
    if 'balance' not in st.session_state:
        st.session_state['balance'] = wallet['balance'] if wallet else 0

    wallet_placeholder = st.sidebar.empty()
    wallet_placeholder.metric("Баланс", f"{st.session_state['balance']} марок")

    topup_amount = st.sidebar.number_input("Пополнить на", min_value=1, step=1)
    if st.sidebar.button("Пополнить"):
        topup_wallet(st.session_state.token, user_id, topup_amount)
        st.rerun()

    st.header("Анализ текста")

    if not st.session_state.models:
        with st.spinner("Загрузка моделей..."):
            models = get_models(st.session_state.token)
            st.session_state.models = models

    if st.session_state.models:
        model_name_to_id = {model["name"]: model["id"] for model in st.session_state.models}
        selected_model_name = st.selectbox("Выберите модель", options=list(model_name_to_id.keys()))
        selected_model_id = model_name_to_id[selected_model_name]

        text_input = st.text_area("Введите текст для анализа, каждый текст на новой строке")
        texts = [line.strip() for line in text_input.splitlines() if line.strip()]

        if st.button("Анализиировать на токсичность"):
            if len(texts) == 0:
                st.warning("Пожалуйста, введите хотя бы один текст для анализа")
            else:
                result = analyze_text(st.session_state.token, texts, selected_model_id)
                if result and result["success"]:
                    st.session_state['last_analysis'] = result
                    st.success("Анализ завершен!")
                    
                    # Show preview of the data
                    st.dataframe(result["data"])
                    
                    # Download button
                    st.download_button(
                        label="Download CSV",
                        data=result["csv_data"],
                        file_name="analysis_results.csv",
                        mime="text/csv"
                    )

                    wallet = get_wallet(st.session_state.token, user_id)
                    st.session_state['balance'] = wallet['balance'] if wallet else 0
                    wallet_placeholder.metric("Wallet Balance", f"{st.session_state['balance']} coins")
                    
                elif not result["success"]:
                    st.error(result["error"])
    else:
        st.info("No models available.")
        
    with st.expander("📜 Посмотреть историю"):
        if st.button("История"):
            history_data = get_history(st.session_state.token)
            if history_data:
                for entry in history_data:
                    if entry["start_at"]:
                        entry["start_at"] = entry["start_at"].replace("T", " ").split(".")[0]
                    if entry["end_at"]:
                        entry["end_at"] = entry["end_at"].replace("T", " ").split(".")[0]
                    else:
                        entry["end_at"] = "In Progress"
                    if entry["cost"] is None:
                        entry["cost"] = 0

                df = pd.DataFrame(history_data)
                df = df.rename(columns={
                    "model_name": "Model",
                    "start_at": "Started",
                    "end_at": "Ended",
                    "status": "Status",
                    "cost": "Total Cost"
                })
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Не найдено логов.")