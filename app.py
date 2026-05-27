import streamlit as st
import re
import random
import math
import sympy as sp

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="파티 계산기", page_icon="🎉", layout="centered")

# --- Session State (상태 관리) 초기화 ---
if "calc_state" not in st.session_state: st.session_state.calc_state = ""
if "history" not in st.session_state: st.session_state.history = ""

safe_math_dict = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "sqrt": math.sqrt,
    "π": math.pi
}

# --- 핵심 기능 로직 (콜백 함수) ---
def add_to_calc(val):
    if st.session_state.calc_state in ['Error', '방정식 문법 오류', '일반 수식 오류', '변수(x) 없음'] or any(x in st.session_state.calc_state for x in ["잭팟", "천사", "빨리", "="]):
        st.session_state.calc_state = ""
    st.session_state.calc_state += val

def clear_calc():
    st.session_state.calc_state = ""

def calculate():
    expr = st.session_state.calc_state
    if not expr: return
    
    if expr in ['777', '1004', '8282']:
        trigger_easter_egg(expr)
        return
        
    try:
        if re.match(r'^[\d\s\+\-\*\/\.\(\)sincotaqrpiπ]+$', expr):
            result = eval(expr, {"__builtins__": None}, safe_math_dict)
            if isinstance(result, float):
                result = round(result, 10)
                if result.is_integer(): result = int(result)
            st.session_state.history = f"{expr} = {result:,}\n" + st.session_state.history
            st.session_state.calc_state = str(result)
        else:
            st.session_state.calc_state = "일반 수식 오류"
    except Exception:
        st.session_state.calc_state = "Error"

def trigger_easter_egg(egg_type):
    if egg_type == '777':
        st.session_state.calc_state = "🎰 잭팟! 💰"
        st.balloons()
    elif egg_type == '1004':
        st.session_state.calc_state = "👼 천사 등장! ✨"
        st.snow()
    elif egg_type == '8282':
        st.session_state.calc_state = "🚀 빨리빨리! 🔥"
    st.session_state.history = f"*** 🎁 이스터에그: {egg_type} ***\n" + st.session_state.history

def solve_equation():
    expr = st.session_state.eq_input
    if not expr: return
    try:
        if '=' in expr:
            left, right = expr.split('=', 1)
            eq = sp.Eq(sp.sympify(left), sp.sympify(right))
        else:
            eq = sp.Eq(sp.sympify(expr), 0)
            
        symbols = list(eq.free_symbols)
        if not symbols:
            st.session_state.calc_state = "변수(x) 없음"
            return
            
        target_var = symbols[0]
        solutions = sp.solve(eq, target_var)
        sol_str = " 또는 ".join([str(s) for s in solutions]) if solutions else "해가 없음"
        formatted_result = f"{target_var} = {sol_str}"
        
        st.session_state.history = f"🧮 방정식: {expr} ➔ {formatted_result}\n" + st.session_state.history
        st.session_state.calc_state = formatted_result
    except Exception:
        st.session_state.calc_state = "방정식 문법 오류"

def do_nsplit():
    try:
        total = eval(st.session_state.calc_state, {"__builtins__": None}, safe_math_dict)
        num_people = st.session_state.people_input
        if total == 0: return
        split_amount = round(total / num_people)
        if isinstance(total, float) and total.is_integer(): total = int(total)
        
        st.session_state.history = f"💸 N빵: {total:,} / {num_people}명 = 1인당 {split_amount:,}\n" + st.session_state.history
        st.session_state.calc_state = str(split_amount)
        st.balloons() # N빵 성공 축하 풍선
    except Exception:
        st.session_state.calc_state = "Error"

def do_rand():
    try:
        min_v, max_v = st.session_state.r_min, st.session_state.r_max
        if min_v > max_v: min_v, max_v = max_v, min_v
            
        if st.session_state.r_type == '정수': 
            result = random.randint(int(min_v), int(max_v))
        else: 
            result = round(random.uniform(min_v, max_v), 4)
            
        st.session_state.history = f"🎲 랜덤 [{min_v} ~ {max_v}] = {result}\n" + st.session_state.history
        st.session_state.calc_state = str(result)
    except Exception:
        st.session_state.calc_state = "Error"

def btn_click(label):
    if label == '=': calculate()
    elif label == 'C': clear_calc()
    elif label in ['sin', 'cos', 'tan']: add_to_calc(label + '(')
    elif label == '√': add_to_calc('sqrt(')
    else: add_to_calc(label)

# --- UI 렌더링 ---
st.title("🎉 파티 계산기 v8.0")
st.markdown("웹 배포를 위한 **Streamlit 변환 버전**입니다! 스마트폰에서도 완벽하게 작동합니다.")

# 디스플레이 화면
st.info(f"**화면:** {st.session_state.calc_state}" if st.session_state.calc_state else "**화면:** 0", icon="📟")

# 특수 기능 탭
tab1, tab2, tab3 = st.tabs(["💸 N빵", "🎲 뽑기", "🧮 방정식"])

with tab1:
    c1, c2 = st.columns([2, 1])
    with c1: st.number_input("인원(명)", min_value=2, max_value=100, value=2, step=1, key="people_input")
    with c2: 
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("💸 N빵 계산", use_container_width=True, on_click=do_nsplit)

with tab2:
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1.5])
    with c1: st.number_input("최소값", value=1.0, key="r_min")
    with c2: st.number_input("최대값", value=100.0, key="r_max")
    with c3: st.selectbox("타입", ["정수", "실수"], key="r_type")
    with c4: 
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🎲 뽑기", use_container_width=True, on_click=do_rand)

with tab3:
    st.text_input("방정식 입력 (예: 2*x - 4 = 10)", key="eq_input")
    st.button("🧮 방정식 풀기", use_container_width=True, on_click=solve_equation)

st.divider()

# 계산기 버튼 (5x5 배열)
buttons = [
    ['sin', 'cos', 'tan', 'π', 'C'],
    ['√', '**', '(', ')', '/'],
    ['7', '8', '9', '.', '*'],
    ['4', '5', '6', '+', '-'],
    ['1', '2', '3', '0', '=']
]

for row in buttons:
    cols = st.columns(5)
    for i, label in enumerate(row):
        cols[i].button(label, use_container_width=True, on_click=btn_click, args=(label,))

st.divider()

# 영수증 내역
st.subheader("📜 영수증 (History)")
st.text_area("계산 내역 (최근 순)", value=st.session_state.history, height=150, disabled=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("🗑️ 영수증 지우기", use_container_width=True):
        st.session_state.history = ""
        clear_calc()
        st.rerun()
with c2:
    st.download_button("💾 텍스트로 저장", data=st.session_state.history, file_name="receipt.txt", mime="text/plain", use_container_width=True)
