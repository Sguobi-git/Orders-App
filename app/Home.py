import streamlit as st
import pandas as pd
import hashlib
import secrets
import string
import json
import os
from datetime import datetime
# from data.data_manager import GoogleSheetsManager
from data.test_data_manager import GoogleSheetsManager

# For pie chart
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Show Management",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File path for storing users data
USERS_FILE = ".streamlit/users.json"

# Ensure the .streamlit directory exists
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

# Password utilities
def generate_password(length=10):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password):
    """Create a SHA-256 hash of a password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    """Verify a password against its hash"""
    return stored_hash == hashlib.sha256(provided_password.encode()).hexdigest()

# User data management functions
def load_users():
    """Load users from the users file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        else:
            # Create default admin account
            default_users = {
                "admin@expocci.com": {
                    "password_hash": hash_password("admin123"),
                    "initials": "AD",
                    "is_admin": True,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            save_users(default_users)
            return default_users
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return {}

def save_users(users_data):
    """Save users to the users file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f)
        return True
    except Exception as e:
        st.error(f"Error saving users: {e}")
        return False

# Initialize session states
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "current_show" not in st.session_state:
    st.session_state.current_show = None

if "users" not in st.session_state:
    st.session_state.users = load_users()

# Login function
# def login():
#     if email_input.endswith("@expocci.com"):
#         if email_input in st.session_state.users:
#             # User exists, verify password
#             if verify_password(st.session_state.users[email_input]["password_hash"], password_input):
#                 st.session_state.authenticated = True
#                 st.session_state.current_user = st.session_state.users[email_input]["initials"]
#                 st.rerun()
#             else:
#                 st.error("Invalid password")
#         else:
#             st.error("User not found. Please use the registration form.")
#     else:
#         st.error("Please use your company email (@expocci.com)")


# Modification 1: Update the login function to set the current_show automatically
def login():
    if email_input.endswith("@expocci.com"):
        if email_input in st.session_state.users:
            # User exists, verify password
            if verify_password(st.session_state.users[email_input]["password_hash"], password_input):
                st.session_state.authenticated = True
                st.session_state.current_user = st.session_state.users[email_input]["initials"]
                # Automatically set the current show to the first option
                show_options = ["Miami Boat Show 2025", "New York Auto Show 2025", "Paris Expo 2025"]
                st.session_state.current_show = show_options[0]
                st.rerun()
            else:
                st.error("Invalid password")
        else:
            st.error("User not found. Please use the registration form.")
    else:
        st.error("Please use your company email (@expocci.com)")


# Registration function
def register_user():
    if not register_email.endswith("@expocci.com"):
        st.error("Please use a valid company email address (@expocci.com)")
        return
    
    if register_email in st.session_state.users:
        st.error("This email is already registered")
        return
    
    if register_password != confirm_password:
        st.error("Passwords do not match")
        return
    
    if len(register_password) < 8:
        st.error("Password must be at least 8 characters long")
        return
    
    # Extract initials from email
    if '@' in register_email:
        email_prefix = register_email.split('@')[0]
        if '.' in email_prefix:
            # Format: first.last@expocci.com
            parts = email_prefix.split('.')
            initials = parts[0][0].upper() + parts[-1][0].upper()
        else:
            # Either single name or first letter + last name
            if len(email_prefix) <= 2:
                initials = email_prefix.upper()
            else:
                initials = email_prefix[:2].upper()
    else:
        initials = register_email[:2].upper()
    
    # Store the new user
    st.session_state.users[register_email] = {
        "password_hash": hash_password(register_password),
        "initials": initials,
        "is_admin": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save the updated users data
    save_users(st.session_state.users)
    
    st.success("Registration successful! You can now log in.")

# Admin function to create user
def create_user():
    if not admin_create_email.endswith("@expocci.com"):
        st.error("Please use a valid company email address (@expocci.com)")
        return
    
    if admin_create_email in st.session_state.users:
        st.error("This email is already registered")
        return
    
    # Generate a random password
    temp_password = generate_password()
    
    # Extract initials from email
    if '@' in admin_create_email:
        email_prefix = admin_create_email.split('@')[0]
        if '.' in email_prefix:
            # Format: first.last@expocci.com
            parts = email_prefix.split('.')
            initials = parts[0][0].upper() + parts[-1][0].upper()
        else:
            # Either single name or first letter + last name
            if len(email_prefix) <= 2:
                initials = email_prefix.upper()
            else:
                initials = email_prefix[:2].upper()
    else:
        initials = admin_create_email[:2].upper()
    
    # Store the new user
    st.session_state.users[admin_create_email] = {
        "password_hash": hash_password(temp_password),
        "initials": initials,
        "is_admin": make_admin,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save the updated users data
    save_users(st.session_state.users)
    
    st.success(f"""
    User created successfully!
    
    Email: {admin_create_email}
    Temporary Password: {temp_password}
    
    Please securely communicate this password to the user.
    """)

# Admin function to delete user
def delete_user(email):
    if email in st.session_state.users:
        # Don't allow deleting yourself
        current_email = None
        for e, user_data in st.session_state.users.items():
            if user_data.get("initials") == st.session_state.current_user:
                current_email = e
                break
        
        if email == current_email:
            st.error("You cannot delete your own account")
            return False
        
        # Remove the user
        del st.session_state.users[email]
        
        # Save the updated users data
        save_users(st.session_state.users)
        return True
    
    return False

# Password reset function
def reset_password():
    if not reset_email.endswith("@expocci.com"):
        st.error("Please use a valid company email address (@expocci.com)")
        return
    
    if reset_email not in st.session_state.users:
        st.error("Email not found. Please register first.")
        return
    
    # Generate a new password
    new_password = generate_password()
    
    # Update user's password
    st.session_state.users[reset_email]["password_hash"] = hash_password(new_password)
    st.session_state.users[reset_email]["last_reset"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save the updated users data
    save_users(st.session_state.users)
    
    st.success(f"""
    Password reset successful!
    
    Your new temporary password is: {new_password}
    
    Please save this password immediately, as it won't be shown again.
    """)

# Change password function
def change_password():
    # Find current user's email
    current_email = None
    for email, user_data in st.session_state.users.items():
        if user_data.get("initials") == st.session_state.current_user:
            current_email = email
            break
    
    if not current_email:
        st.error("User not found")
        return
    
    if not verify_password(st.session_state.users[current_email]["password_hash"], current_password):
        st.error("Current password is incorrect")
        return
    
    if new_password != confirm_new_password:
        st.error("New passwords do not match")
        return
    
    if len(new_password) < 8:
        st.error("New password must be at least 8 characters long")
        return
    
    # Update the password
    st.session_state.users[current_email]["password_hash"] = hash_password(new_password)
    st.session_state.users[current_email]["last_reset"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save the updated users data
    save_users(st.session_state.users)
    
    st.success("Password changed successfully!")

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_show = None
    # Reset the show_button state to True so it appears again on next login
    st.session_state['show_button'] = True
    st.rerun()

# Function to change show
def change_show():
    st.session_state.current_show = selected_show
    st.rerun()

# Initialize data manager
gs_manager = GoogleSheetsManager()

# Login page if not authenticated
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🎪 Show Management")
        
        # Create tabs for Login, Registration, and Password Reset
        auth_tab1, auth_tab2, auth_tab3 = st.tabs(["Login", "Register", "Reset Password"])
        
        with auth_tab1:
            st.subheader("Login")
            email_input = st.text_input("Email (@expocci.com)", key="login_email")
            password_input = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, key="login_button"):
                if email_input and password_input:
                    login()
                else:
                    st.error("Please enter both email and password")
        
        with auth_tab2:
            st.subheader("Register")
            st.write("Register with your company email address.")
            register_email = st.text_input("Email (@expocci.com)", key="register_email")
            register_password = st.text_input("Password (min 8 characters)", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Register", use_container_width=True, key="register_button"):
                if register_email and register_password and confirm_password:
                    register_user()
                else:
                    st.error("Please fill in all fields")
        
        with auth_tab3:
            st.subheader("Reset Password")
            st.write("Reset your password if you've forgotten it.")
            reset_email = st.text_input("Email (@expocci.com)", key="reset_email")
            
            if st.button("Reset Password", use_container_width=True, key="reset_button"):
                if reset_email:
                    reset_password()
                else:
                    st.error("Please enter your email address")
        
        st.caption("Contact your administrator if you need assistance")
else:
    # Check if current user is an admin
    current_email = None
    for email, user_data in st.session_state.users.items():
        if user_data.get("initials") == st.session_state.current_user:
            current_email = email
            break
    
    is_admin = False
    if current_email and st.session_state.users[current_email].get("is_admin", False):
        is_admin = True

    
    # Display user sidebar
    # with st.sidebar:
    #     st.write(f"**User:** {st.session_state.current_user}")
        
    #     # Show selector
    #     st.divider()
    #     st.subheader("Active Show")
    with st.sidebar:
        st.write(f"**User:** {st.session_state.current_user}")
        
        # Show information (display only, not a selector)
        # st.divider()
        # st.subheader("Active Show")
        # st.info(f"{st.session_state.current_show}")
        
        # # In a real application, you would load the list of shows from Google Sheets
        # show_options = ["Miami Boat Show 2025", "New York Auto Show 2025", "Paris Expo 2025"]
        # selected_show = st.selectbox(
        #     "Select a show",
        #     show_options,
        #     index=0 if st.session_state.current_show is None else show_options.index(st.session_state.current_show)
        # )
        
        # if st.button("Change show", use_container_width=True):
        #     change_show()
        
        # Account settings
        st.divider()
        st.subheader("Account Settings")
        
        with st.expander("Change Password"):
            current_password = st.text_input("Current Password", type="password", key="current_password")
            new_password = st.text_input("New Password (min 8 chars)", type="password", key="new_password")
            confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")
            
            if st.button("Update Password", use_container_width=True, key="change_password_button"):
                if current_password and new_password and confirm_new_password:
                    change_password()
                else:
                    st.error("Please fill in all fields")
        
        # Admin section
        if is_admin:
            st.divider()
            st.subheader("Admin Panel")
            
            admin_tab1, admin_tab2 = st.tabs(["Create User", "User Management"])
            
            with admin_tab1:
                st.write("Create a new user account")
                admin_create_email = st.text_input("Email (@expocci.com)", key="admin_create_email")
                make_admin = st.checkbox("Make this user an admin", key="make_admin")
                
                if st.button("Create User", use_container_width=True, key="admin_create_button"):
                    if admin_create_email:
                        create_user()
                    else:
                        st.error("Please enter an email address")
            
            with admin_tab2:
                st.write("Registered Users")
                users_list = []
                for email, data in st.session_state.users.items():
                    users_list.append({
                        "Email": email,
                        "Initials": data.get("initials", ""),
                        "Admin": "Yes" if data.get("is_admin", False) else "No",
                        "Created/Reset": data.get("created_at", data.get("last_reset", "Unknown")),
                        "Actions": email  # Store email as a reference for actions
                    })
                
                users_df = pd.DataFrame(users_list)
                
                # Add delete button functionality - using a different approach since ButtonColumn is not available
                st.dataframe(
                    users_df.drop(columns=["Actions"]),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Create a selectbox for user deletion instead of ButtonColumn
                if users_list:
                    email_to_delete = st.selectbox(
                        "Select user to delete:",
                        options=[user["Email"] for user in users_list],
                        key="user_to_delete"
                    )
                    
                    if st.button("Delete Selected User", key="delete_user_button"):
                        if delete_user(email_to_delete):
                            st.success(f"User {email_to_delete} deleted successfully")
                            st.rerun()
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()



    # # Initialize the state
    # if 'show_button' not in st.session_state:
    #     st.session_state['show_button'] = True
    
    # # Only show the button if needed
    # if st.session_state.show_button:
    #     # Use vertical space to center vertically (about halfway down the screen)
    #     st.write("")
    #     st.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    
    #     # Create centered columns
    #     col1, col2, col3 = st.columns([1, 2, 1])
    #     with col2:
    #         st.markdown(
    #             """
    #             <style>
    #             div.stButton > button {
    #                 font-size: 1.5em;
    #                 padding: 0.75em 2em;
    #             }
    #             </style>
    #             """,
    #             unsafe_allow_html=True
    #         )
    
    #         if st.button("Start", key="change_show_button"):
    #             st.session_state['show_button'] = False
    #             change_show()



    

    

    
    # Main page (dashboard)
    # if st.session_state.current_show is None:
    #     pass
    #     # st.warning("Please select a show to continue.")
    # else:
    #     st.title(f"🎪 {st.session_state.current_show}")
    #     st.caption(f"General Dashboard")

    # st.title(f"🎪 {st.session_state.current_show}")
    st.title(f"🎪 General Dashboard")
    # st.caption(f"General Dashboard")
        
    # Loading data
    @st.cache_data(ttl=60)  # Cache for 1 minute
    def load_dashboard_data():
        try:
            # Load order data
            orders_df = gs_manager.get_data("1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE", "Orders")
            
            # Redefine column names from the first row
            if not orders_df.empty:
                orders_df.columns = orders_df.iloc[0].str.strip()  # Strip whitespace from column names
                orders_df = orders_df[1:]  # remove the now unnecessary row 0
                orders_df = orders_df.reset_index(drop=True)  # reindex properly
            
            # Load checklist data
            checklist_df = gs_manager.get_data("19ksIroX0i3WY3XmSGXQpdS1RzjpYKhqMhwK1tYiKZZA", "Orders")

            if not checklist_df.empty:
                checklist_df.columns = checklist_df.iloc[0].str.strip()  # Strip whitespace from column names
                checklist_df = checklist_df[1:]  # remove the now unnecessary row 0
                checklist_df = checklist_df.reset_index(drop=True)  # reindex properly
            
            # Load inventory
            inventory_df = gs_manager.get_data("1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE", "Show Inventory")
            
            # Redefine column names for inventory
            if not inventory_df.empty:
                inventory_df.columns = inventory_df.iloc[0].str.strip()  # Strip whitespace from column names
                inventory_df = inventory_df[1:]  # remove the now unnecessary row 0
                inventory_df = inventory_df.reset_index(drop=True)  # reindex properly
            
            return orders_df, checklist_df, inventory_df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Load data
    orders_df, checklist_df, inventory_df = load_dashboard_data()
    
    # Calculate metrics
    if not orders_df.empty:
        # Order metrics
        total_orders = len(orders_df)
        # Check if "Status" column exists before filtering
        if "Status" in orders_df.columns:
            delivered_orders = len(orders_df[orders_df["Status"] == "Delivered"])
            cancelled_orders = len(orders_df[orders_df["Status"] == "cancelled"])
            pending_orders = total_orders - delivered_orders - cancelled_orders
            delivery_rate = int(delivered_orders / total_orders * 100) if total_orders > 0 else 0
        else:
            delivered_orders = 0
            cancelled_orders = 0
            pending_orders = total_orders
            delivery_rate = 0
            st.warning("Status column not found in orders data. Some metrics may not be accurate.")
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Orders", total_orders)
        
        with col2:
            st.metric("Delivered", delivered_orders)
        
        with col3:
            st.metric("Pending", pending_orders)
        
        with col4:
            st.metric("Cancelled", cancelled_orders)
        
        with col5:
            st.metric("Delivery Rate", f"{delivery_rate}%")
        
        # Progress bar
        st.progress(delivery_rate / 100)

        # ----------- PIE CHART OF ORDER STATUS -----------
        if "Status" in orders_df.columns:
            # Clean NaN values
            status_counts = orders_df["Status"].fillna("Unknown").value_counts()
            status_labels = status_counts.index.tolist()
            status_values = status_counts.values.tolist()
            # Calculate percentages
            status_percentages = [v / sum(status_values) * 100 for v in status_values]
            # Compose labels with both status and count
            status_labels_with_counts = [
                f"{label} ({count})" for label, count in zip(status_labels, status_values)
            ]

            # Define color mapping for statuses
            status_color_map = {
                "In Process": "#FFD600",  # yellow
                "In route from warehouse": "#FF9800",  # orange
                "Delivered": "#4CAF50",  # green
                "Cancelled": "#F44336",  # red
                "Received": "#2196F3",  # blue
            }
            # Assign colors to each status in the order of status_labels
            # If a status is not in the map, assign a default color (gray)
            default_color = "#BDBDBD"
            # Extract the status (without count) for color mapping
            status_labels_raw = status_labels  # these are the raw status names
            color_list = [status_color_map.get(status, default_color) for status in status_labels_raw]

            # Create the pie chart with Plotly
            fig = px.pie(
                names=status_labels_with_counts,
                values=status_values,
                title="Order Status Distribution",
                hole=0.3,
                color_discrete_sequence=color_list
            )
            fig.update_traces(
                textinfo='percent+label',
                hovertemplate='%{label}: %{value} (%{percent})<extra></extra>'
            )
            st.subheader("Order Statuses")
            st.plotly_chart(fig, use_container_width=True)
        # ----------------------------------------------------------

    # Button to refresh data
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()
    
    # Dashboard sections
    # tab1, tab2, tab3 = st.tabs(["Latest Orders", "Inventory", "Checklist Progress"])
    tab1, tab2 = st.tabs(["Latest Orders", "Inventory"])
    
    with tab1:
        if not orders_df.empty:
            # Check if Date and Hour columns exist before sorting
            if "Date" in orders_df.columns and "Hour" in orders_df.columns:
                # Convert Date and Hour to datetime for proper sorting
                try:
                    # Create a temporary column for sorting
                    orders_df['datetime_sort'] = pd.to_datetime(
                        orders_df['Date'] + ' ' + orders_df['Hour'], 
                        errors='coerce',
                        format='%m/%d/%Y %I:%M:%S %p'
                    )
                    
                    # Sort by the datetime column
                    last_orders = orders_df.sort_values(by='datetime_sort', ascending=False).head(10)
                    
                    # Drop the temporary column
                    last_orders = last_orders.drop(columns=['datetime_sort'])
                except Exception as e:
                    st.warning(f"Error converting dates for sorting: {e}")
                    # Fallback to original sorting method
                    last_orders = orders_df.sort_values(by=["Date", "Hour"], ascending=False).head(10)
            else:
                sort_columns = []
                if "Date" in orders_df.columns:
                    sort_columns.append("Date")
                if "Hour" in orders_df.columns:
                    sort_columns.append("Hour")
                
                # Filter and display the 10 latest orders
                if sort_columns:
                    last_orders = orders_df.sort_values(by=sort_columns, ascending=False).head(10)
                else:
                    last_orders = orders_df.head(10)
                    st.warning("Date/Hour columns not found. Orders may not be sorted correctly.")
            
            # Columns to display - check if they exist
            available_columns = orders_df.columns.tolist()
            display_columns = [col for col in ["Booth #", "Section", "Exhibitor Name", "Item", "Color", 
                               "Quantity", "Date", "Hour", "Status", "User"] if col in available_columns]
            
            if display_columns:
                st.dataframe(
                    last_orders[display_columns], 
                    use_container_width=True
                )
            else:
                st.error("No valid columns found to display orders.")
        else:
            st.info("No order data available.")
    
    with tab2:
        if not inventory_df.empty:
            # Filter to display only relevant columns that exist
            inventory_columns = [col for col in ["Items", "Load List", "Pull List", 
                                 "Starting Quantity", "Ordered items", "Damaged Items", 
                                 "Available Quantity", "Requested to the Warehouse", 
                                 "Requested Date and Time"] if col in inventory_df.columns]
            
            if inventory_columns:
                # Display inventory
                st.dataframe(inventory_df[inventory_columns], use_container_width=True)
                
                # Select items with low available quantity if column exists
                if "Available Quantity" in inventory_df.columns:
                    try:
                        # Convert to numeric if possible
                        inventory_df["Available Quantity"] = pd.to_numeric(inventory_df["Available Quantity"], errors="coerce")
                        low_inventory = inventory_df[inventory_df["Available Quantity"] < 10]
                        
                        if not low_inventory.empty:
                            st.subheader("⚠️ Low quantity items")
                            st.dataframe(
                                low_inventory[inventory_columns],
                                use_container_width=True,
                                hide_index=True
                            )
                    except Exception as e:
                        st.warning(f"Could not process inventory quantities: {e}")
            else:
                st.error("No valid columns found to display inventory.")
        else:
            st.info("No inventory data available.")
    
    # with tab3:
    #     # Check if checklist_df is empty or not
    #     if not checklist_df.empty:
    #         # Check if Status column exists
    #         if "Status" in checklist_df.columns:
    #             # Calculate checklist progress
    #             total_items = len(checklist_df)
    #             completed_items = len(checklist_df[checklist_df["Status"] == True])
    #             completion_percentage = int((completed_items / total_items * 100) if total_items > 0 else 0)
                
    #             col1, col2, col3 = st.columns(3)
                
    #             with col1:
    #                 st.metric("Total items", total_items)
                
    #             with col2:
    #                 st.metric("Checked items", completed_items)
                
    #             with col3:
    #                 st.metric("Progress", f"{completion_percentage}%")
                
    #             # Progress bar
    #             st.progress(completion_percentage / 100)
    #         else:
    #             st.warning("Status column not found in checklist data.")
            
    #         # Display by section
    #         try:
    #             # Get list of sections
    #             sections = gs_manager.get_worksheets("19ksIroX0i3WY3XmSGXQpdS1RzjpYKhqMhwK1tYiKZZA")
    #             sections = [s for s in sections if s.startswith("Section") or s == "No Section"]
                
    #             # Progress data by section
    #             section_progress = []
                
    #             for section in sections:
    #                 section_df = gs_manager.get_data("19ksIroX0i3WY3XmSGXQpdS1RzjpYKhqMhwK1tYiKZZA", section)
    #                 if not section_df.empty:
    #                     total = len(section_df)
    #                     # Check if Status column exists
    #                     if "Status" in section_df.columns:
    #                         completed = len(section_df[section_df["Status"] == True])
    #                     else:
    #                         completed = 0
    #                     progress = int((completed / total * 100) if total > 0 else 0)
                        
    #                     section_progress.append({
    #                         "Section": section,
    #                         "Total": total,
    #                         "Completed": completed,
    #                         "Progress": progress
    #                     })
                
    #             # Create DataFrame for display
    #             progress_df = pd.DataFrame(section_progress)
                
    #             # Display DataFrame
    #             st.subheader("Progress by section")
    #             st.dataframe(
    #                 progress_df,
    #                 use_container_width=True,
    #                 hide_index=True
    #             )
    #         except Exception as e:
    #             st.error(f"Error loading section data: {e}")
    #     else:
    #         st.info("No checklist data available.")
            
    # Links to other pages
    st.divider()
    
    st.subheader("Quick Access")
    
    # col1, col2 = st.columns(2)
    (col1,) = st.columns(1)
    
    with col1:
        st.page_link("pages/1_Orders.py", label="📦 Order Management", icon="🔗")
        st.caption("Track and manage orders by booth")
    
    # with col2:
    #     st.page_link("pages/2_Checklists.py", label="✅ Booth Checklist", icon="🔗")
    #     st.caption("Check booths progress status")
