import streamlit as st
import pandas as pd
from datetime import datetime
import time
# from data.data_manager import GoogleSheetsManager
from data.test_data_manager import GoogleSheetsManager

# Page configuration
st.set_page_config(
    page_title="Booth Checklist",
    page_icon="✅",
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
st.title("✅ Booth Checklist")
st.caption(f"Show: {st.session_state.current_show}")

# Function to load checklist data
@st.cache_data(ttl=60)  # Cache for 1 minute
def load_checklists():
    # Load header data from the "Orders" sheet
    orders_df = gs_manager.get_data(st.secrets["booth_checklist_sheet_id"], "Orders")
    
    # Get the list of available sections
    worksheets = gs_manager.get_worksheets(st.secrets["booth_checklist_sheet_id"])
    sections = [ws for ws in worksheets if ws.startswith("Section") or ws == "No Section"]
    
    # Dictionary to store data by section
    section_data = {}
    
    orders_df.columns = orders_df.iloc[0]  # row 0 = column names
    orders_df = orders_df[1:]              # remove the now unnecessary row 0
    orders_df = orders_df.reset_index(drop=True)  # reindex properly

    # Load data for each section
    for section in sections:
        section_df = gs_manager.get_data(st.secrets["booth_checklist_sheet_id"], section)

        section_df.columns = section_df.iloc[0]  # row 0 = column names
        section_df = section_df[1:]              # remove the now unnecessary row 0
        section_df = section_df.reset_index(drop=True)  # reindex properly

        if not section_df.empty:
            section_data[section] = section_df
    
    return orders_df, section_data, sections

# Load data
checklist_orders, section_data, available_sections = load_checklists()

# Sidebar to select section
with st.sidebar:
    st.header("Filters")
    
    # Add "All sections" option
    selection_options = ["All sections"] + available_sections
    selected_section = st.selectbox("Select a section", selection_options)
    
    # Status filter
    status_options = ["All", "Checked", "Unchecked"]
    selected_status = st.selectbox("Status", status_options)
    
    # Search by booth number or exhibitor
    search_query = st.text_input("Search for a booth or exhibitor")

# Determine which data to display based on filters
if selected_section == "All sections":
    # Combine data from all sections
    all_data = []
    for section, df in section_data.items():
        if not df.empty:
            # Add data from this section
            all_data.append(df)
    
    # Concatenate all DataFrames if there are any
    display_df = pd.concat(all_data) if all_data else pd.DataFrame()
else:
    # Display only the selected section
    display_df = section_data.get(selected_section, pd.DataFrame())

# Apply status filter
if not display_df.empty:
    if selected_status == "Checked":
        display_df = display_df[display_df["Status"] == True]
    elif selected_status == "Unchecked":
        display_df = display_df[display_df["Status"] == False]

# Apply search filter
if search_query and not display_df.empty:
    # Correction pour la recherche exacte de booth
    try:
        # Si la recherche est un nombre, on cherche exactement ce numéro de booth
        if search_query.isdigit():
            search_condition = display_df["Booth #"].astype(str) == search_query
        else:
            # Pour les recherches qui ne sont pas des numéros, on garde la recherche par contenance
            search_condition = display_df["Booth #"].astype(str).str.contains(search_query, case=False, na=False)
        
        # Vérifier si "Exhibitor Name" existe dans les colonnes
        if "Exhibitor Name" in display_df.columns:
            # Pour le nom d'exposant, toujours utiliser la recherche par contenance
            search_condition = search_condition | display_df["Exhibitor Name"].astype(str).str.contains(search_query, case=False, na=False)
        
        display_df = display_df[search_condition]
    except Exception as e:
        st.error(f"Error in search: {e}")

# Metrics at the top of the page
st.subheader("Overview")

# Calculate metrics
if not display_df.empty:
    total_items = len(display_df)
    completed_items = len(display_df[display_df["Status"] == True])
    completion_percentage = int((completed_items / total_items * 100) if total_items > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Items", total_items)
    
    with col2:
        st.metric("Checked Items", completed_items)
    
    with col3:
        st.metric("Progress", f"{completion_percentage}%")
    
    # Progress bar
    st.progress(completion_percentage / 100)
else:
    st.info("No data available for the selected filters.")


# Display data by booth
if not display_df.empty:
    st.subheader("List of Items")
    
    # Check if 'Section' column exists before grouping
    if 'Section ' in display_df.columns and 'Exhibitor Name ' in display_df.columns:
        booths = display_df.groupby(["Booth #", "Section ", "Exhibitor Name "])
    else:
        booths = display_df.groupby(["Booth #", "Exhibitor Name"]) if 'Exhibitor Name' in display_df.columns else display_df.groupby("Booth #")
    
    # For each booth, create an expander
    for booth_info, items in booths:
        # Ensure booth_info is a tuple or list
        if isinstance(booth_info, (tuple, list)):
            booth_number = booth_info[0]  # Extract booth number
            exhibitor_info = booth_info[1:] if len(booth_info) > 1 else ["Unknown"]
            exhibitor = exhibitor_info[0] if exhibitor_info else "Unknown"
        else:
            booth_number = booth_info
            exhibitor = "Unknown"
        
        with st.expander(f"Booth #{booth_number} - {exhibitor}"):
            # Calculate progress for this booth
            booth_total = len(items)
            booth_completed = len(items[items["Status"] == True])
            booth_progress = int((booth_completed / booth_total * 100) if booth_total > 0 else 0)
            
            # Display booth progress
            st.progress(booth_progress / 100)
            st.write(f"**Progress:** {booth_completed}/{booth_total} items checked ({booth_progress}%)")
            
            # Create a list of checkboxes for each item
            for idx, row in items.iterrows():
                # Create a unique key for each item
                item_key = f"{booth_number}_{row['Item Name']}_{idx}"
                
                # Get the current status
                current_status = row["Status"] == True
                
                # Create a line with the checkbox and details
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    # Checkbox to modify the status
                    new_status = st.checkbox(
                        "", 
                        value=current_status,
                        key=item_key
                    )
                    
                    # If the status has changed, update the Google Sheet
                    if new_status != current_status:
                        # Prepare data to update
                        update_data = {
                            "Status": new_status,
                            "Date": datetime.now().strftime("%m-%d-%y"),
                            "Hour": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        # Update in Google Sheets
                        try:
                            gs_manager.update_checklist_item(
                                sheet_id=st.secrets["booth_checklist_sheet_id"],
                                worksheet=row.get("Section", selected_section),  # Use selected_section as default
                                booth_num=booth_number,
                                item_name=row["Item Name"],
                                data=update_data
                            )
                            
                            # Display a temporary success message
                            st.success(f"Status updated for {row['Item Name']}")
                            
                            # Reload data after a few seconds
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating: {e}")
                
                with col2:
                    quantity = row.get('Quantity', 'N/A')  # Use 'N/A' if 'Quantity' key is missing
                    st.write(f"**{row['Item Name']}** (Qty: {quantity})")
                    if pd.notna(row.get('Special Instructions')) and row['Special Instructions']:
                        st.caption(f"Instructions: {row['Special Instructions']}")
                
                with col3:
                    if current_status:
                        status_date = row.get('Date', '')
                        status_hour = row.get('Hour', '')
                        if pd.notna(status_date) and pd.notna(status_hour):
                            st.caption(f"Checked on {status_date} at {status_hour}")
                
                st.divider()
                
    # Button to refresh data
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("No items found with the current filters.")