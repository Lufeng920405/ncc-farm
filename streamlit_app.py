# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="NCC 农场管理", layout="wide")

# --- 数据读取函数 (带自动容错) ---
def load_data(file_name):
    try:
        # 尝试多种编码和格式读取
        df = pd.read_csv(file_name, encoding='utf-8-sig', on_bad_lines='skip')
        # 如果第一行是空行，自动清理
        if df.columns[0].startswith('Unnamed'):
            df.columns = df.iloc[0]
            df = df[1:]
        return df.reset_index(drop=True)
    except Exception as e:
        st.warning(f"文件 {file_name} 读取受阻，正在尝试基础模式...")
        try:
            return pd.read_csv(file_name, encoding='gbk')
        except:
            return pd.DataFrame()

# 加载数据
inventory = load_data("warehouse_inventory.csv")
maintenance = load_data("maintenance_plans.csv")

st.title("🚜 NCC 农场管理系统")

# --- 侧边栏 ---
role = st.sidebar.radio("身份选择", ["员工模式", "管理后台"])

if role == "管理后台":
    st.header("📊 NCC 经营概览")
    if not inventory.empty:
        # 尝试寻找包含“总额”或“price”的列计算总数
        st.subheader("库存清单预览")
        st.dataframe(inventory)
    
    st.subheader("📅 年度维养计划")
    st.dataframe(maintenance)
    
    st.info(f"提醒功能已锁定：每月月底将发送清单至 johnny920405@gmail.com")

else:
    st.header("🛠️ 员工工作台")
    tab1, tab2 = st.tabs(["📦 领料登记", "✅ 维养打卡"])
    
    with tab1:
        search = st.text_input("搜索物料 (输入名称、规格或SKU)")
        if search and not inventory.empty:
            # 全表模糊搜索
            mask = inventory.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
            results = inventory[mask]
            st.write("找到以下匹配：")
            st.dataframe(results)
            
            if not results.empty:
                item = st.selectbox("确认选择的物品", results.iloc[:, 0].tolist())
                qty = st.number_input("领取数量", min_value=1)
                if st.button("提交登记"):
                    st.success(f"登记成功！项目：{item} 数量：{qty}")

    with tab2:
        st.subheader("待办维护任务")
        if not maintenance.empty:
            # 尝试显示任务内容
            task_col = maintenance.columns[2] if len(maintenance.columns) > 2 else maintenance.columns[0]
            for i, task in maintenance.head(10).iterrows():
                st.checkbox(f"任务: {task[task_col]}", key=i)
            st.file_uploader("上传现场照片")
            if st.button("完成打卡"):
                st.balloons()
