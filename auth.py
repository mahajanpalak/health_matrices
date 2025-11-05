# auth.py
import streamlit as st
import database as db

def check_auth():
    """Check if user is logged in"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    return st.session_state.logged_in

def show_login_signup():
    """Show login and signup forms"""
    
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.8rem;
            color: #ffffff;
            background: linear-gradient(135deg, #131a2f 0%, #264493 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🏥 Health Matrices Pro</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h3>Your Personal Health Companion</h3>
        <p>Track your fitness, plan your meals, and achieve your health goals</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 **Login**", "📝 **Sign Up**"])
    
    with tab1:
        st.header("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_btn:
                if username and password:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.session_state.logged_in = True
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("⚠️ Please fill all fields")
    
    with tab2:
        st.header("Create New Account")
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username", placeholder="Enter a username")
            new_password = st.text_input("Choose Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            email = st.text_input("Email (optional)", placeholder="your.email@example.com")
            signup_btn = st.form_submit_button("🎯 Create Account", use_container_width=True)
            
            if signup_btn:
                if new_username and new_password and confirm_password:
                    if len(new_username) < 3:
                        st.error("❌ Username must be at least 3 characters long")
                    elif len(new_password) < 4:
                        st.error("❌ Password must be at least 4 characters long")
                    elif new_password == confirm_password:
                        if db.create_user(new_username, new_password, email):
                            st.success("✅ Account created successfully! Please login.")
                        else:
                            st.error("❌ Username already exists")
                    else:
                        st.error("❌ Passwords don't match")
                else:
                    st.error("⚠️ Please fill all required fields")

def logout():
    """Logout the current user"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None