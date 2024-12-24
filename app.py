from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from DB_connection import ConnectDatabase

app = Flask(__name__)
app.secret_key = 'OptiVision_Tameer_Redan'  

db = ConnectDatabase()

@app.route('/')
def login():
    if 'user_name' in session:
        session.clear()  # Clear any existing session
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/login', methods=['POST'])
def login_process():
    email = request.form['email']
    password = request.form['password']
    
    result = db.login(email, password)
    
    if result == "True details":
        user_id = db.get_user_id(email)
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = db.get_user_name(email)
        return redirect(url_for('dashboard'))
    elif result == "Email does not exist":
        flash('Email does not exist', 'error')
    else:
        flash('Incorrect password', 'error')
    
    return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_process():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('register'))
    
    result = db.register(name, email, password)
    
    if result == "success":
        flash('Successfully Registered!', 'success')
        return redirect(url_for('login'))
    elif result == "Email already exists":
        flash('Email already exists', 'error')
    else:
        flash(f'Registration failed: {result}', 'error')
    
    return redirect(url_for('register'))

@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_name = session['user_name']
    
    total_tests = db.get_total_tests_count(user_id)
    
    response = make_response(render_template('dashboard.html', 
        user_name=user_name, 
        total_tests=total_tests
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/calibration')
def calibration():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    response = make_response(render_template('calibration.html', user_name=session['user_name']))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/allTests')
def allTests():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    # Get all test counts in one query
    test_counts = db.test_count(user_id)

    user_name = session['user_name']
    response = make_response(
        render_template(
            'allTests.html', 
            user_name=user_name,
            visual_acuity=test_counts.get('visual_acuity', 0),
            color_vision=test_counts.get('color_vision', 0),
            contrast_vision=test_counts.get('contrast_vision', 0),
            blur_check=test_counts.get('blur_check', 0),
            watch_dot=test_counts.get('watch_dot', 0)
        )
    )
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response


@app.route('/VisualAcuityTest')
def VisualAcuityTest():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    user_name = session['user_name']
    response = make_response(render_template('VisualAcuityTest.html', user_name=user_name))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/ColorVisionTest')
def ColorVisionTest():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    user_name = session['user_name']
    response = make_response(render_template('ColorVisionTest.html', user_name=user_name))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/ContrastVisionTest')
def ContrastVisionTest():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    user_name = session['user_name']
    response = make_response(render_template('ContrastVisionTest.html', user_name=user_name))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/BlurCheckTest')
def BlurCheckTest():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    user_name = session['user_name']
    response = make_response(render_template('BlurCheckTest.html', user_name=user_name))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/WatchTheDotTest')
def WatchTheDotTest():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    user_name = session['user_name']
    response = make_response(render_template('WatchTheDotTest.html', user_name=user_name))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/Visual_Acuity_save_results', methods=['POST'])
def Visual_Acuity_save_results():
    data = request.get_json()
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    success = db.VisualAcuity_save_test_result(
        user_id, 
        data.get('rightEyeLevel'),
        data.get('rightEyeIncorrect'),
        data.get('leftEyeLevel'),
        data.get('leftEyeIncorrect'),
        data.get('feedBack')
    )
    
    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to save results'}), 500

@app.route('/Color_Vision_save_results', methods=['POST'])
def Color_Vision_save_results():
    data = request.get_json()
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    success = db.ColorVision_save_test_result(
        user_id,
        data.get('score'),
        data.get('incorrectanswers'),
        data.get('feedBack')
    )
    
    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to save results'}), 500

@app.route('/Contrast_Vision_save_results', methods=['POST'])
def Contrast_Vision_save_results():
    try:
        data = request.get_json()
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401
        
        user_id = session['user_id']
        success = db.ContrastVision_save_test_result(
            user_id,
            data.get('score'),
            data.get('incorrectAnswers'),
            data.get('feedback')
        )
        
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save to database'}), 500
            
    except Exception as e:
        print(f"Error in Contrast_Vision_save_results: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/Blur_Check_save_results', methods=['POST'])
def Blur_Check_save_results():
    data = request.get_json()
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    success = db.BlurCheck_save_test_result(
        user_id,
        data.get('score'),
        data.get('incorrectAnswers'),
        data.get('feedback')
    )
    
    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to save results'}), 500

@app.route('/Watch_Dot_save_results', methods=['POST'])
def Watch_Dot_save_results():
    data = request.get_json()
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_id = session['user_id']
    success = db.WatchDot_save_test_result(
        user_id,
        data.get('score'),
        data.get('incorrectAnswers'),
        data.get('feedback')
    )
    
    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to save results'}), 500

@app.route('/TestsSection')
def TestsSection():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    response = make_response(render_template('TestsSection.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/reports')
def reports():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    response = make_response(render_template('Reports.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/settings')
def settings():
    if 'user_name' not in session:
        return redirect(url_for('login')) 
    user_email = session.get('user_email', 'Not provided')  # Default value
    user_name = session.get('user_name', 'Guest')
    response = make_response(render_template('Settings.html',user_name=user_name, user_email=user_email))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    username = request.form.get('username')
    email = request.form.get('email')
    
    try:
        result = db.update_profile(user_id, username, email)
        if result == "success":
            session['user_name'] = username  # Update session with new username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    try:
        result = db.change_password(user_id, current_password, new_password)
        if result == "success":
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        result = db.delete_account(user_id)
        if result == "success":
            session.clear()  # Clear session after successful deletion
            return jsonify({'success': True, 'redirect': url_for('login')})
        else:
            return jsonify({'success': False, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)