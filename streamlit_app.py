# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. 高级 UI 样式注入 ---
st.set_page_config(page_title="NCC Project Pro", layout="wide")

st.markdown("""
    <style>
    /* 引入现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background: #f8fafc; /* 柔和的浅色底 */
        color: #1e293b;
    }

    /* 登录卡片美化 */
    .auth-card {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        max-width: 450px;
        margin: auto;
    }

    /* 项目卡片：毛玻璃与悬浮感 */
    .stCard {
        background: white;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .stCard:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.1);
    }

    /* 进度条美化 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        border-radius: 10px;
    }
    
    /* 节点时间线样式 */
    .milestone-box {
        border-left: 2px solid #e2e8f0;
        padding-left: 20px;
        margin-left: 10px;
        position: relative;
    }
    .milestone-active { border-left: 2px solid #6366f1; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 模拟用户与项目数据库 ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'projects' not in st.session_state:
    # 预设一个带时间节点的演示项目
    st.session_state.projects = [{
        "id": 1,
        "name": "西侧仓库扩建",
        "leader": "Johnny",
        "budget": 50000,
        "nodes": [
            {"title": "完成地基", "start": date(2025,1,1), "end": date(2025,1,5), "done": True},
            {"title": "完成墙体", "start": date(2025,1,6), "end": date(2025,1,10), "done": True},
            {"title": "完成屋顶", "start": date(2025,1,11), "end": date(2025,1,15), "done": False},
        ]
    }]

# --- 3. 登录与注册模块 ---
def auth_page():
    st.markdown('<div style="height:100px"></div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.title("✨ NCC Project Pro")
        st.subheader("欢迎回来，请登录您的账号")
        user = st.text_input("用户名", placeholder="admin")
        pwd = st.text_input("密码", type="password")
        if st.button("进入系统", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        st.markdown('<p style="text-align:center; color:#64748b; font-size:14px">没有账号？请联系系统管理员注册</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 主程序入口 ---
if not st.session_state.logged_in:
    auth_page()
else:
    # 侧边栏导航
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        page = st.radio("前往", ["🏗️ 工程项目中心", "🔧 年度维养", "📦 全场总库存", "🚪 退出登录"])
        if page == "🚪 退出登录":
            st.session_state.logged_in = False
            st.rerun()

    # --- 工程管理页面 ---
    if page == "🏗️ 工程项目中心":
        st.title("工程管理中心")
        
        # 顶部操作
        c1, c2 = st.columns([0.8, 0.2])
        with c1: st.write("管理您当前负责的所有建设工程与时间节点")
        with c2: 
            if st.button("✨ 创建新工程", use_container_width=True):
                st.toast("加载工程模版...")

        # 循环显示项目卡片
        for p in st.session_state.projects:
            with st.container():
                st.markdown(f'### {p["name"]}')
                col_info, col_chart = st.columns([0.4, 0.6])
                
                with col_info:
                    st.write(f"负责人: **{p['leader']}**")
                    st.metric("项目预算", f"${p['budget']:,}")
                    
                with col_chart:
                    # 计算总进度
                    done_count = sum(1 for n in p['nodes'] if n['done'])
                    progress = int((done_count / len(p['nodes'])) * 100)
                    st.write(f"当前整体完成度: {progress}%")
                    st.progress(progress)

                # 展开显示时间节点对比
                with st.expander("🔍 查看详细里程碑与时间偏差", expanded=True):
                    st.write("项目节点计划对比 (负责人设定 vs 实际进度)")
                    today = date.today()
                    
                    for n in p['nodes']:
                        # 判断是否逾期
                        is_late = today > n['end'] and not n['done']
                        status_color = "🔴 逾期" if is_late else ("🟢 已完成" if n['done'] else "🟡 进行中")
                        
                        col_n1, col_n2, col_n3 = st.columns([0.4, 0.4, 0.2])
                        with col_n1:
                            st.write(f"**{n['title']}**")
                            st.caption(f"计划: {n['start']} 至 {n['end']}")
                        with col_n2:
                            if is_late:
                                st.error(f"警告：该节点已落后计划 { (today - n['end']).days } 天")
                            else:
                                st.write(f"当前状态: {status_color}")
                        with col_n3:
                            if st.checkbox("标记完成", value=n['done'], key=f"{p['id']}_{n['title']}"):
                                n['done'] = True
