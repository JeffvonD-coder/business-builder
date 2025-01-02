import streamlit as st
from utils.database import Database
from translations import UI_TRANSLATIONS

# Configure the page layout
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Add custom CSS to align content to the left and make it mobile-friendly
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }
        .stForm > label {
            min-width: 150px;
        }
        .stButton {
            text-align: left;
        }
        .stExpander {
            max-width: 100%;
        }
        /* Mobile-friendly adjustments */
        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .stForm > label {
                min-width: 100px;
            }
            /* Make text more readable on small screens */
            .streamlit-expanderHeader {
                font-size: 1rem !important;
            }
            p, .stMarkdown {
                font-size: 0.9rem !important;
            }
            h1 {
                font-size: 1.5rem !important;
            }
            h2 {
                font-size: 1.3rem !important;
            }
            h3 {
                font-size: 1.1rem !important;
            }
            /* Stack columns on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
            /* Add spacing between stacked columns */
            [data-testid="column"]:not(:first-child) {
                margin-top: 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

def user_management():
    """User management page for admin users"""
    
    # Get language code from session state or default to English
    selected_language = st.session_state.get('selected_language', 'English')
    lang_code = "nl" if selected_language == "Dutch" else "en"
    texts = UI_TRANSLATIONS[lang_code]
    
    # Check if user is logged in and is admin
    if not st.session_state.get("authentication_status"):
        st.error(texts["login_required"])
        st.stop()
    elif not st.session_state.get("is_admin"):
        st.error(texts["unauthorized"])
        st.stop()

    st.title(texts["user_management_title"])
    
    # Initialize database connection
    db = Database()
    
    # Create two columns for the layout (will stack on mobile)
    col1, col2 = st.columns([1, 2], gap="large")
    
    # Add new user section in the first column
    with col1:
        st.header(texts["add_user"])
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input(texts["username_label"]).lower()
            new_password = st.text_input(texts["password_label"], type="password")
            new_name = st.text_input(texts["name_label"])
            new_email = st.text_input(texts["email_label"])
            new_credits = st.number_input(texts["initial_credits"], min_value=0, value=3)
            new_is_admin = st.checkbox(texts["is_admin"])
            
            if st.form_submit_button(texts["add_user_button"]):
                if new_username and new_password and new_name and new_email:
                    db.create_user(new_username, new_password, new_email, new_name, new_credits, new_is_admin)
                    st.success(texts["user_added"])
                    st.rerun()
                else:
                    st.error(texts["all_fields_required"])
    
    # User list and management in the second column
    with col2:
        st.header(texts["user_list"])
        users = db.list_users()
        
        for user in users:
            with st.expander(f"{user['name']} ({user['username']})"):
                with st.form(f"edit_user_{user['username']}", clear_on_submit=False):
                    name = st.text_input(texts["name_label"], value=user['name'])
                    email = st.text_input(texts["email_label"], value=user.get('email', ''))
                    credits = st.number_input(texts["credits_label"], value=user['credits'])
                    is_admin = st.checkbox(texts["admin_label"], value=user.get('is_admin', False))
                    
                    # Use full width for buttons on mobile
                    save_col, delete_col = st.columns(2)
                    with save_col:
                        if st.form_submit_button(texts["save_changes"], use_container_width=True):
                            updates = {
                                "name": name,
                                "email": email,
                                "credits": credits,
                                "is_admin": is_admin
                            }
                            db.update_user(user['username'], updates)
                            st.success(texts["user_updated"])
                            st.rerun()
                    
                    with delete_col:
                        if st.form_submit_button(texts["delete_user"], use_container_width=True):
                            if st.session_state["username"] != user["username"]:
                                if st.button(texts["confirm_delete"]):
                                    db.delete_user(user['username'])
                                    st.success(texts["user_deleted"])
                                    st.rerun()

if __name__ == "__main__":
    user_management() 