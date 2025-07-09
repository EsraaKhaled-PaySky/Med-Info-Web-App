from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import mongo, bcrypt, mail
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import secrets
import os
from flask_mail import Message
from flask import session


# ✅ DEFINE BLUEPRINT
main = Blueprint('main', __name__)

# ✅ HOME
@main.route('/')
def home():
    return render_template('home.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        if not all([first_name, last_name, username, email, password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template('signup.html')
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('signup.html')
        
        # Check if username already exists
        if mongo.db.users.find_one({'username': username}):
            flash("Username already exists. Please choose a different one.", "error")
            return render_template('signup.html')
        
        # Check if email already exists
        if mongo.db.users.find_one({'email': email}):
            flash("Email already registered. Please use a different email.", "error")
            return render_template('signup.html')
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create user document
        user_data = {
            'firstName': first_name,
            'lastName': last_name,
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow()
        }
        
        try:
            # Insert user into database
            mongo.db.users.insert_one(user_data)
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('main.login'))
        except Exception as e:
            flash("An error occurred during signup. Please try again.", "error")
            return render_template('signup.html')
    
    return render_template('signup.html')

# ✅ LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            user_obj = User(user)
            login_user(user_obj)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        flash("Please log in to access your profile.", "error")
        return redirect(url_for('main.login'))

    try:
        # GET request - fetch user data
        if request.method == 'GET':
            user_data = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
            if not user_data:
                flash("User not found.", "error")
                return redirect(url_for('main.login'))
            
            # Calculate profile completion
            required_fields = ['firstName', 'lastName', 'email', 'username']
            optional_fields = ['bio', 'phone', 'location']
            
            completed_required = sum(1 for field in required_fields if user_data.get(field))
            completed_optional = sum(1 for field in optional_fields if user_data.get(field))
            
            # Required fields are worth 60%, optional fields 40%
            required_score = (completed_required / len(required_fields)) * 60
            optional_score = (completed_optional / len(optional_fields)) * 40
            profile_completion = int(required_score + optional_score)
            
            user_stats = {
                'member_since': user_data.get('created_at', datetime.utcnow()).strftime('%B %Y'),
                'last_updated': user_data.get('updated_at', user_data.get('created_at', datetime.utcnow())).strftime('%B %d, %Y'),
                'total_searches': mongo.db.search_history.count_documents({'user_id': ObjectId(current_user.id)}) if 'search_history' in mongo.db.list_collection_names() else 0,
                'profile_completion': profile_completion
            }
            
            return render_template('profile.html', user=user_data, stats=user_stats)
        
        # POST request - update profile
        elif request.method == 'POST':
            # Get form data
            first_name = request.form.get('firstName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            email = request.form.get('email', '').strip()
            bio = request.form.get('bio', '').strip()
            phone = request.form.get('phone', '').strip()
            location = request.form.get('location', '').strip()
            
            # Basic validation
            if not all([first_name, last_name, email]):
                flash("First name, last name, and email are required.", "error")
                return redirect(url_for('main.profile'))
            
            # Check if email is being changed and if it already exists
            if email != current_user.email:
                existing_email = mongo.db.users.find_one({
                    'email': email,
                    '_id': {'$ne': ObjectId(current_user.id)}
                })
                if existing_email:
                    flash("This email is already registered to another account.", "error")
                    return redirect(url_for('main.profile'))
            
            # Update user data
            update_data = {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'bio': bio if bio else None,
                'phone': phone if phone else None,
                'location': location if location else None,
                'updated_at': datetime.utcnow()
            }
            
            # Update user in database
            result = mongo.db.users.update_one(
                {'_id': ObjectId(current_user.id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                flash("Profile updated successfully!", "success")
            else:
                flash("No changes were made to your profile.", "info")
            
            return redirect(url_for('main.profile'))
    
    except Exception as e:
        print(f"Error in profile route: {str(e)}")  # Log the error for debugging
        flash("An error occurred while processing your request. Please try again.", "error")
        return redirect(url_for('main.dashboard'))

def calculate_profile_completion(user_data):
    """Calculate profile completion percentage"""
    required_fields = ['firstName', 'lastName', 'email', 'username']
    optional_fields = ['bio', 'phone', 'location']
    
    completed_required = sum(1 for field in required_fields if user_data.get(field))
    completed_optional = sum(1 for field in optional_fields if user_data.get(field))
    
    # Required fields are worth 60%, optional fields 40%
    required_score = (completed_required / len(required_fields)) * 60
    optional_score = (completed_optional / len(optional_fields)) * 40
    
    return int(required_score + optional_score)

@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Handle account deletion"""
    password = request.form.get('password')
    
    if not password:
        flash("Password is required to delete your account.", "error")
        return redirect(url_for('main.profile'))
    
    try:
        # Verify password
        user_data = mongo.db.users.find_one({'username': session['username']})
        if not user_data or not bcrypt.check_password_hash(user_data['password'], password):
            flash("Incorrect password. Account deletion failed.", "error")
            return redirect(url_for('main.profile'))
        
        # Delete user data
        mongo.db.users.delete_one({'username': session['username']})
        
        # Optional: Delete related user data
        if 'search_history' in mongo.db.list_collection_names():
            mongo.db.search_history.delete_many({'username': session['username']})
        
        # Clear session
        session.clear()
        
        flash("Your account has been successfully deleted.", "success")
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash("An error occurred while deleting your account. Please try again.", "error")
        return redirect(url_for('main.profile'))

# ✅ DASHBOARD (same as your medicine search)
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    medicine = None
    searched = False
    if request.method == 'POST':
        searched = True
        query = request.form['medicine']
        medicine = mongo.db.medicines.find_one({"name": {"$regex": query, "$options": "i"}})
    return render_template('dashboard.html', user=current_user, medicine=medicine, searched=searched)

# ✅ LOGOUT
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))



@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = mongo.db.users.find_one({'email': email})
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            
            # Store token in database
            mongo.db.users.update_one(
                {'email': email},
                {
                    '$set': {
                        'reset_token': token,
                        'reset_expires': expires
                    }
                }
            )
            
            # Send reset email
            try:
                send_reset_email(email, token)
                flash('Password reset instructions have been sent to your email.', 'info')
            except Exception as e:
                flash('Error sending email. Please try again later.', 'error')
                print(f"Email error: {str(e)}")
        else:
            # Don't reveal if email exists or not for security
            flash('If that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html')

# ✅ PASSWORD RESET FORM
@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Find user with valid token
    user = mongo.db.users.find_one({
        'reset_token': token,
        'reset_expires': {'$gt': datetime.utcnow()}
    })
    
    if not user:
        flash('Invalid or expired password reset token.', 'error')
        return redirect(url_for('main.forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Hash new password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Update password and remove reset token
        mongo.db.users.update_one(
            {'_id': user['_id']},
            {
                '$set': {'password': hashed_password},
                '$unset': {'reset_token': '', 'reset_expires': ''}
            }
        )
        
        flash('Your password has been reset successfully. Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', token=token)

# ✅ CHANGE PASSWORD (for logged-in users)
@main.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Get current user from database
        user = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
        
        if not bcrypt.check_password_hash(user['password'], current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('change_password.html')
        
        # Hash new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update password
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': {'password': hashed_password}}
        )
        
        flash('Password changed successfully.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html')

def send_reset_email(email, token):
    """Send password reset email"""
    reset_url = url_for('main.reset_password', token=token, _external=True)
    
    msg = Message(
        subject='Password Reset Request - MedInfo Pro',
        sender=os.environ.get('MAIL_DEFAULT_SENDER'),
        recipients=[email]
    )
    
    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #319795; color: white; padding: 20px; text-align: center;">
            <h2>Password Reset Request</h2>
        </div>
        
        <div style="padding: 20px; background: #f9f9f9;">
            <p>Hello,</p>
            
            <p>You have requested to reset your password for your MedInfo Pro account.</p>
            
            <p>Click the button below to reset your password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: #319795; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_url}</p>
            
            <p><strong>This link will expire in 1 hour.</strong></p>
            
            <p>If you did not request this password reset, please ignore this email.</p>
            
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #666; font-size: 12px;">
                This is an automated message from MedInfo Pro. Please do not reply to this email.
            </p>
        </div>
    </div>
    """
    
    mail.send(msg)
