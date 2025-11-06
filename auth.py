# auth.py
import streamlit as st
import database as db
import re

class PasswordValidationError(Exception):
    """Custom exception for invalid passwords."""
    pass

def validate_password(password):
    """
    Validates that a password:
    - Has at least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one number
    - Contains at least one special character
    Raises PasswordValidationError if any rule is violated.
    """
    if len(password) < 8:
        raise PasswordValidationError("Password must be at least 8 characters long.")
    
    if not re.search(r"[A-Z]", password):
        raise PasswordValidationError("Password must contain at least one uppercase letter.")
    
    if not re.search(r"\d", password):
        raise PasswordValidationError("Password must contain at least one numeric value.")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordValidationError("Password must contain at least one special character.")
    
    # If all conditions are met
    return True

def validate_email_format(email):
    """
    Strict email validation that only accepts legitimate providers
    """
    if not email:
        return True, ""
    
    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "❌ Invalid email format. Please check your email address."
    
    domain = email.split('@')[1].lower()
    
    # List of approved email providers
    APPROVED_DOMAINS = {
        # Google
        'gmail.com', 'googlemail.com',
        
        # Yahoo
        'yahoo.com', 'yahoo.co.in', 'yahoo.co.uk', 'ymail.com', 'rocketmail.com',
        
        # Microsoft
        'outlook.com', 'hotmail.com', 'live.com', 'msn.com',
        
        # Apple
        'icloud.com', 'me.com', 'mac.com',
        
        # Other major providers
        'aol.com', 'protonmail.com', 'proton.me',
        'zoho.com', 'zohomail.com', 'fastmail.com',
        'tutanota.com', 'tuta.io', 'mail.com',
        'gmx.com', 'gmx.net', 'gmx.us',
        
        # Regional providers
        'rediffmail.com', 'mail.ru', 'yandex.com', 'yandex.ru',
        'qq.com', 'naver.com', 'daum.net', 'web.de'
    }
    
    # Check against approved list
    if domain in APPROVED_DOMAINS:
        return True, ""
    
    # Allow company/organization emails with verification
    domain_parts = domain.split('.')
    if len(domain_parts) == 2:
        tld = domain_parts[1]
        company = domain_parts[0]
        
        # Must be proper TLD and reasonable company name
        if (tld in {'com', 'org', 'net', 'edu', 'gov', 'co', 'io'} and
            len(company) >= 3 and 
            company.isalnum()):
            
            st.warning(f"🔒 Using {domain} - organization emails are accepted")
            return True, ""
    
    # Show helpful error message
    st.error(f"""
❌ **{domain}** is not a recognized email provider.

Please use:
• **Gmail** (@gmail.com)
• **Yahoo** (@yahoo.com) 
• **Outlook/Hotmail** (@outlook.com, @hotmail.com)
• **iCloud** (@icloud.com)
• **ProtonMail** (@protonmail.com)
• Or your company/organization email
""")
    return False, "Unrecognized email provider"

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
        .password-requirements {
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #00e0ff;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🏥 Health Matrices</h1>', unsafe_allow_html=True)
    
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
        
        # Password requirements info
        st.markdown("""
        <div class="password-requirements">
            <h4>🔒 Password Requirements:</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>At least 8 characters long</li>
                <li>Contains at least one uppercase letter (A-Z)</li>
                <li>Contains at least one number (0-9)</li>
                <li>Contains at least one special character (!@#$%^&* etc.)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username", placeholder="Enter a username")
            new_password = st.text_input("Choose Password", type="password", placeholder="Create a strong password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            email = st.text_input("Email (optional)", placeholder="your.email@example.com")
            signup_btn = st.form_submit_button("🎯 Create Account", use_container_width=True)
            
            if signup_btn:
                # Validate inputs
                if not new_username or not new_password or not confirm_password:
                    st.error("⚠️ Please fill all required fields")
                elif len(new_username) < 3:
                    st.error("❌ Username must be at least 3 characters long")
                else:
                    try:
                        # Validate password strength
                        validate_password(new_password)
                        
                        # Check if passwords match
                        if new_password != confirm_password:
                            st.error("❌ Passwords don't match")
                        else:
                            # Validate email format if provided
                            if email:  # Email is optional, but if provided, validate it
                                is_valid, email_error = validate_email_format(email)
                                if not is_valid:
                                    st.error(email_error)
                                else:
                                    # All validations passed, create user
                                    success = db.create_user(new_username, new_password, email)
                                    if success:
                                        st.success("✅ Account created successfully! Please login.")
                                    else:
                                        st.error("❌ Username already exists")
                            else:
                                # No email provided, create user without email
                                success = db.create_user(new_username, new_password, "")
                                if success:
                                    st.success("✅ Account created successfully! Please login.")
                                else:
                                    st.error("❌ Username already exists")
                    
                    except PasswordValidationError as e:
                        st.error(f"❌ {str(e)}")

def logout():
    """Logout the current user"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None