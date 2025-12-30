# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# --- 1. UI 视觉深度重塑 (极简高级感 + 修复黑色框) ---
st.set_page_config(page_title="NCC Project Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    /* 填写框：背景透明，底部单黑线，提示文字清晰 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: none !important;
        border-bottom: 1.5px solid #E2E8F0 !important;
        border-radius: 0px !important;
        padding: 12px 0px !important;
        font-size: 16px !important;
    }
    .stTextInput>div>div>input:focus { border-bottom: 2px solid #6366F1 !important; transition: 0.3s; }
    ::placeholder { color: #94A3B8 !important; opacity: 1; }

    /* 底部导航栏固定 */
    .nav-bar {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background: white;
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        border-top: 1px solid #F1F5F9;
        z-index: 9999;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div > div { background-color: #6366F1 !important; }
    
    /* 颜色规范 */
    .blue-item { color: #2563EB !important; font-weight: 600; } /* 我负责的 */
    .green-item { color: #059669 !important; font-weight: 600; } /* 我参与的 */
    .red-alert { color: #DC2626 !important; font-weight: bold; border-left: 4px solid #DC2626; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库逻辑 (保持数据持久性) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'users': ['admin', 'Johnny', 'Staff1'],
        'projects': [],
        'inventory': pd.DataFrame([
            {"项目名": "2x4x8 木材", "规格": "2x4", "数量": 100, "SKU": "WD-01", "单价": 15.0},
            {"项目名": "3寸自攻钉", "规格": "3IN", "数量": 500, "SKU": "SC-01", "单价": 22.0}
        ]),
        'maint_plan': [
            {"季度": "Q4", "周期": "当前周", "任务": "水泵压力检查", "截止": "2024-12-25", "完成": False},
            {"季度": "Q4", "周期": "当前季", "任务": "温室结构加固", "截止": "2024-12-20", "完成": False}
        ],
        'contacts': {"工程外联": [], "租赁外联": [], "医院": [{"名": "诊所", "电": "911"}], "火警": [{"名": "火警", "电": "119"}]}
    }

if 'page' not in st.session_state: st.session_state.page = "login"
if 'user' not in st.session_state: st.session_state.user = None

def nav(p): st.session_state.page = p

# --- 3. 页面渲染 ---

# 【1. 登录注册】
if st.session_state.page == "login":
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.title("✨ NCC Login")
        u = st.text_input("用户名", placeholder="请输入用户名")
        p = st.text_input("密码", type="password", placeholder="请输入密码")
        st.checkbox("记住登录", value=True)
        if st.button("进入网站", use_container_width=True):
            st.session_state.user = u
            nav("home")
            st.rerun()

# 【2. 首页：项目列表】
elif st.session_state.page == "home":
    st.markdown("<h2 style='text-align:center;'>工程项目</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.2, 0.8])
    with c1: 
        if st.button("➕新增项目"): nav("add_p")
    with c2:
        if st.button("📁我的项目"): nav("my_p")
    
    # 列表展示
    for p in sorted(st.session_state.db['projects'], key=lambda x: x.get('created_at', "")):
        with st.container():
            done = sum(1 for n in p['nodes'] if n['done'])
            prog = int((done / len(p['nodes'])) * 100) if p['nodes'] else 0
            if st.button(f"{p['name']} | 负责人: {p['leader']} | 完工: {p['nodes'][-1]['time'] if p['nodes'] else '--'}", key=f"h_{p['id']}"):
                st.session_state.sel_p = p
                nav("det_p")
            st.progress(prog)
            st.divider()

# 【3. 新增项目页】
elif st.session_state.page == "add_p":
    if st.button("⬅️ 返回主页"): nav("home")
    st.header("新增项目")
    p_n = st.text_input("项目名称", placeholder="第一行：工程项目名")
    p_d = st.text_area("描述", placeholder="第二行：工程描述")
    p_l = st.text_input("负责人", placeholder="第三行：工程负责人")
    p_m = st.text_input("参与人员", placeholder="第四行：@用户名，关联其它员工")
    
    st.write("第五行：时间节点")
    if 'nodes_tmp' not in st.session_state: st.session_state.nodes_tmp = [{"time":"","cont":"","done":False}]
    for i, n in enumerate(st.session_state.nodes_tmp):
        c_t, c_c = st.columns(2)
        n['time'] = c_t.text_input(f"区间 {i+1}", placeholder="时间区间", key=f"at_{i}")
        n['cont'] = c_c.text_input(f"内容 {i+1}", placeholder="完成内容", key=f"ac_{i}")
    if st.button("➕ 新增行"):
        st.session_state.nodes_tmp.append({"time":"","cont":"","done":False})
        st.rerun()
    if st.button("发布项目", use_container_width=True):
        st.session_state.db['projects'].append({
            "id": len(st.session_state.db['projects'])+1, "name": p_n, "desc": p_d, 
            "leader": p_l, "members": p_m, "nodes": st.session_state.nodes_tmp, 
            "created_at": str(date.today()), "done_final": False
        })
        del st.session_state.nodes_tmp
        nav("home")
        st.rerun()

# 【4. 农场维护】🌲
elif st.session_state.page == "maint":
    st.header("🌲 农场维护")
    st.subheader("📍 当前维护工作")
    m_df = pd.DataFrame(st.session_state.db['maint_plan'])
    st.table(m_df)
    
    st.subheader("⏪ 进度复盘")
    for m in st.session_state.db['maint_plan']:
        if not m['完成'] and m['截止'] < str(date.today()):
            st.markdown(f"<div class='red-alert'>未完成: {m['任务']} (应于{m['截止']}完成)</div>", unsafe_allow_html=True)
    
    with st.expander("📅 全年计划明细"):
        st.write("正在自动抓取全年计划...")

# 【5. 库存管理】📦
elif st.session_state.page == "inv":
    st.header("📦 库存管理")
    c1, c2 = st.columns([0.3, 0.7])
    with c1: 
        if st.button("🛒 申请购买"): nav("buy_req")
    with c2: 
        sk = st.text_input("", placeholder="🔍 模糊搜索材料...")
    
    inv_df = st.session_state.db['inventory']
    if sk: inv_df = inv_df[inv_df['项目名'].str.contains(sk, case=False)]
    
    for i, r in inv_df.iterrows():
        cols = st.columns([3, 1, 1, 1, 1])
        cols[0].write(f"**{r['项目名']}**")
        cols[1].write(f"量: {r['数量']}")
        if cols[2].button("出", key=f"o_{i}"): pass
        if cols[3].button("入", key=f"i_{i}"): pass
        if cols[4].button("购", key=f"b_{i}"): nav("buy_req")

# 【6. 我的 / 个人中心】👤
elif st.session_state.page == "profile":
    st.subheader("👤 我的中心")
    if st.button("🚪 退出登录"):
        st.session_state.user = None
        nav("login")
        st.rerun()

# --- 4. 底部菜单栏 (全页面通用) ---
if st.session_state.page != "login":
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
    nb1, nb2, nb3, nb4, nb5 = st.columns(5)
    with nb1: 
        if st.button("📞"): nav("contact")
    with nb2: 
        if st.button("🌲"): nav("maint")
    with nb3: 
        if st.button("✨N"): nav("home")
    with nb4: 
        if st.button("📦"): nav("inv")
    with nb5: 
        if st.button("👤"): nav("profile")
