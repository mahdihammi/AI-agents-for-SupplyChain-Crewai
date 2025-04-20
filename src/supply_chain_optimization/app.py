import streamlit as st
import snowflake.connector
import json
from supply_chain_optimization.main import SupplyChainFlow, SupplyChainState
from supply_chain_optimization.utils.snowflake_client import SnowflakeClient
import plotly.express as px
import pandas as pd

def run_inference():
    flow = SupplyChainFlow()
    flow.kickoff()
    return flow.state

def get_snowflake_data(query):
    sfc = SnowflakeClient()
    data = sfc.execute_query(query)
    return data


# Fetch the data if it's not already in session_state or refresh button is clicked
def fetch_dashboard_data():
    # 1. Top 10 Products by Stock
    stock_by_product_query = """
        SELECT p.PRODUCT_NAME, SUM(f.STOCK_QUANTITY) AS TOTAL_STOCK
        FROM SUPPLY_CHAIN.SUPPLY_DATA.INVENTORY_FACT f
        JOIN SUPPLY_CHAIN.SUPPLY_DATA.PRODUCT p
        ON f.PRODUCT_ID = p.PRODUCT_ID
        GROUP BY p.PRODUCT_NAME
        ORDER BY TOTAL_STOCK DESC
        LIMIT 10
    """
    stock_data = pd.DataFrame(get_snowflake_data(stock_by_product_query), columns=["PRODUCT_NAME", "TOTAL_STOCK"])

    # 2. Stock over Time
    stock_over_time_query = """
        SELECT EVENT_DATE, SUM(STOCK_QUANTITY) AS TOTAL_STOCK
        FROM SUPPLY_CHAIN.SUPPLY_DATA.INVENTORY_FACT
        GROUP BY EVENT_DATE
        ORDER BY EVENT_DATE
    """
    time_data = pd.DataFrame(get_snowflake_data(stock_over_time_query), columns=["EVENT_DATE", "TOTAL_STOCK"])

    # 3. Current Stock vs Reorder Threshold
    reorder_query = """
        SELECT p.PRODUCT_NAME, SUM(f.STOCK_QUANTITY) AS CURRENT_STOCK, p.REORDER_THRESHOLD
        FROM SUPPLY_CHAIN.SUPPLY_DATA.INVENTORY_FACT f
        JOIN SUPPLY_CHAIN.SUPPLY_DATA.PRODUCT p
        ON f.PRODUCT_ID = p.PRODUCT_ID
        GROUP BY p.PRODUCT_NAME, p.REORDER_THRESHOLD
    """
    reorder_data = pd.DataFrame(get_snowflake_data(reorder_query), columns=["PRODUCT_NAME", "CURRENT_STOCK", "REORDER_THRESHOLD"])

    # 4. Route Transport Mode Distribution
    transport_mode_query = """
        SELECT TRANSPORT_MODE, COUNT(*) AS ROUTE_COUNT
        FROM SUPPLY_CHAIN.SUPPLY_DATA.ROUTE
        GROUP BY TRANSPORT_MODE
    """
    transport_data = pd.DataFrame(get_snowflake_data(transport_mode_query), columns=["TRANSPORT_MODE", "ROUTE_COUNT"])

    # 5. Supplier Reliability
    supplier_query = """
        SELECT SUPPLIER_NAME, CAST(REPLACE(RELIABILITY_SCORE, '%', '') AS FLOAT) AS RELIABILITY
        FROM SUPPLY_CHAIN.SUPPLY_DATA.SUPPLIER
        WHERE RELIABILITY_SCORE IS NOT NULL
    """
    supplier_data = pd.DataFrame(get_snowflake_data(supplier_query), columns=["SUPPLIER_NAME", "RELIABILITY"])

    return stock_data, time_data, reorder_data, transport_data, supplier_data


if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
    st.session_state.time_data = None
    st.session_state.reorder_data = None
    st.session_state.transport_data = None
    st.session_state.supplier_data = None

def main():
    st.set_page_config(layout="wide", page_icon="🚚")
    st.sidebar.title("Navigation ➡️")
    page = st.sidebar.selectbox("Go to", ["Inference", "Queries", "Dashboard"])
    
    if page == "Inference":
        st.title("Supply Chain Optimization 🚚")
        
        if st.button("Run Inference", use_container_width=True):
            state = run_inference()
            
            st.subheader("Products")
            st.json(state.products)
            
            st.subheader("Supplier")
            st.json(state.supplier)
            
            st.subheader("Route")
            st.json(state.route)
            
            st.subheader("Email")
            st.text(state.email)
            
            st.subheader("Report")
            st.text(state.report)
    
    elif page == "Queries":
        st.title("Supply Chain Queries Execution 📊")
        query = st.text_area("Enter SQL Query for Snowflake:", "SELECT * FROM ... LIMIT 10")
        
        if st.button("Fetch Data", use_container_width=True):
            data = get_snowflake_data(query)
            
            if data:
                st.write("Results:")
                st.table(data)
            else:
                st.write("No data found.")


    elif page == "Dashboard":
        st.title("Supply Chain Dashboard 📊")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.stock_data, st.session_state.time_data, st.session_state.reorder_data, st.session_state.transport_data, st.session_state.supplier_data = fetch_dashboard_data()

        # ------------------------------
        # 1. Top 10 Products by Stock
        st.subheader("Top 10 Products by Stock")
        if st.session_state.stock_data is None:
            st.session_state.stock_data = fetch_dashboard_data()[0]

        if not st.session_state.stock_data.empty:
            st.bar_chart(st.session_state.stock_data.set_index("PRODUCT_NAME")["TOTAL_STOCK"])
        else:
            st.info("No stock data available.")

        # ------------------------------
        # 2. Stock over Time
        st.subheader("Stock Quantity Over Time")
        if st.session_state.time_data is None:
            st.session_state.time_data = fetch_dashboard_data()[1]

        if not st.session_state.time_data.empty:
            st.session_state.time_data["EVENT_DATE"] = pd.to_datetime(st.session_state.time_data["EVENT_DATE"])
            fig = px.line(st.session_state.time_data, x="EVENT_DATE", y="TOTAL_STOCK", title="Total Stock Over Time")
            st.plotly_chart(fig)
        else:
            st.info("No time series data available.")

        # ------------------------------
        # 3. Current Stock vs Reorder Threshold
        st.subheader("Current Stock vs Reorder Threshold")
        if st.session_state.reorder_data is None:
            st.session_state.reorder_data = fetch_dashboard_data()[2]

        if not st.session_state.reorder_data.empty:
            fig = px.bar(st.session_state.reorder_data, x="PRODUCT_NAME", y=["CURRENT_STOCK", "REORDER_THRESHOLD"], barmode="group")
            st.plotly_chart(fig)
        else:
            st.info("No reorder threshold data.")

        # ------------------------------
        # 4. Route Transport Mode Distribution
        st.subheader("Transport Mode Distribution")
        if st.session_state.transport_data is None:
            st.session_state.transport_data = fetch_dashboard_data()[3]

        if not st.session_state.transport_data.empty:
            fig = px.pie(st.session_state.transport_data, names="TRANSPORT_MODE", values="ROUTE_COUNT", title="Transport Mode Usage")
            st.plotly_chart(fig)
        else:
            st.info("No route data available.")

        # ------------------------------
        # 5. Supplier Reliability
        st.subheader("Supplier Reliability Score")
        if st.session_state.supplier_data is None:
            st.session_state.supplier_data = fetch_dashboard_data()[4]

        if not st.session_state.supplier_data.empty:
            fig = px.bar(st.session_state.supplier_data, x="SUPPLIER_NAME", y="RELIABILITY", title="Reliability by Supplier")
            st.plotly_chart(fig)
        else:
            st.info("No supplier reliability data.")

            
if __name__ == "__main__":
    main()
