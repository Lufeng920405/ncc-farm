# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. 高级极简 UI 样式 ---
st.set_page_config(page_title="NCC Management", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Noto Sans SC', sans-serif;
        background-color: #FFFFFF !important;
        color: #2D3436 !important;
    }

    /* 输入框：极简黑线描边 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: white !important;
        color: #2D3436 !important;
        border: none !important;
        border-bottom: 1px solid #E2E8F0 !important;
        border-radius: 0px !important;
        padding: 10px 0px !important;
    }
    .stTextInput>div>div>input:focus {
        border-bottom: 2px solid #000000 !important;
    }
    ::placeholder { color: #A0AEC0 !important; }

    /* 底部导航 */
    .nav-spacer { height: 80px; }
    
    /* 进度条颜色 */
    .stProgress > div > div > div > div { background-color: #00B894 !important; }

    /* 状态颜色 */
    .text-me { color: #0984E3 !important; font-weight: bold; }
    .text-join { color: #00B894 !important; font-weight: bold; }
    .danger-text { color: #D63031 !important; font-weight: bold; border-left: 3px solid #D63031; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库引擎 ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'projects': [
            {"id": 1, "name": "1号仓库改建", "desc": "扩建", "leader": "admin", "members": ["Johnny"], 
             "nodes": [{"time": "1-5号", "content": "地基", "done": True}, {"time": "6-10号", "content": "墙体", "done": False}], 
             "status": "进行中", "created_at": "2024-12-01"}
        ],
        'inventory': pd.DataFrame([{"项目名": "2x4x8 木材", "规格": "2x4", "数量": 100, "SKU": "WD-01", "单价": 15.0}]),
        'maintenance': [{"季度": "Q4", "任务": "水泵维护", "时间": "2024-12-20", "完成": False}],
        'contacts': {"工程外联": [{"名": "王工", "电": "13800000000"}], "医院": [{"名": "紧急救护", "电": "911"}]}
    }

if 'page' not in st.session_state: st.session_state.page = "home"
if 'user' not in st.session_state: st.session_state.user = "admin"

def nav(p): st.session_state.page = p

# --- 3. 页面渲染逻辑 ---

# 【首页：工程项目列表】
if st.session_state.page == "home":
    st.markdown("<h2 style='text-align:center;'>工程项目</h2>", unsafe_allow_html=True)
    c1, _ = st.columns([1, 4])
    if c1.button("➕ 新增项目"): nav("add_p")
    
    for p in sorted(st.session_state.db['projects'], key=lambda x: x['created_at']):
        with st.container():
            done = sum(1 for n in p['nodes'] if n['done'])
            total = len(p['nodes']) if p['nodes'] else 1
            prog = int((done / total) * 100)
            
            st.markdown(f"**{p['name']}** | 负责人: {p['leader']} | 完工: {p['nodes'][-1]['time'] if p['nodes'] else '--'}")
