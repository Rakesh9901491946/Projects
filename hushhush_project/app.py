from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
from selector import get_data
import pandas as pd
import openai
from openai import OpenAI
import json
import sqlite3
from dotenv import load_dotenv
import os
from codeevalgpt import chatgpt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Candidate_Requirements.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class CandidateRequirement(db.Model):
    # tablename = 'candidate_requirement'
    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String())
    years_of_experience = db.Column(db.String())
    number_of_candidates = db.Column(db.Integer)
    #save created time in created_at column
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())




class CodingSolution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    solution_1 = db.Column(db.String())
    solution_2 = db.Column(db.String())
    solution_3 = db.Column(db.String())
    evaluated= db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
class SelectedCandidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    attempted = db.Column(db.Boolean, default=False)
    selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    question= db.Column(db.String())
    code_snippet= db.Column(db.String())
    time_complexity= db.Column(db.String())
    space_complexity= db.Column(db.String())
    feedback= db.Column(db.String())
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    
 
with app.app_context():   
    db.create_all()

users = {
    'Recruiter@gmail.com': {'password': 'password@123', 'dashboard': 'dashboard'},
    'HRecruiter@gmail.com': {'password': 'password@1234', 'dashboard': 'dashboard2'},
    'student@gmail.com': {'password': 'student@123', 'dashboard': 'coding'},
    'studentdb@gmail.com': {'password': 'studentdb@123', 'dashboard': 'studentdb'},
}

@app.route('/', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials and redirect to the correct dashboard
        user_info = users.get(username)
        if user_info and user_info['password'] == password:
            if user_info['dashboard'] == 'dashboard':
                return redirect(url_for('dashboard'))
            elif user_info['dashboard'] == 'dashboard2':
                return redirect(url_for('dashboard2'))
            elif user_info['dashboard'] == 'coding':
                return redirect(url_for('coding'))
            elif user_info['dashboard'] == 'studentdb':
                return redirect(url_for('studentdb'))
       
        return render_template('login.html', error='Invalid credentials.')
        
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
   
    return render_template('dashboard.html')

@app.route('/dashboard2')
def dashboard2():
   
    return render_template('dashboard2.html')
@app.route('/studentdb')
def studentdb():
   
    return render_template('studentdb.html')
@app.route('/overview')
def overview():
    sc = SelectedCandidate.query.all()

    sc_list = []
    for s in sc:
        selected = ('Yes' if s.selected else 'No') if s.attempted else 'Not yet attempted'
        
        feedback = Feedback.query.filter_by(user_id=s.user_id).first()
        
        sc_list.append({
            'user_id': s.user_id,
            'attempted': 'Yes' if s.attempted else 'No',
            'selected': selected,
            'evaluated': 'Yes' if feedback else 'No',
            'Link Expired': 'Yes' if (datetime.now() - s.created_at).seconds > 86400 else 'No'
        })
    
    return render_template('overview.html', selected_candidates=sc_list)

@app.route('/candidate_requirements')
def candidate_requirements():
   
    return render_template('candidate_requirements.html')
@app.route('/submit-candidate-requirements', methods=['POST'])
def submit_candidate_requirements():
    job_role = request.form['job_roles']
    years_of_experience = request.form['years_of_experience']
    number_of_candidates = request.form['number_of_candidates']
 
    new_candidate_requirement = CandidateRequirement(job_role=job_role, years_of_experience=years_of_experience, number_of_candidates=number_of_candidates, created_at=datetime.now())
 
    db.session.add(new_candidate_requirement)
   
    db.session.commit()
   
    return redirect(url_for('dashboard'))
@app.route('/candidate_results')
def candidate_results():
   
    return render_template('candidate_results.html')

@app.route('/coding/<int:user_id>')
def coding(user_id):
    selected_candidate = SelectedCandidate.query.filter_by(user_id=user_id).first()
    # selected_candidate= CandidateRequirement.query.filter_by(user_id=user_id).first()
    created_date = selected_candidate.created_at

    if (datetime.now() - created_date).seconds > 86400:

        return "Sorry, the test link has expired."
    else:
        print(selected_candidate.attempted)
        if selected_candidate.attempted: 
            return 'Already attempted'
        return render_template('coding.html', user_id=user_id)
    

@app.route('/coding_solutions', methods=['POST'])
def coding_solutions():
    if request.method == 'POST':
       
        candidate_id = int(int(request.form['candidate_id'].strip()))
        solution_1 = request.form['code_solution_1'].strip()
        solution_2 = request.form['code_solution_2'].strip()
        solution_3 = request.form['code_solution_3'].strip()
       
        created_at = datetime.now()
       
        new_solution = CodingSolution(user_id=candidate_id,
                                      solution_1=solution_1,
                                      solution_2=solution_2,
                                      solution_3=solution_3,
                                      created_at=created_at)
       
        db.session.add(new_solution)
       
        db.session.commit()
       
        attemped_test(candidate_id)
       
        time_complexity, space_complexity, feedback = chatgpt("Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.", solution_1)
       
        new_feedback = Feedback(user_id=candidate_id,
                                question="Sum Problem Statement: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
                                code_snippet=solution_1,
                                time_complexity=time_complexity,
                                space_complexity=space_complexity,
                                feedback=feedback,
                                created_at=created_at)
       
        db.session.add(new_feedback)
       
        time_complexity, space_complexity, feedback = chatgpt("Longest Substring Without Repeating Characters Problem Statement: Given a string s, find the length of the longest substring without repeating characters.", solution_2)
       
        new_feedback = Feedback(user_id=candidate_id,
                                question="Longest Substring Without Repeating Characters Problem Statement: Given a string s, find the length of the longest substring without repeating characters.",
                                code_snippet=solution_2,
                                time_complexity=time_complexity,
                                space_complexity=space_complexity,
                                feedback=feedback,
                                created_at=created_at)
       
        db.session.add(new_feedback)
       
        time_complexity, space_complexity, feedback = chatgpt("Maximum Subarray Sum Problem Statement: Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.", solution_3)
       
        new_feedback = Feedback(user_id=candidate_id,
                                question="Maximum Subarray Sum Problem Statement: Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
                                code_snippet=solution_3,
                                time_complexity=time_complexity,
                                space_complexity=space_complexity,
                                feedback=feedback,
                                created_at=created_at)
        
        db.session.add(new_feedback)
       
        db.session.commit()
       
        return redirect(url_for('login'))
 
    return render_template('coding.html')


@app.route('/requirement_demands_list')
def requirement_demands_list():

    latest_job_requirement = CandidateRequirement.query.order_by(CandidateRequirement.created_at.desc()).first()
    print(latest_job_requirement)
    return render_template('requirement_demands_list.html', latest_job_requirement=latest_job_requirement)


@app.route('/Eligible_Candidate_list', methods=['GET'])
def Eligible_Candidate_list():
    selected_candidates = SelectedCandidate.query.all()
    selected_ids = [str(float(candidate.user_id)) for candidate in selected_candidates]
    
    role = request.args.get('role')
    num = int(request.args.get('num'))
    print(num)
    
    return render_template('Eligible_Candidate_list.html', candidates=get_data(role, num, selected_ids))


@app.route('/add_selected_candidate', methods=['GET'])
def add_selected_candidate():
    candidate_id = int(float(request.args.get('user_id')))
    df = pd.read_csv('0to50k_profile_data.csv')
    print(df[df['user_id'] == candidate_id])
    
    new_candidate = SelectedCandidate(id=candidate_id,
                                      user_id=candidate_id, 
                                      attempted=False,
                                      selected=False,
                                      created_at=datetime.now())
    
    db.session.add(new_candidate)
    
    db.session.commit()
    
    return {'status': 'success'}

def attemped_test(candidate_id):
    # candidate_id = int(float(request.args.get('user_id')))
    candidate = SelectedCandidate.query.filter_by(user_id=candidate_id).first()
    candidate.attempted = True
    db.session.commit()

@app.route('/passed_test', methods=['GET'])
def passed_test():
    candidate_id = int(float(request.args.get('user_id')))
    candidate = SelectedCandidate.query.filter_by(user_id=candidate_id).first()
    candidate.selected = True
    db.session.commit()
    
    return {'status': 'success'}
@app.route('/hr_overview')
def hr_overview():
    sc = SelectedCandidate.query.all()

    sc_list = []
    for s in sc:
        selected = ('Yes' if s.selected else 'No') if s.attempted else 'Not yet attempted'
        
        feedback = Feedback.query.filter_by(user_id=s.user_id).first()
        
        sc_list.append({
            'user_id': s.user_id,
            'attempted': 'Yes' if s.attempted else 'No',
            'selected': selected,
            'evaluated': 'Yes' if feedback else 'No',
            'Link Expired': 'Yes' if (datetime.now() - s.created_at).seconds > 86400 else 'No'
        })
        
    return render_template('hr_overview.html', selected_candidates=sc_list)

@app.route('/summary/<int:user_id>')
def summary(user_id):
    feedback = Feedback.query.filter_by(user_id=user_id).all()
    
    return render_template('summary.html', feedback={'feedback': feedback, 'user_id': user_id})

@app.route('/set_result/<int:user_id>/<result>')
def set_result(user_id, result):
    sc = SelectedCandidate.query.filter_by(user_id=user_id).first()
    
    if result == 'Yes':
        sc.selected = True
    else:
        sc.selected = False
    
    db.session.commit()
    
    return redirect(url_for('overview'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)

