import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import io
from utils import validate_csv_data, calculate_metrics, format_currency
from sample_data import generate_sample_data

# Page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'date_column' not in st.session_state:
    st.session_state.date_column = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'date_min' not in st.session_state:
    st.session_state.date_min = None
if 'date_max' not in st.session_state:
    st.session_state.date_max = None

# Main title
st.title("📊 Sales Dashboard")

# Sidebar for data upload and filters
with st.sidebar:
    st.header("Data Upload")
    
    uploaded_file = st.file_uploader("Upload your sales CSV file", type=["csv"])
    
    use_sample_data = st.checkbox("Use sample data for demonstration", value=False)
    
    if use_sample_data:
        if st.button("Generate Sample Data"):
            with st.spinner("Generating sample data..."):
                sample_df = generate_sample_data()
                st.session_state.data = sample_df
                st.session_state.date_column = 'Date'
                st.success("Sample data generated successfully!")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            validation_result, message = validate_csv_data(df)
            
            if validation_result:
                st.success(message)
                
                # Detect date columns
                date_columns = []
                for col in df.columns:
                    try:
                        pd.to_datetime(df[col])
                        date_columns.append(col)
                    except:
                        pass
                
                if date_columns:
                    selected_date_column = st.selectbox("Select the date column", date_columns)
                    df[selected_date_column] = pd.to_datetime(df[selected_date_column])
                    st.session_state.date_column = selected_date_column
                    st.session_state.data = df
                    
                    # Set date min and max
                    st.session_state.date_min = df[selected_date_column].min().date()
                    st.session_state.date_max = df[selected_date_column].max().date()
                else:
                    st.error("No date columns detected in the data. Please ensure your CSV contains date information.")
            else:
                st.error(message)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Date range filter (if data is loaded)
    if st.session_state.data is not None and st.session_state.date_column is not None:
        st.header("Filters")
        
        date_min = st.session_state.date_min
        date_max = st.session_state.date_max
        
        selected_date_range = st.date_input(
            "Select Date Range",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max
        )
        
        # Handle single date selection
        if len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
        else:
            start_date = selected_date_range[0]
            end_date = selected_date_range[0]
        
        # Category filter if categories exist
        if st.session_state.data is not None and 'Category' in st.session_state.data.columns:
            categories = ['All'] + sorted(st.session_state.data['Category'].unique().tolist())
            selected_category = st.selectbox("Select Product Category", categories)
        else:
            selected_category = 'All'

# Main dashboard
if st.session_state.data is not None and st.session_state.date_column is not None:
    # Filter data based on date range
    df = st.session_state.data.copy()
    date_col = st.session_state.date_column
    
    filtered_df = df[(df[date_col].dt.date >= start_date) & 
                      (df[date_col].dt.date <= end_date)]
    
    # Apply category filter
    if selected_category != 'All' and 'Category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    # Calculate metrics
    metrics_dict = calculate_metrics(filtered_df)
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sales", format_currency(metrics_dict['total_sales']))
    
    with col2:
        st.metric("Average Order Value", format_currency(metrics_dict['avg_order_value']))
    
    with col3:
        st.metric("Total Orders", f"{metrics_dict['total_orders']:,}")
    
    with col4:
        st.metric("Unique Customers", f"{metrics_dict['unique_customers']:,}")
    
    # Sales Trend Over Time
    st.subheader("Sales Trend")
    
    # Group by date
    sales_by_date = filtered_df.groupby(filtered_df[date_col].dt.date)['Amount'].sum().reset_index()
    sales_by_date.columns = ['Date', 'Sales']
    
    # Create line chart for sales trend
    fig_trend = px.line(
        sales_by_date, 
        x='Date', 
        y='Sales',
        title='Daily Sales Trend',
        labels={'Sales': 'Sales Amount', 'Date': 'Date'},
        template='plotly_white'
    )
    fig_trend.update_layout(height=400)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Split dashboard into two columns for category and product breakdown
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Sales by Category")
        if 'Category' in filtered_df.columns:
            category_sales = filtered_df.groupby('Category')['Amount'].sum().reset_index()
            category_sales = category_sales.sort_values('Amount', ascending=False)
            
            fig_category = px.bar(
                category_sales,
                x='Category',
                y='Amount',
                title='Sales by Product Category',
                labels={'Amount': 'Sales Amount', 'Category': 'Product Category'},
                template='plotly_white'
            )
            fig_category.update_layout(height=400)
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("No category data available in the uploaded file.")
    
    with col_right:
        st.subheader("Top Products")
        if 'Product' in filtered_df.columns:
            product_sales = filtered_df.groupby('Product')['Amount'].sum().reset_index()
            top_products = product_sales.sort_values('Amount', ascending=False).head(10)
            
            fig_products = px.bar(
                top_products,
                x='Amount',
                y='Product',
                title='Top 10 Products by Sales',
                labels={'Amount': 'Sales Amount', 'Product': 'Product Name'},
                template='plotly_white',
                orientation='h'
            )
            fig_products.update_layout(height=400)
            st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.info("No product data available in the uploaded file.")
    
    # Monthly comparison
    if len(filtered_df[date_col].dt.date.unique()) > 30:  # Only show if we have more than a month of data
        st.subheader("Monthly Sales Comparison")
        
        # Add month and year columns
        filtered_df['Month'] = filtered_df[date_col].dt.strftime('%b')
        filtered_df['Year'] = filtered_df[date_col].dt.year
        filtered_df['MonthYear'] = filtered_df[date_col].dt.strftime('%b %Y')
        
        # Group by month and year
        monthly_sales = filtered_df.groupby(['Year', 'Month', 'MonthYear'])['Amount'].sum().reset_index()
        
        # Sort chronologically
        month_order = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 
                       'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        monthly_sales['MonthNum'] = monthly_sales['Month'].map(month_order)
        monthly_sales = monthly_sales.sort_values(['Year', 'MonthNum'])
        
        fig_monthly = px.bar(
            monthly_sales,
            x='MonthYear',
            y='Amount',
            title='Monthly Sales',
            labels={'Amount': 'Sales Amount', 'MonthYear': 'Month'},
            template='plotly_white'
        )
        fig_monthly.update_layout(height=400, xaxis={'categoryorder': 'array', 'categoryarray': monthly_sales['MonthYear']})
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Raw data viewer (with expand/collapse)
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df)
        
        # Download button for filtered data
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()
        
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_str,
            file_name="filtered_sales_data.csv",
            mime="text/csv"
        )

else:
    # Show instructions if no data is loaded
    st.info("""
    ### Welcome to the Sales Dashboard!
    
    To get started:
    1. Upload your sales data CSV file using the sidebar, or
    2. Use the sample data option for demonstration
    
    Your CSV should contain:
    - Date column (for time-based analysis)
    - Sales/Amount column (numeric values)
    - Optional: Product, Category, Customer columns for detailed analysis
    
    Once data is loaded, you can filter by date range and explore your sales metrics.
    """)
