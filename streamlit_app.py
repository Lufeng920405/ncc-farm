# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. 高级 UI 样式定制 (极简、轻量、解决黑色框问题) ---
st.set_page_config(page_title="NCC Management", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 1. 字体与整体氛围 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Noto Sans SC', sans-serif;
        background-color: #FFFFFF !important;
        color: #2D3436 !important;
    }

    /* 2. 彻底修复并美化填写框 */
    /* 移除背景，只保留底部黑线或极简细框 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: transparent !important;
        color: #2D3436 !important;
        border: none !important;
        border-bottom: 1px solid #E2E8F0 !important; /* 初始灰线 */
        border-radius: 0px !important;
        padding: 10px 0px !important;
        font-size: 16px !important;
    }
    .stTextInput>div>div>input:focus {
        border-bottom: 2px solid #000000 !important; /* 聚焦时变黑线 */
        transition: 0.3s;
    }
    /* 调整提示文字颜色 */
    ::placeholder { color: #A0AEC0 !important; opacity: 1; }

    /* 3. 底部导航栏排版 */
    .nav-container {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        border-top: 1px solid #F1F5F9;
        z-index: 9999;
    }

    /* 4. 项目卡片精修 */
    .project-item {
        background: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* 5. 颜色规范 */
    .text-blue { color: #0984E3 !important; }
    .text-green { color: #00B894 !important; }
    .text-red { color: #D63031 !important; }

    /* 隐藏默认冗余 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心数据引擎 (保持功能完整) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'users': ['admin', 'Johnny', 'Staff1'],
        'projects': [
            {"id": 1, "name": "1号仓库改建", "desc": "基础扩容", "leader": "admin", "members": ["Staff1"], 
             "nodes": [{"time": "1-5号", "content": "地基", "done": True}, {"time": "6-10号", "content": "墙体", "done": False}], 
             "status": "进行中", "created_at": "2024-12-20"}
        ],
        'inventory': pd.DataFrame([{"项目名": "2x4x8 木材", "规格": "2x4", "数量": 100, "SKU": "WD-01", "单价": 15.0}]),
        'maintenance': [{"任务": "水泵检查", "周期": "每周", "时间": "2024-12-15", "完成": False}],
        'contacts': {"工程外联": [{"名": "王工", "电": "13800000000"}]}
    }

if 'page' not in st.session_state: st.session_state.page = "home"

# --- 3. 逻辑处理函数 ---
def navigate_to(p): st.session_state.page = p

# --- 4. 页面内容渲染 ---

# 【首页：工程项目】
if st.session_state.page == "home":
    st.markdown("<h2 style='text-align:center;'>工程项目</h2>", unsafe_allow_html=True)
    c1, _ = st.columns([1, 4])
    if c1.button("➕ 新增项目"): navigate_to("add_p")
    
    for p in st.session_state.db['projects']:
        done = sum(1 for n in p['nodes'] if n['done'])
        prog = int((done/len(
