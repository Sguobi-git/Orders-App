import streamlit as st
import pandas as pd
from datetime import datetime
import time
import asyncio
# from data.data_manager import GoogleSheetsManager
from data.test_data_manager import GoogleSheetsManager
from data.direct_sheets_operations import direct_add_order

# Page configuration
st.set_page_config(
    page_title="Order Management",
    page_icon="📦",
    layout="wide"
)

# Authentication check
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in to access this page.")
    st.stop()

# Current show check
if "current_show" not in st.session_state or st.session_state.current_show is None:
    st.warning("Please select a show to continue.")
    st.stop()

# Data manager initialization
gs_manager = GoogleSheetsManager()

# Page header
st.title("📦 Order Management")
st.caption(f"Show: {st.session_state.current_show}")

# Properly handle cache clearing
def safe_clear_cache():
    try:
        # Use session state to track if we need to reload data
        st.session_state.reload_data = True
    except Exception as e:
        st.error(f"Error clearing cache: {e}")

# Function to load data
@st.cache_data(ttl=30)  # Cache for 30 seconds to refresh more frequently
def load_orders():
    # Load header data from the "Orders" sheet
    # orders_df = gs_manager.get_data(st.secrets["order_tracking_sheet_id"], "Orders")
    orders_df = gs_manager.get_data("1Kbdarxula-BboWoErv2gjnsd7d4SuGkKj_y4pILyNBQ", "Orders")
    # Get the list of available sections
    # worksheets = gs_manager.get_worksheets(st.secrets["order_tracking_sheet_id"])
    worksheets = gs_manager.get_worksheets("1Kbdarxula-BboWoErv2gjnsd7d4SuGkKj_y4pILyNBQ")
    sections = [ws for ws in worksheets if ws.startswith("Section")]
    
    # Load inventory data
    # inventory_df = gs_manager.get_data(st.secrets["order_tracking_sheet_id"], "Show Inventory")
    inventory_df = gs_manager.get_data("1Kbdarxula-BboWoErv2gjnsd7d4SuGkKj_y4pILyNBQ", "Show Inventory")

    # Redefine column names from the first row
    orders_df.columns = orders_df.iloc[0].str.strip()  # Strip whitespace from column names
    orders_df = orders_df[1:]              # remove the now unnecessary row 0
    orders_df = orders_df.reset_index(drop=True)  # reindex properly

    # Redefine column names from the first row for inventory
    inventory_df.columns = inventory_df.iloc[0].str.strip()  # Strip whitespace from column names
    inventory_df = inventory_df[1:]              # remove the now unnecessary row 0
    inventory_df = inventory_df.reset_index(drop=True)  # reindex properly

    # Extract the list of available items from the inventory
    available_items = inventory_df["Items"].dropna().tolist() if not inventory_df.empty else []
    
    return orders_df, sections, inventory_df, available_items

# Initialize the session state for data reloading if needed
if "reload_data" not in st.session_state:
    st.session_state.reload_data = False

# Check if we need to reload data and reset the flag
if st.session_state.get('reload_data', False):
    load_orders.clear()
    st.session_state.reload_data = False

# Load data
orders_df, sections, inventory_df, available_items = load_orders()

# Function to add a new order
def add_new_order():
    st.subheader("Add a New Order")
    
    with st.form("new_order_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            booth_num = st.text_input("Booth Number")  # Removed 'required=True'
            
            # If sections are available, show a selector
            if sections:
                section = st.selectbox("Section", sections)
            else:
                section = st.text_input("Section")
            
            status = st.selectbox("Status", ["Delivered", "Received", "In route from warehouse", "In Process", "Out for delivery", "cancelled"])
            

        
        with col2:
            exhibitor_name = st.text_input("Exhibitor Name")
            
            # If items are available, show a selector
            if available_items:
                item = st.selectbox("Item", [""] + available_items + ["Unlisted Item - See the Comments"])
            else:
                item = st.text_input("Item")
            
            comments_required = item == "Unlisted Item - See the Comments"

            # Order type
            order_type = st.selectbox("Type", ["New Order", "Missing Item ", "Remove"])

        
        with col3:
            color_options = ["White ", "Black ", "Blue", "Red ", "Green ", "Burgundy", "Teal", "Other"]
            color = st.selectbox("Color", color_options)
            
            quantity = st.number_input("Quantity", min_value=1, max_value=10000000000000, value=1)

            boomer = st.number_input("Boomer's Quantity", min_value=1, max_value=10000000000000, value=1)
            
            # printed = st.text_input("Printed?")
            
    
        # Comments
        comments = st.text_area("Comments", max_chars=1000, help="Enter additional details here")
        
        # Check if comments are required
        if comments_required and not comments:
            st.warning("Comments are required for unlisted items.")
        
        # Submit button
        submit_button = st.form_submit_button("Add Order", use_container_width=True)
        
        if submit_button:
            if not booth_num:
                st.error("Booth number is required.")
            elif comments_required and not comments:
                st.error("Comments are required for unlisted items.")
            else:
                # Rafraîchir le client avant d'ajouter une commande
                # gs_manager.refresh_client()
                
                # Prepare order data
                order_data = {
                    'Booth #': booth_num,
                    'Section': section,
                    'Exhibitor Name': exhibitor_name,
                    'Item': item,
                    'Color': color,
                    'Quantity': quantity,
                    'Status': status,
                    'Type': order_type,
                    # 'Printed': printed,
                    "Boomer's Quantity": boomer,  # Use exact column name with apostrophe
                    'Comments': comments,
                    'User': st.session_state.current_user
                }
                
                # Add the order
                # success = gs_manager.add_order(st.secrets["order_tracking_sheet_id"], order_data)
                
                
                
                success = direct_add_order("1Kbdarxula-BboWoErv2gjnsd7d4SuGkKj_y4pILyNBQ", order_data)
                if success:
                    st.success("Order added successfully!")
                    # Use safe method to clear cache
                    safe_clear_cache()
                    time.sleep(1)
                    st.rerun()  # Reload the page
                else:
                    st.error("Error adding the order.")

# Sidebar for selecting section and status
with st.sidebar:
    st.header("Filters")
    
    # Section selector
    section_options = ["All Sections"] + sections
    selected_section = st.selectbox("Section", section_options)
    
    # Status filter
    status_options = ["All", "Delivered", "New", "In Progress", "Cancelled"]
    selected_status = st.selectbox("Status", status_options)
    
    # Search by booth number or exhibitor
    search_query = st.text_input("Search by booth or exhibitor")
    
    # Button to refresh data
    if st.button("🔄 Refresh Data", use_container_width=True):
        # Use safe method to clear cache
        safe_clear_cache()
        st.rerun()

# Main interface with tabs
tab1, tab2 = st.tabs(["Order List", "New Order"])

with tab1:
    # Filter data according to criteria
    filtered_df = orders_df.copy()
    
    # Apply section filter
    if selected_section != "All Sections":
        filtered_df = filtered_df[filtered_df["Section"] == selected_section]
    
    # Apply status filter
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["Status"] == selected_status]
    
    # Apply search filter
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Booth #"].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_df["Exhibitor Name"].str.contains(search_query, case=False, na=False)
        ]
    
    # Display number of orders found
    st.write(f"**{len(filtered_df)} orders found**")
    
    # Display data
    if not filtered_df.empty:
        # Columns to display
        display_columns = ["Booth #", "Section", "Exhibitor Name", "Item", "Color", 
                  "Quantity", "Date", "Hour", "Status", "Type", "Boomer's Quantity", "Comments", "User"]
        
        # Check that all columns to display exist in the DataFrame
        display_columns = [col for col in display_columns if col in filtered_df.columns]
        
        # Display data as a table
        edited_df = st.data_editor(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Booth #": st.column_config.NumberColumn(
                    "Booth #",
                    width="small",
                ),
                "Section": st.column_config.TextColumn(
                    "Section",
                    width="medium",
                ),
                "Color": st.column_config.TextColumn(
                    "Color",
                    width="small",
                ),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    width="small",
                ),
                "Date": st.column_config.TextColumn(
                    "Date",
                    width="small",
                ),
                "Hour": st.column_config.TextColumn(
                    "Hour",
                    width="small",
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    width="small",
                    options=["In Process", "In route from warehouse", "Delivered", "Cancelled", "Received"],
                ),
                "Type": st.column_config.SelectboxColumn(
                    "Type",
                    width="small",
                    options=["New Order", "Missing Item ", "Remove"],
                ),
                "Boomer's Quantity": st.column_config.NumberColumn(
                    "Boomer's Quantity",
                    width="small",
                ),
                "Comments": st.column_config.TextColumn(
                    "Comments",
                    width="medium",
                ),
                # "Printed": st.column_config.NumberColumn(
                #     "Boomer's Quantity",
                #     width="small",
                # ),
                "User": st.column_config.TextColumn(
                    "User",
                    width="small",
                ),
                "Exhibitor Name": st.column_config.TextColumn(
                    "Exhibitor Name",
                    width="medium",
                ),
                "Item": st.column_config.TextColumn(
                    "Item",
                    width="medium",
                ),
            },
            num_rows="dynamic",
        )
        
        # Check if any modifications have been made
        if edited_df is not None and not edited_df.equals(filtered_df[display_columns]):
            # Identifier les lignes modifiées
            for i, (_, row) in enumerate(edited_df.iterrows()):
                original_row = filtered_df.iloc[i]
                
                # Vérifier chaque colonne pour des modifications
                for col in display_columns:
                    # Handle NA values safely by using pandas.isna() to check for NaN values
                    if pd.isna(row[col]) and pd.isna(original_row[col]):
                        continue  # Both are NaN, so they're equal
                    elif pd.isna(row[col]) or pd.isna(original_row[col]):
                        # One is NaN and the other isn't, so they're different
                        if col == "Status":
                            # Handle status update
                            booth_num = original_row["Booth #"]
                            item_name = original_row["Item"]
                            color = original_row["Color"]
                            new_status = row["Status"] if not pd.isna(row["Status"]) else ""
                            
                            # Déterminer la feuille de travail
                            worksheet = "Orders"
                            if original_row["Section"] in sections:
                                worksheet = original_row["Section"]
                            
                            # Mettre à jour le statut
                            success = gs_manager.update_order_status(
                                sheet_id="1Kbdarxula-BboWoErv2gjnsd7d4SuGkKj_y4pILyNBQ",
                                worksheet=worksheet,
                                booth_num=booth_num,
                                item_name=item_name,
                                color=color,
                                status=new_status,
                                user=st.session_state.current_user
                            )
                            
                            if success:
                                st.success(f"Status updated for booth #{booth_num}, item {item_name}")
                                safe_clear_cache()
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"Error updating status for booth #{booth_num}")
                    elif row[col] != original_row[col]:
                        # Neither is NaN and they're different
                        if col == "Status":
                            # Handle status update
                            booth_num = original_row["Booth #"]
                            item_name = original_row["Item"]
                            color = original_row["Color"]
                            new_status = row["Status"]
                            
                            # Déterminer la feuille de travail
                            worksheet = "Orders"
                            if original_row["Section"] in sections:
                                worksheet = original_row["Section"]
                            
                            # Mettre à jour le statut
                            success = gs_manager.update_order_status(
                                sheet_id="1Kbdarxula-BboWoErv2gjnsd7d4SuGkKj_y4pILyNBQ",
                                worksheet=worksheet,
                                booth_num=booth_num,
                                item_name=item_name,
                                color=color,
                                status=new_status,
                                user=st.session_state.current_user
                            )
                        
                            if success:
                                st.success(f"Status updated for booth #{booth_num}, item {item_name}")
                                safe_clear_cache()
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"Error updating status for booth #{booth_num}")
    else:
        st.info("No orders match the search criteria.")

with tab2:
    # Interface to add a new order
    add_new_order()

# Statistics at the bottom of the page
if not orders_df.empty:
    st.divider()
    st.subheader("Order Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Orders by section
        section_counts = orders_df["Section"].value_counts().reset_index()
        section_counts.columns = ["Section", "Number of Orders"]
        
        st.write("**Orders by Section**")
        st.dataframe(
            section_counts,
            use_container_width=True,
            hide_index=True,
        )
    
    with col2:
        # Order statuses
        status_counts = orders_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Number"]
        
        st.write("**Order Statuses**")
        st.dataframe(
            status_counts,
            use_container_width=True,
            hide_index=True,
        )
    
    with col3:
        # Most ordered items
        top_items = orders_df["Item"].value_counts().reset_index().head(5)
        top_items.columns = ["Item", "Number"]
        
        st.write("**Most Ordered Items**")
        st.dataframe(
            top_items,
            use_container_width=True,
            hide_index=True,
        )