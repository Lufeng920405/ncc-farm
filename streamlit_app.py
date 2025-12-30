# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 深度定制 UI 样式 (工业精装风格) ---
st.set_page_config(page_title="NCC Project Hub", layout="wide")

st.markdown("""
    <style>
    /* 全局背景与字体 */
    .main { background-color: #f4f7f6; }
    .stApp { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; }
    
    /* 项目卡片样式 */
    .project-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* 侧边栏与标题 */
    .stSidebar { background-color: #0f172a !important; }
    h1, h2, h3 { color: #38bdf8 !important; }
    
    /* 进度条定制 */
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #38bdf8, #818cf8); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 模拟数据库 (实际应用中可挂载外部数据库，现阶段使用内存缓存) ---
if 'projects' not in st.session_state:
    st.session_state.projects = [
        {"name": "1号仓库扩建", "leader": "John", "start": "2025-01-01", "end": "2025-03-01", "progress": 65, "budget": 50000, "actual": 32000, "status": "进行中"},
        {"name": "西侧围栏加固", "leader": "Mike", "start": "2025-02-01", "end": "2025-02-15", "progress": 90, "budget": 8000, "actual": 7800, "status": "收尾阶段"}
    ]

# --- 3. 页面导航 ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/0f172a/38bdf8?text=NCC+FARM", use_container_width=True)
    st.title("控制中心")
    page = st.radio("模块切换", ["🏗️ 工程管理中心", "🔧 年度维养计划", "📦 物资总库", "🔒 系统管理"])
    st.divider()
    st.info("当前登录: johnny920405")

# --- 4. 模块1：工程管理中心 ---
if page == "🏗️ 工程管理中心":
    col_t1, col_t2 = st.columns([0.8, 0.2])
    with col_t1:
        st.header("工程建设实时看板")
    with col_t2:
        if st.button("➕ 新建工程项目"):
            st.session_state.show_create = True
            
    # 新建项目表单 (弹窗效果模拟)
    if st.session_state.get('show_create'):
        with st.expander("🛠️ 创建新工程项目", expanded=True):
            p_name = st.text_input("工程名称")
            p_leader = st.text_input("项目负责人")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p_budget = st.number_input("项目预算 (USD)", min_value=0)
                p_start = st.date_input("预计启动日期")
            with p_col2:
                p_file = st.file_uploader("导入工程预算表 (Excel)", type=['xlsx', 'csv'])
                p_end = st.date_input("预计交付日期")
            if st.button("提交工程申请"):
                st.session_state.projects.append({"name": p_name, "leader": p_leader, "start": str(p_start), "end": str(p_end), "progress": 0, "budget": p_budget, "actual": 0, "status": "准备中"})
                st.session_state.show_create = False
                st.rerun()

    # 循环渲染项目卡片
    for p in st.session_state.projects:
        with st.container():
            st.markdown(f"""
            <div class="project-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 20px; font-weight: bold;">{p['name']}</span>
                    <span class="status-badge" style="background: #0369a1; color: white;">{p['status']}</span>
                </div>
                <p style="color: #94a3b8; font-size: 14px;">负责人: {p['leader']} | 周期: {p['start']} 至 {p['end']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            with c1:
                st.write(f"进度: {p['progress']}%")
                st.progress(p['progress']/100)
            with c2:
                st.metric("预算支出", f"${p['actual']:,}", f"{p['budget'] - p['actual']:,} 剩余")
            with c3:
                if st.button(f"详情/物料导入", key=p['name']):
                    st.write("跳转至项目详情页面...")

# --- 5. 模块2：年度维养计划 ---
elif page == "🔧 年度维养计划":
    st.header("年度周期性维护计划")
    st.markdown("---")
    # 这里加载你上传的 maintenance_plans.csv
    try:
        m_df = pd.read_csv("maintenance_plans.csv")
        st.dataframe(m_df, use_container_width=True)
    except:
        st.info("请在总库上传 maintenance_plans.csv 文件")

# --- 6. 模块3：物资总库 ---
elif page == "📦 物资总库":
    st.header("全场库存与物料管理")
    tab_inv, tab_inout = st.tabs(["库存清单", "手动调整/出入库"])
    with tab_inv:
        search = st.text_input("🔍 模糊搜索库存物料 (支持名称、SKU、位置)")
        # 演示数据
        st.table({"SKU": ["WOOD-001", "SCREW-22"], "名称": ["2x4x8 木材", "3寸自攻钉"], "库存": [120, 5000], "位置": ["A1货架", "B3箱"]})
    with tab_inout:
        st.subheader("人工修正库存")
        st.selectbox("选择物料", ["2x4x8 木材", "3寸自攻钉"])
        st.number_input("调整数量 (+/-)", value=0)
        st.button("确认修改")
