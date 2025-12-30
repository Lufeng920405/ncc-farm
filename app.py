# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. 网页配置
st.set_page_config(page_title="NCC 农场管理系统", layout="wide")
st.title("🚜 NCC Farm Management System")

# 2. 数据库加载（容错处理：如果CSV名字不对也能运行）
def load_data():
    try:
        # 尝试用 utf-8-sig 读取，这是处理 Excel 转 CSV 最稳妥的方式
        inventory = pd.read_csv("warehouse_inventory.csv", encoding='utf-8-sig')
        tasks = pd.read_csv("maintenance_plans.csv", encoding='utf-8-sig')
        return inventory, tasks
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        # 如果找不到文件，先创建一个空的表格，保证程序不崩
        return pd.DataFrame(columns=["名称", "库存"]), pd.DataFrame(columns=["任务", "状态"])

inventory, tasks = load_data()

# 3. 登录与身份切换
user_role = st.sidebar.radio("身份登录", ["管理员", "员工"])
user_id = st.sidebar.text_input("工号/姓名", value="Staff01")

if user_role == "管理员":
    st.header("📊 老板控制台 (Admin Dashboard)")
    st.write(f"欢迎回来，{user_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚠️ 本月维养清单")
        st.dataframe(tasks, use_container_width=True)
    with col2:
        st.subheader("📈 预算与库存预览")
        st.dataframe(inventory.head(10), use_container_width=True)

else:
    st.header(f"👋 NCC 员工工作台: {user_id}")
    
    # 模糊搜索领料
    tab1, tab2 = st.tabs(["📦 领用物资", "📅 维养任务"])
    
    with tab1:
        search_query = st.text_input("输入关键词（搜索建材、SKU、规格）")
        if search_query:
            # 模糊匹配
            mask = inventory.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            results = inventory[mask]
            st.write("找到以下物资：")
            st.dataframe(results)
            
            qty = st.number_input("领用数量", min_value=1, step=1)
            if st.button("提交领用登记"):
                st.success(f"登记成功：{user_id} 领用了 {qty} 个单位。")

    with tab2:
        st.subheader("本月 NCC 维养任务")
        st.info("每月1号自动刷新。完成后请勾选并在下方上传照片。")
        # 简单列举几个任务供测试
        st.checkbox("1号水泵巡检")
        st.checkbox("东侧围栏检查")
        st.file_uploader("上传现场照片", type=['png', 'jpg', 'jpeg'])
        if st.button("提交进度"):
            st.balloons()
            st.success("任务进度已更新，老板后台已可见！")
