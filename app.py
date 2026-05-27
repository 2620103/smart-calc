import streamlit as st
import re
import random
import math
import sympy as sp

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="나만의 계산기", page_icon="🎉", layout="centered")

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

# --- 핵심 기능 로직 ---
def add_to_calc(val):
    if st.session_state.calc_state in ['Error', '방정식 문법 오류', '일반 수식 오류', '변수(x, y 등) 없음'] or any(x in st.session_state.calc_state for x in ["잭팟", "천사", "빨리", "="]):
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

# ★ 연립방정식 지원으로 업그레이드된 로직 ★
def solve_equation():
    expr = st.session_state.eq_input
    if not expr: return
    
    try:
        # 쉼표(,)를 기준으로 여러 방정식을 분리
        eq_strings = expr.split(',')
        eq_list = []
        
        for eq_str in eq_strings:
            eq_str = eq_str.strip()
            if '=' in eq_str:
                left, right = eq_str.split('=', 1)
                eq_list.append(sp.Eq(sp.sympify(left), sp.sympify(right)))
            else:
                eq_list.append(sp.Eq(sp.sympify(eq_str), 0))
                
        # 수식에 사용된 모든 변수(x, y 등)를 찾음
        symbols = set()
        for eq in eq_list:
            symbols.update(eq.free_symbols)
        symbols = list(symbols)
        
        if not symbols:
            st.session_state.calc_state = "변수(x, y 등) 없음"
            return
            
        # 연립방정식 풀이
        solutions = sp.solve(eq_list, symbols)
        
        # 해(Solution) 결과를 텍스트로 예쁘게 변환
        if not solutions:
            formatted_result = "해가 없음"
        elif isinstance(solutions, dict):
            # 단일 해 {x: 1, y: 2} 형태
            sol_parts = [f"{var} = {val}" for var, val in solutions.items()]
            formatted_result = ", ".join(sol_parts)
        elif isinstance(solutions, list):
            # 2차 방정식 등 해가 여러 개일 때
            if all(isinstance(s, dict) for s in solutions):
                sol_strs = ["(" + ", ".join([f"{k}={v}" for k, v in s.items()]) + ")" for s in solutions]
                formatted_result = " 또는 ".join(sol_strs)
            elif all(isinstance(s, tuple) for s in solutions):
                sol_strs = ["(" + ", ".join([f"{symbols[i]}={s[i]}" for i in range(len(symbols))]) + ")" for s in solutions]
                formatted_result = " 또는 ".join(sol_strs)
            else:
                formatted_result = " 또는 ".join([str(s) for s in solutions])
        else:
            formatted_result = str(solutions)
            
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
        st.balloons() 
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

st.info(f"**화면:** {st.session_state.calc_state}" if st.session_state.calc_state else "**화면:** 0", icon="📟")

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
    # ★ 안내 문구 변경 ★
    st.text_input("방정식 입력 (연립은 쉼표로 구분. 예: x+y=10, x-y=2)", key="eq_input")
    st.button("🧮 방정식 풀기", use_container_width=True, on_click=solve_equation)

st.divider()

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
with st.expander("📖 스마트 계산기 사용 설명서 보기"):
    st.markdown("""
    **1. 💸 N빵 계산 (더치페이)**
    * 계산기 버튼으로 총액을 먼저 구하거나 화면에 입력된 상태에서, 인원수를 맞추고 **[N빵 계산]**을 누르면 1인당 얼마를 내야 하는지 정확히 나눠줍니다.
    
    **2. 🎲 랜덤 뽑기**
    * 최소/최대값을 설정하고 **[뽑기]**를 누르면 범위 안에서 랜덤한 숫자를 뱉어냅니다. 밥값 내기나 벌칙자를 정할 때 써보세요!
    
    **3. 🧮 방정식 풀기 (연립방정식 지원)**
    * **일반 방정식:** `x**2 - 5*x + 6 = 0` (파이썬 규칙상 곱셈은 반드시 `*` 기호를 써야 합니다.)
    * **연립 방정식:** 식과 식 사이를 쉼표(`,`)로 구분하세요. (예: `x + y = 10, x - y = 2`)
    
    **4. 🎁 숨겨진 이스터에그**
    * 화면에 특정 숫자를 입력하고 `=` 버튼을 누르면 화면에 특별한 이벤트가 발생합니다!
    """)
