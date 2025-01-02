import streamlit as st
from main import run_business_builder
from translations import UI_TRANSLATIONS
from utils.database import Database

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
        .stRadio > label {
            min-width: 150px;
        }
        .stTextArea > label {
            min-width: 200px;
        }
        .stButton {
            text-align: left;
        }
        /* Mobile-friendly adjustments */
        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .stRadio > label {
                min-width: 100px;
            }
            .stTextArea > label {
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
        }
    </style>
""", unsafe_allow_html=True)

def secure_main():
    """Main function with authentication"""
    # Initialize database connection
    db = Database()
    
    # Initialize language in session state if not present
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    
    # Get language code from session state
    selected_language = st.session_state.get('selected_language', 'English')
    lang_code = "nl" if selected_language == "Dutch" else "en"
    texts = UI_TRANSLATIONS[lang_code]

    # Create a container for the language selection
    with st.container():
        # Language selection (before login to allow language selection on login screen)
        st.session_state.selected_language = st.radio(
            texts["select_language"],
            options=["English", "Dutch"],
            horizontal=True,
            index=0 if st.session_state.selected_language == "English" else 1
        )
    
    # Check if user is not logged in
    if not st.session_state.get("authentication_status"):
        st.title(texts["title"])
        
        # Login form aligned to the left
        with st.container():
            with st.form("login_form", clear_on_submit=True):
                username = st.text_input(texts["username_label"]).lower()
                password = st.text_input(texts["password_label"], type="password")
                submitted = st.form_submit_button(texts["login_button"])
                
                if submitted:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state['authentication_status'] = True
                        st.session_state['username'] = user['username']
                        st.session_state['name'] = user['name']
                        st.session_state['is_admin'] = user.get('is_admin', False)
                        st.rerun()
                    else:
                        st.error(texts["invalid_credentials"])
        return
    
    # Get user information
    user = db.get_user(st.session_state["username"])
    if not user:
        st.error(texts["user_not_found"])
        st.session_state['authentication_status'] = None
        st.rerun()

    # Sidebar with logout and navigation
    with st.sidebar:
        st.write(f'{texts["welcome"]} *{st.session_state["name"]}*')
        
        # Language selection
        st.selectbox(
            texts["select_language"],
            ["English", "Dutch"],
            key="selected_language",
            on_change=lambda: st.rerun()
        )
        
        st.divider()
        
        # Navigation menu
        st.markdown(f"### {texts['navigation']}")
        st.page_link("pages/02_report_history.py", label=texts["report_history"])
        
        # Admin menu
        if st.session_state.get("is_admin"):
            st.divider()
            st.markdown(f"### {texts['admin_menu']}")
            st.page_link("pages/01_user_management.py", label=texts["user_management"])
        
        st.divider()
        
        # Logout button
        if st.button(texts["logout"]):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Credits display
        credits_placeholder = st.empty()
        credits_placeholder.write(f"**{texts['credits_remaining']}:** {user['credits']}")

    # Main app content
    with st.container():
        st.title(texts["title"])

        # Business idea input
        business_idea = st.text_area(texts["business_idea_label"], height=150)
        
        if st.button(texts["analyze_button"]):
            if not business_idea:
                st.error(texts["please_enter_idea"])
                return
                
            if user['credits'] <= 0:
                st.error(texts["no_credits"])
                return
                
            try:
                # Run the analysis
                txt_file, pdf_file = run_business_builder(
                    business_idea,
                    lang_code,
                    st.session_state["username"]  # Pass username for saving to MongoDB
                )
                
                # Update credits
                db.update_credits(st.session_state["username"], user['credits'] - 1)
                credits_placeholder.write(f"**{texts['credits_remaining']}:** {user['credits'] - 1}")
                
                # Offer downloads
                st.download_button(
                    label=texts["download_report"],
                    data=open(pdf_file, "rb"),
                    file_name=pdf_file,
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"{texts['error_occurred']}: {str(e)}")

if __name__ == "__main__":
    secure_main() 