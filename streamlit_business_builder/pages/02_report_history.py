import streamlit as st
from utils.database import Database
from translations import UI_TRANSLATIONS
import io
import zipfile
from datetime import datetime

# Configure the page layout
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def format_datetime(dt):
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M")

def create_zip_file(reports, selected_format="pdf"):
    """Create a zip file containing selected reports"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for report in reports:
            if selected_format == "pdf":
                data = report["pdf_report"]
                ext = "pdf"
            else:
                data = report["txt_report"]
                ext = "txt"
            
            # Create filename using idea_id and timestamp
            filename = f"report_{report['idea_id']}.{ext}"
            zip_file.writestr(filename, data)
    
    return zip_buffer.getvalue()

def report_history():
    """Report history page for viewing past business ideas and reports"""
    
    # Get language code from session state
    selected_language = st.session_state.get('selected_language', 'English')
    lang_code = "nl" if selected_language == "Dutch" else "en"
    texts = UI_TRANSLATIONS[lang_code]
    
    # Check if user is logged in
    if not st.session_state.get("authentication_status"):
        st.error(texts["login_required"])
        st.stop()

    st.title(texts["report_history_title"])
    
    # Initialize database connection
    db = Database()
    
    # Get user's role
    is_admin = st.session_state.get("is_admin", False)
    
    # Create tabs for different views
    if is_admin:
        tab1, tab2 = st.tabs([texts["all_reports"], texts["batch_download"]])
    else:
        tab1, tab2 = st.tabs([texts["my_reports"], texts["batch_download"]])

    with tab1:
        # Get business ideas
        if is_admin:
            ideas = db.get_all_ideas()
            st.subheader(texts["all_users_reports"])
        else:
            ideas = db.get_user_ideas(st.session_state["username"])
            st.subheader(texts["your_reports"])

        # Display ideas in a table
        if ideas:
            for idea in ideas:
                with st.expander(f"{format_datetime(idea['created_at'])} - {idea['idea_text'][:100]}..."):
                    st.write(f"**{texts['business_idea']}:**")
                    st.write(idea['idea_text'])
                    st.write(f"**{texts['created_by']}:** {idea['username']}" if is_admin else "")
                    st.write(f"**{texts['created_at']}:** {format_datetime(idea['created_at'])}")
                    
                    # Get reports for this idea
                    reports = db.get_idea_reports(idea['idea_id'])
                    if reports:
                        col1, col2 = st.columns(2)
                        with col1:
                            if reports.get('pdf_report'):
                                st.download_button(
                                    texts["download_pdf"],
                                    data=reports['pdf_report'],
                                    file_name=f"report_{idea['idea_id']}.pdf",
                                    mime="application/pdf"
                                )
                        with col2:
                            if reports.get('txt_report'):
                                st.download_button(
                                    texts["download_txt"],
                                    data=reports['txt_report'],
                                    file_name=f"report_{idea['idea_id']}.txt",
                                    mime="text/plain"
                                )
        else:
            st.info(texts["no_reports"])

    with tab2:
        st.subheader(texts["batch_download_title"])
        
        # Get ideas for batch download
        if is_admin:
            batch_ideas = db.get_all_ideas()
        else:
            batch_ideas = db.get_user_ideas(st.session_state["username"])

        if batch_ideas:
            # Create selection interface
            selected_ideas = []
            for idea in batch_ideas:
                if st.checkbox(
                    f"{format_datetime(idea['created_at'])} - {idea['idea_text'][:100]}...",
                    key=f"select_{idea['idea_id']}"
                ):
                    selected_ideas.append(idea['idea_id'])

            if selected_ideas:
                # Format selection
                format_col1, format_col2 = st.columns(2)
                with format_col1:
                    selected_format = st.radio(
                        texts["select_format"],
                        ["PDF", "TXT"],
                        horizontal=True
                    )
                
                # Download button
                reports = db.get_multiple_reports(selected_ideas)
                if reports:
                    zip_data = create_zip_file(reports, selected_format.lower())
                    st.download_button(
                        texts["download_selected"],
                        data=zip_data,
                        file_name=f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )
        else:
            st.info(texts["no_reports"])

if __name__ == "__main__":
    report_history() 