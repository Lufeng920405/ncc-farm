# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# --- 1. 终极 UI 样式修正 (解决黑色背景/文字看不见的问题) ---
st.set_page_config(page_title="NCC Project Pro", layout="wide")

st.markdown("""
    <style>
    /* 强制背景与全局文字颜色 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }
    
    /* 修复输入框文字为黑色导致的看不见问题 */
    input, textarea, [data-baseweb="input"] {
        color: #1e293b !important;
        background-color: white !important;
    }
    
    /* 登录卡片样式 */
    .auth-card {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }

    /* 按钮样式：紫色高级感 */
    div.stButton > button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 12px;
        font-weight: 600;
        border: none;
        padding: 10px 24px;
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 提示文本 */
    .danger-tag { color: #ef4444; border-left: 4px solid #ef4444; padding-left: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心状态管理 (登录、工程、库存) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'projects' not in st.session_state: st.session_state.projects = []
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"SKU": "WD-2x4", "名称": "2x4x8 木材", "规格": "2x4", "尺寸": "8ft", "价格": 15.5, "库存": 100},
        {"SKU": "SC-3IN", "名称": "3寸自攻钉", "规格": "3in", "尺寸": "Box", "价格": 22.0, "库存": 50}
    ])

# --- 3. 登录逻辑 (找回登录按钮) ---
def login_screen():
    st.markdown('<div style="height:100px"></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#6366f1;'>✨ NCC Project Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b;'>专业农场工程协作平台</p>", unsafe_allow_html=True)
        user = st.text_input("用户名", value="admin")
        pwd = st.text_input("密码", type="password", value="admin")
        if st.button("进入系统", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 主程序判断 ---
if not st.session_state.logged_in:
    login_screen()
else:
    # 侧边栏导航与退出
    with st.sidebar:
        st.markdown("<h3 style='color:#6366f1;'>NCC 控制台</h3>", unsafe_allow_html=True)
        page = st.radio("功能模块", ["🏗️ 工程管理", "🔧 维养计划", "📦 智能库存"])
        st.divider()
        if st.button("🚪 退出登录"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 工程管理模块 ---
    if page == "🏗️ 工程管理":
        st.title("🏗️ 工程项目中心")
        c1, c2 = st.columns([0.8, 0.2])
        with c2:
            if st.button("✨ 创建新工程"): st.session_state.show_form = True
            
        if st.session_state.get('show_form'):
            with st.form("new_project"):
                st.subheader("🛠️ 录入新项目基本信息")
                p_name = st.text_input("项目名称 (如: 仓库改建)")
                p_lead = st.text_input("项目负责人")
                p_budget = st.number_input("初始预算 (USD)", min_value=0)
                # 里程碑设定
                st.markdown("📅 **设定关键时间节点**")
                n_text = st.text_area("节点计划", placeholder="例如:\n1-5号: 地基工程\n6-10号: 墙体建设")
                
                submitted = st.form_submit_button("发布工程")
                if submitted:
                    st.session_state.projects.append({
                        "name": p_name, "leader": p_lead, "budget": p_budget, 
                        "nodes": n_text, "created_at": str(date.today())
                    })
                    st.session_state.show_form = False
                    st.success(f"项目 {p_name} 已成功创建！")
                    st.rerun()

        # 展示项目卡片
        if not st.session_state.projects:
            st.info("暂无工程项目，请点击上方按钮新建。")
        else:
            for p in st.session_state.projects:
                with st.container():
                    st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:15px; border:1px solid #e2e8f0; margin-bottom:15px;">
                        <h3 style="color:#1e293b; margin:0;">{p['name']}</h3>
                        <p style="color:#64748b; font-size:14px;">负责人: {p['leader']} | 预算: ${p['budget']:,}</p>
                        <hr style="border:0.5px solid #f1f5f9;">
                        <p style="white-space: pre-wrap;">{p['nodes']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # --- 维养计划模块 ---
    elif page == "🔧 维养计划":
        st.title("🔧 维养体系看板")
        # 模拟维养数据
        m_data = [
            {"任务": "水泵维护", "截止": "2024-12-20", "状态": "未完成", "周期": "每周"},
            {"任务": "发电机测试", "截止": "2024-12-30", "状态": "完成", "周期": "每月"}
        ]
        
        # 中间标红逻辑
        st.subheader("🚩 异常/逾期监控")
        for m in m_data:
            if m['状态'] == "未完成":
                st.markdown(f"<div class='danger-tag'>🚨 逾期提醒: {m['任务']} 应于 {m['截止']} 完成</div>", unsafe_allow_html=True)
        
        st.subheader("📅 全年计划明细")
        st.table(m_data)

    # --- 库存模块 ---
    elif page == "📦 智能库存":
        st.title("📦 智能物料仓库")
        search = st.text_input("🔍 搜索物料...")
        if search:
            # 简化展示搜索结果
            st.dataframe(st.session_state.inventory)
