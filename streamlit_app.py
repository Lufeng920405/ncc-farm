# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# --- 1. 高级 UI 样式再升级 (引入彩色点缀与层次感) ---
st.set_page_config(page_title="NCC Project Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background: #fdfdfd; 
        color: #1e293b;
    }
    /* 侧边栏点缀色 */
    [data-testid="stSidebar"] { background-color: #f8fafc !important; border-right: 1px solid #e2e8f0; }
    
    /* 核心卡片：增加翡翠绿/琥珀金的呼吸感 */
    .stCard {
        background: white;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    
    /* 提醒标红 */
    .danger-text { color: #ef4444; font-weight: bold; border-left: 4px solid #ef4444; padding-left: 10px; }
    .success-text { color: #10b981; font-weight: bold; }
    
    /* 按钮美化 */
    div.stButton > button {
        border-radius: 12px;
        background-color: #6366f1;
        color: white;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #4f46e5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据持久化模拟 (初始化) ---
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"SKU": "WD-2x4", "名称": "2x4x8 木材", "规格": "2x4", "尺寸": "8ft", "价格": 15.5, "库存": 100},
        {"SKU": "SC-3IN", "名称": "3寸自攻钉", "规格": "3in", "尺寸": "Box", "价格": 22.0, "库存": 50}
    ])
if 'maintenance' not in st.session_state:
    # 模拟维养数据
    st.session_state.maintenance = pd.DataFrame([
        {"任务": "水泵压力检查", "周期": "每周", "季度": "Q1", "状态": "完成", "截止": "2024-12-25"},
        {"任务": "温室覆盖检查", "周期": "每季", "季度": "Q4", "状态": "未完成", "截止": "2024-12-20"},
        {"任务": "发电机试运行", "周期": "每周", "季度": "Q1", "状态": "进行中", "截止": "2025-01-05"}
    ])

# --- 3. 导航逻辑 ---
with st.sidebar:
    st.markdown("<h2 style='color:#6366f1;'>✨ NCC Admin</h2>", unsafe_allow_html=True)
    page = st.radio("系统导航", ["🏗️ 工程项目", "🔧 维养计划", "📦 智能库存"])

# --- 4. 模块：工程项目 (修复新建功能) ---
if page == "🏗️ 工程项目":
    st.title("🏗️ 工程项目管理")
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("➕ 新建工程"): st.session_state.create_mode = True
    
    if st.session_state.get('create_mode'):
        with st.expander("🛠️ 录入新工程信息", expanded=True):
            name = st.text_input("项目名称")
            lead = st.text_input("项目负责人")
            b_val = st.number_input("项目预算 (USD)")
            node_text = st.text_area("时间节点计划 (例如: 1-5号地基, 6-10号墙体)")
            if st.button("确认创建"):
                st.session_state.projects.append({"name": name, "leader": lead, "budget": b_val, "nodes": []})
                st.session_state.create_mode = False
                st.rerun()

    # 显示已有项目 (此处逻辑同上，略...)
    if not st.session_state.projects:
        st.info("目前没有进行中的工程。点击右上角新建。")

# --- 5. 模块：维养计划 (按你的逻辑重构) ---
elif page == "🔧 维养计划":
    st.title("🔧 年度维养体系")
    
    # A. 顶部：当前工作
    st.subheader("📍 当前时间节点任务 (周/季)")
    current_tasks = st.session_state.maintenance[st.session_state.maintenance['截止'] >= str(date.today())]
    st.dataframe(current_tasks, use_container_width=True)
    
    # B. 中部：预告与复盘
    col_pre, col_rev = st.columns(2)
    with col_rev:
        st.markdown("<p style='color:#64748b;'>⏪ 上季度完成情况</p>", unsafe_allow_html=True)
        # 标红未完成内容
        past_tasks = st.session_state.maintenance[st.session_state.maintenance['状态'] == "未完成"]
        for _, row in past_tasks.iterrows():
            st.markdown(f"<div class='danger-text'>未完成: {row['任务']} (截止: {row['截止']})</div>", unsafe_allow_html=True)
            
    with col_pre:
        st.markdown("<p style='color:#64748b;'>⏩ 下季度任务预告</p>", unsafe_allow_html=True)
        st.write("Q2: 灌溉系统全面启动排查...")

    # C. 底部：全表展示
    with st.expander("📅 全年计划明细总表"):
        st.table(st.session_state.maintenance)

# --- 6. 模块：智能库存 (三入口设计) ---
elif page == "📦 智能库存":
    st.title("📦 物资智慧中心")
    
    # 搜索入口
    search_key = st.text_input("🔍 搜索库存 (输入物品名、规格或SKU)")
    
    if search_key:
        results = st.session_state.inventory[st.session_state.inventory.apply(lambda r: search_key.lower() in str(r).lower(), axis=1)]
        if not results.empty:
            st.dataframe(results, use_container_width=True)
            selected_sku = st.selectbox("选中操作目标", results['SKU'].tolist())
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("➖ 确认出库"):
                    st.success("库存已减除，对账单已同步。")
            with c2:
                if st.button("➕ 确认入库"):
                    st.info("已按历史规格入库。")
            with c3:
                # 申请购买逻辑
                if st.button("🛒 申请购买"):
                    st.session_state.buy_mode = True
        else:
            st.warning("无匹配，可直接点击下方【申请购买】新建")

    # 申请购买功能 (自动生成 Excel)
    if st.session_state.get('buy_mode'):
        st.divider()
        st.subheader("📝 请购单生成")
        req_name = st.text_input("物品名称")
        req_sku = st.text_input("SKU / 链接")
        req_qty = st.number_input("申请数量", min_value=1)
        req_price = st.number_input("历史/预计单价", min_value=0.0)
        
        if st.button("生成 Excel 请购单"):
            # 生成临时文件供下载
            df_req = pd.DataFrame([{"名称": req_name, "SKU": req_sku, "数量": req_qty, "单价": req_price, "总价": req_qty*req_price}])
            st.write(f"### 预估总额: ${req_qty*req_price:,.2f}")
            st.download_button("📩 点击下载 Excel 请购表", data=df_req.to_csv().encode('utf-8-sig'), file_name="请购单.csv")
