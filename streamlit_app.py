# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# --- 1. 核心配置与 UI 样式 (底部导航与高级感) ---
st.set_page_config(page_title="NCC Project Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 全局背景与字体 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #fcfdfd;
        color: #1e293b;
    }
    
    /* 底部菜单栏样式 */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: white;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 10px 0;
        border-top: 1px solid #e2e8f0;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    
    /* 颜色标识 */
    .text-me { color: #3b82f6 !important; font-weight: bold; } /* 我负责的-蓝色 */
    .text-join { color: #10b981 !important; font-weight: bold; } /* 我参与的-绿色 */
    .danger-text { color: #ef4444; font-weight: bold; }
    
    /* 按钮美化 */
    div.stButton > button { border-radius: 12px; }
    
    /* 隐藏默认侧边栏导航，使用我们自定义的底部菜单 */
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 模拟数据库初始化 (确保数据在跳转时不丢失) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'users': ['admin', 'Johnny', 'Staff1'],
        'projects': [
            {"id": 1, "name": "1号仓库扩建", "desc": "扩建西侧存储区域", "leader": "admin", "members": ["Staff1"], "nodes": [{"time": "1-5号", "content": "地基", "done": True}, {"time": "6-10号", "content": "墙体", "done": False}], "status": "进行中", "created_at": "2024-12-20"},
        ],
        'inventory': pd.DataFrame([
            {"项目名": "2x4x8 木材", "规格": "2x4", "数量": 100, "SKU": "WD-01", "单价": 15.0},
            {"项目名": "3寸自攻钉", "规格": "3IN", "数量": 500, "SKU": "SC-01", "单价": 22.0}
        ]),
        'inv_history': [], # 存储购买历史
        'maintenance': [
            {"任务": "水泵检查", "周期": "每周", "季度": "Q4", "时间": "2024-12-28", "完成": False},
            {"任务": "温室维护", "周期": "每季", "季度": "Q4", "时间": "2024-12-20", "完成": False}
        ],
        'contacts': {
            "工程外联": [{"名": "张经理", "电": "13800138000"}],
            "租赁外联": [{"名": "李老板", "电": "13900139000"}],
            "医院": [{"名": "农场诊所", "电": "911"}],
            "火警": [{"名": "火警", "电": "119"}]
        }
    }

if 'current_page' not in st.session_state: st.session_state.current_page = "login"
if 'user' not in st.session_state: st.session_state.user = None

# --- 3. 辅助功能：一键回到主页 ---
def go_home(): st.session_state.current_page = "home"

# --- 4. 页面逻辑控制 ---

# A. 登录注册页面
if st.session_state.current_page == "login":
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.title("✨ NCC Project Pro")
        user = st.text_input("用户名")
        pwd = st.text_input("密码", type="password")
        st.checkbox("记住登录", value=True)
        if st.button("登录", use_container_width=True):
            st.session_state.user = user
            st.session_state.current_page = "home"
            st.rerun()

# B. 首页：工程项目列表
elif st.session_state.current_page == "home":
    st.title("🏗️ 工程项目")
    col_l, col_r = st.columns([0.8, 0.2])
    with col_l:
        if st.button("➕ 新增项目"): st.session_state.current_page = "add_project"
    with col_r:
        if st.button("👤 我的项目"): st.session_state.current_page = "my_projects"

    # 项目排序展示 (按创建时间先后)
    for p in sorted(st.session_state.db['projects'], key=lambda x: x['created_at']):
        with st.container():
            # 计算进度
            done_nodes = sum(1 for n in p['nodes'] if n['done'])
            progress = int((done_nodes / len(p['nodes'])) * 100) if p['nodes'] else 0
            
            # 点击项目名进入详情
            if st.button(f"{p['name']} | 负责人: {p['leader']} | 预计完工: {p['nodes'][-1]['time'] if p['nodes'] else '未定'}", key=f"p_{p['id']}"):
                st.session_state.selected_project = p
                st.session_state.current_page = "project_detail"
                st.rerun()
            st.progress(progress)
            st.divider()

# C. 新增项目页面
elif st.session_state.current_page == "add_project":
    if st.button("⬅️ 返回"): go_home()
    st.header("新增工程项目")
    p_name = st.text_input("1. 工程项目名")
    p_desc = st.text_area("2. 工程描述")
    p_lead = st.text_input("3. 工程负责人", value=st.session_state.user)
    p_members = st.multiselect("4. 参与人员 (@关联用户)", st.session_state.db['users'])
    
    st.write("5. 时间节点计划")
    if 'temp_nodes' not in st.session_state: st.session_state.temp_nodes = [{"time": "", "content": "", "done": False}]
    
    for i, node in enumerate(st.session_state.temp_nodes):
        c1, c2 = st.columns(2)
        node['time'] = c1.text_input(f"时间区间 {i+1}", value=node['time'], key=f"time_{i}")
        node['content'] = c2.text_input(f"完成内容 {i+1}", value=node['content'], key=f"cont_{i}")
    
    if st.button("➕ 添加新节点行"):
        st.session_state.temp_nodes.append({"time": "", "content": "", "done": False})
        st.rerun()
        
    if st.button("提交创建", use_container_width=True):
        new_p = {
            "id": len(st.session_state.db['projects']) + 1,
            "name": p_name, "desc": p_desc, "leader": p_lead, 
            "members": p_members, "nodes": st.session_state.temp_nodes,
            "status": "进行中", "created_at": str(date.today())
        }
        st.session_state.db['projects'].append(new_p)
        del st.session_state.temp_nodes
        go_home()
        st.rerun()

# D. 农场维护页面
elif st.session_state.current_page == "maintenance":
    st.header("🌲 农场维护")
    # 管理员编辑
    if st.session_state.user == 'admin':
        c1, c2 = st.columns(2)
        with c1: st.button("➕ 添加计划")
        with c2: st.button("📝 编辑计划")

    # 1. 顶部当前工作
    st.subheader("📍 当前任务")
    m_df = pd.DataFrame(st.session_state.db['maintenance'])
    st.table(m_df[['季度', '任务', '时间', '完成']])

    # 2. 中间预告与标红
    st.subheader("⏪ 复盘与预告")
    for m in st.session_state.db['maintenance']:
        if not m['完成'] and m['时间'] < str(date.today()):
            st.markdown(f"<div class='danger-text'>未完成: {m['任务']} (截止: {m['时间']})</div>", unsafe_allow_html=True)

    # 3. 底部全年计划
    with st.expander("📅 全年计划展开列表"):
        st.dataframe(st.session_state.db['maintenance'], use_container_width=True)

# E. 库存管理主页
elif st.session_state.current_page == "inventory":
    st.header("📦 库存管理")
    c1, c2 = st.columns([0.3, 0.7])
    with c1:
        if st.button("🛒 申请购买"): st.session_state.current_page = "buy_request"
    with c2:
        search = st.text_input("🔍 模糊搜索材料...", placeholder="输入名称或SKU")

    # 搜索结果显示
    df = st.session_state.db['inventory']
    if search:
        df = df[df['项目名'].str.contains(search, case=False)]

    # 列表展示：项目名 | 数量 | 出库按钮 | 入库按钮 | 申请购买
    for i, row in df.iterrows():
        cols = st.columns([3, 1, 1, 1, 1])
        if cols[0].button(row['项目名'], key=f"inv_name_{i}"):
            st.session_state.selected_item = row
            st.session_state.current_page = "inv_detail"
            st.rerun()
        cols[1].write(row['数量'])
        if cols[2].button("出", key=f"out_{i}"):
            st.session_state.selected_item = row
            st.session_state.current_page = "inv_out"
            st.rerun()
        if cols[3].button("入", key=f"in_{i}"):
            st.session_state.selected_item = row
            st.session_state.current_page = "inv_in"
            st.rerun()
        if cols[4].button("购", key=f"buy_{i}"):
            st.session_state.selected_item = row
            st.session_state.current_page = "buy_request"
            st.rerun()
    
    if st.button("📊 查看库存总表"):
        st.session_state.current_page = "inv_all"
        st.rerun()

# F. 申请购买页面 (核心逻辑)
elif st.session_state.current_page == "buy_request":
    if st.button("⬅️ 返回"): st.session_state.current_page = "inventory"
    st.subheader("📝 填写请购单")
    
    if 'buy_rows' not in st.session_state: st.session_state.buy_rows = [{"name":"", "spec":"", "qty":1, "sku":"", "link":"", "price":0.0, "user":""}] * 3
    
    # 填写列表
    total_cost = 0.0
    for i, r in enumerate(st.session_state.buy_rows):
        st.write(f"项目 {i+1}")
        c1, c2, c3, c4 = st.columns(4)
        r['name'] = c1.text_input("名称", key=f"bn_{i}")
        r['spec'] = c2.text_input("规格", key=f"bs_{i}")
        r['qty'] = c3.number_input("数量", min_value=1, key=f"bq_{i}")
        # 自动获取历史价格逻辑
        hist = st.session_state.db['inventory'][st.session_state.db['inventory']['项目名'] == r['name']]
        r['price'] = hist['单价'].values[0] if not hist.empty else 0.0
        c4.write(f"参考价: {r['price']}")
        total_cost += r['qty'] * r['price']
    
    if st.button("➕ 新增一行"):
        st.session_state.buy_rows.append({"name":"", "spec":"", "qty":1, "sku":"", "link":"", "price":0.0, "user":""})
        st.rerun()
        
    st.write(f"### 💰 采购总预估: ${total_cost:,.2f}")
    if st.button("提交并下载 Excel"):
        # 生成 Excel (CSV模拟)
        final_df = pd.DataFrame(st.session_state.buy_rows)
        st.download_button("点击下载请购表", data=final_df.to_csv().encode('utf-8-sig'), file_name="请购单.csv")

# --- 5. 底部固定导航栏 ---
if st.session_state.current_page != "login":
    st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True) # 占位
    
    # 创建底部按钮列
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("📞"): st.session_state.current_page = "contacts"
    with b2:
        if st.button("🌲"): st.session_state.current_page = "maintenance"
    with b3:
        if st.button("✨N"): st.session_state.current_page = "home"
    with b4:
        if st.button("📦"): st.session_state.current_page = "inventory"
    with b5:
        if st.button("👤"): st.session_state.current_page = "profile"
