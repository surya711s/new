import streamlit as st
import math
import re

# --- Page Configuration ---
st.set_page_config(page_title="Scientific Calculator", layout="centered")

# --- Initialize Session State ---
for key in ["expression", "memory", "last_result", "angle_mode"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "expression" else 0 if key == "memory" else "" if key == "last_result" else "Rad"

# --- Theme Selector ---
theme = st.radio("Choose Theme", ["🌙 Dark", "☀️ Light"], horizontal=True)

# --- Apply Theme ---
def apply_theme(theme):
    if theme == "🌙 Dark":
        st.markdown("""
            <style>
            body { background-color: #121212; color: white; }
            .stTextInput input {
                background-color: #1e1e1e !important;
                color: #00ffcc !important;
                font-size: 32px !important;
                text-align: right;
            }
            button {
                background-color: #2e2e2e !important;
                color: #eee !important;
                border-radius: 10px;
                height: 60px;
                font-size: 20px !important;
                font-weight: bold;
            }
            button:hover {
                background-color: #00ffcc !important;
                color: black !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            body { background-color: #ffffff; color: black; }
            .stTextInput input {
                background-color: #f0f0f0 !important;
                color: #003366 !important;
                font-size: 32px !important;
                text-align: right;
            }
            button {
                background-color: #eeeeee !important;
                color: #003366 !important;
                border-radius: 10px;
                height: 60px;
                font-size: 20px !important;
                font-weight: bold;
            }
            button:hover {
                background-color: #003366 !important;
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)

apply_theme(theme)

# --- Title & Display ---
st.markdown("<h1 style='text-align: center;'>🧮 Scientific Calculator</h1>", unsafe_allow_html=True)
with st.container():
    col1, col2 = st.columns([9, 1])
    with col1:
        st.session_state.expression = st.text_input("Display", st.session_state.expression, key="display", label_visibility="collapsed")
    with col2:
        if st.button("⌫", use_container_width=True):
            st.session_state.expression = st.session_state.expression[:-1]

# --- Help Section ---
with st.expander("📘 How to Use"):
    st.markdown("""
    - Type or click to build expressions.
    - Supported: `sin`, `cos`, `tan`, `log`, `ln`, `√`, `π`, `e`, `^`, `x!`, etc.
    - Use `Ans` to reuse last result.
    - `M+` stores current value, `MR` recalls it.
    - Click `Rad/Deg` to switch angle mode for trigonometric functions.
    """)

# --- Button Layout ---
buttons = [
    ["Rad", "Deg", "x!", "(", ")", "%", "Clear"],
    ["Inv", "sin", "ln", "7", "8", "9", "＋"],
    ["π", "cos", "log", "4", "5", "6", "−"],
    ["e", "tan", "√", "1", "2", "3", "×"],
    ["Ans", "EXP", "^", "0", ".", "=", "÷"],
    ["Σ", "M+", "MR", "MC", "", "", ""],
]

# --- Expression Cleaner ---
def clean_expression(expr):
    expr = expr.replace("×", "*").replace("÷", "/")
    expr = expr.replace("＋", "+").replace("−", "-")
    expr = expr.replace("π", str(math.pi)).replace("e", str(math.e))
    expr = expr.replace("^", "**").replace("√", "math.sqrt")
    expr = expr.replace("log", "math.log10").replace("ln", "math.log").replace("EXP", "math.exp")
    expr = expr.replace("Ans", str(st.session_state.last_result))

    expr = re.sub(r"(\d+|\([^()]+\))x!", lambda m: str(math.factorial(int(eval(m.group(1))))), expr)

    if st.session_state.angle_mode == "Deg":
        expr = re.sub(r"math\.sin\(([^)]+)\)", r"math.sin(math.radians(\1))", expr)
        expr = re.sub(r"math\.cos\(([^)]+)\)", r"math.cos(math.radians(\1))", expr)
        expr = re.sub(r"math\.tan\(([^)]+)\)", r"math.tan(math.radians(\1))", expr)

    return expr

# --- Input Handler ---
def handle_input(char):
    try:
        expr = st.session_state.expression

        if char == "Clear":
            st.session_state.expression = ""
        elif char == "=":
            expr = clean_expression(expr)
            result = eval(expr, {"math": math, "__builtins__": {}})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            st.session_state.expression = str(result)
            st.session_state.last_result = result
        elif char == "Σ":
            try:
                numbers = [float(n.strip()) for n in expr.replace(",", "+").split("+")]
                st.session_state.expression = str(sum(numbers))
            except:
                st.session_state.expression = "Error"
        elif char == "M+":
            st.session_state.memory = float(expr or "0")
        elif char == "MR":
            st.session_state.expression += str(st.session_state.memory)
        elif char == "MC":
            st.session_state.memory = 0
        elif char == "Rad":
            st.session_state.angle_mode = "Rad"
        elif char == "Deg":
            st.session_state.angle_mode = "Deg"
        else:
            st.session_state.expression += char

    except:
        st.session_state.expression = "Error"

# --- Render Buttons ---
for row in buttons:
    cols = st.columns(len(row))
    for i, btn in enumerate(row):
        with cols[i]:
            if btn != "" and st.button(btn, use_container_width=True, key=f"{btn}_{i}"):
                handle_input(btn)