import streamlit as st
import time

def handle_login(users_collection):
    """
    Renders the login form and handles authentication logic.
    Returns:
        True if login is successful (triggers rerun), False otherwise.
    """
    # Create 3 columns to center the form nicely
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Admin Access")
        st.info("Please sign in to manage family records.")
        
        with st.form("login_form"):
            email = st.text_input("Email ID")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login", type="primary")
            
            if submit_login:
                if not email or not password:
                    st.warning("Please enter both email and password.")
                    return False

                # Check against MongoDB
                user = users_collection.find_one({"email": email, "password": password})
                
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = user.get('role')
                    st.session_state['user_name'] = user.get('slug')
                    
                    # ADD THIS LINE:
                    st.session_state['just_logged_in'] = True 
                    # (This tells app.py to force 'admin' tab on next load)

                    st.success("Login Successful!")
                    time.sleep(0.5)
                    st.rerun()
                    return True
                else:
                    st.error("Invalid Email or Password")
                    return False
    return False

def handle_logout():
    """
    Clears session state and logs the user out.
    """
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['user_name'] = None
    st.rerun()
