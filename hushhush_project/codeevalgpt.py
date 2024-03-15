import openai
import json
import sqlite3
from dotenv import load_dotenv
import os

# def chatgpt():
#     # Load the environment variables from .env file
#     load_dotenv()
#     api_key = os.getenv('API_KEY')
#     candidate_conn = sqlite3.connect('Candidate_Requirements.db')
#     candidate_cursor = candidate_conn.cursor()

#     # Ensure the selected_candidate table exists
#     candidate_cursor.execute('''
#     CREATE TABLE IF NOT EXISTS selected_candidate (
#         id INTEGER PRIMARY KEY,
#         user_id INTEGER NOT NULL,
#         attempted BOOLEAN NOT NULL DEFAULT 0,
#         selected BOOLEAN NOT NULL DEFAULT 0,
#         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#     );
#     ''')
#     candidate_conn.commit()
    
#     feedback_conn = sqlite3.connect('feedback.db')
#     feedback_cursor = feedback_conn.cursor()
#     feedback_cursor.execute('''CREATE TABLE IF NOT EXISTS feedback 
#                                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
#                                      question TEXT, 
#                                      code_snippet TEXT, 
#                                      time_complexity TEXT, 
#                                      space_complexity TEXT, 
#                                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                                      feedback TEXT)''')

#     # Connect to the feedback database
   

#     # Connect to the Candidate_Requirements database
#     candidate_conn = sqlite3.connect('Candidate_Requirements.db')
#     candidate_cursor = candidate_conn.cursor()

#     # Fetch user_ids of candidates whose solutions have not been evaluated yet
#     candidate_cursor.execute("SELECT user_id FROM selected_candidate WHERE selected = 'False'")
#     user_ids = candidate_cursor.fetchall()

#     if not user_ids:
#         print("No unevaluated candidates found.")
#         return

#     for user_id in user_ids:
#         # Fetch the code snippets for the unevaluated user_id
#         candidate_cursor.execute("SELECT solution_1, solution_2, solution_3 FROM coding_solution WHERE user_id = ?", (user_id[0],))
#         solutions = candidate_cursor.fetchall()

#         if solutions:
#             # Assuming solutions contain at least one valid solution
#             solutions = solutions[0]  # Taking the first set of solutions assuming it's one user_id per row
#             questions_and_answers = [{
#                 "question": f"Custom question for solution {i+1} of user_id {user_id[0]}",
#                 "code_snippet": solution
#             } for i, solution in enumerate(solutions) if solution]  # Ensuring non-empty solutions are processed

            

#             for item in questions_and_answers:
#                 PROMPT = f"""
#                 Question: {item['question']}
                
#                 The code solution is below and delimited by triple backticks:
#                 ```python
#                 {item['code_snippet']}
#                 ```
                
#                 YOUR RESPONSE SHOULD STRICTLY BE A JSON AND SHOULD FOLLOW THE FORMAT BELOW:
#                 {{"time_complexity": "O(n)", "space_complexity": "O(1)", "feedback": "The code is correct and efficient."}}
#                 """

#                 client = openai.Client(api_key=api_key)

#                 completion = client.chat.completions.create(
#                     model="gpt-3.5-turbo",
#                     messages=[
#                         {"role": "system", "content": "You are an AI code evaluator. You will be provided with a Question and a code snippet. You need to check the provided question and code snippet. And provide time & space complexity and also the feedback if any syntax errors and logical errors are found."},
#                         {"role": "user", "content": PROMPT}
#                     ]
#                 )

#                 # Extracting data from the response
#                 time_complexity = json.loads(completion.choices[0].message.content)['time_complexity']
#                 space_complexity = json.loads(completion.choices[0].message.content)['space_complexity']
#                 feedback = json.loads(completion.choices[0].message.content)['feedback']
#                 print(completion.choices[0].message.content)

#                 feedback_cursor.execute("INSERT INTO feedback (question, code_snippet, time_complexity, space_complexity, feedback) VALUES (?, ?, ?, ?, ?)",
#                                         (item['question'], item['code_snippet'], time_complexity, space_complexity, feedback))
#                 feedback_conn.commit()

#                 # Optionally, update the 'evaluated' status for the user_id in the 'selected_candidate' table
#                 candidate_cursor.execute("UPDATE selected_candidate SET evaluated = 'True' WHERE user_id = ?", (user_id[0],))
#                 candidate_conn.commit()

#     # Close the database connections
#     candidate_conn.close()
#     feedback_conn.close()
# # Call the function
# chatgpt()
def chatgpt(question, solution):
    load_dotenv()
   
    api_key = os.getenv('API_KEY')
 
    PROMPT = f"""
    Question: {question}
   
    The code solution is below and delimited by triple backticks:
    ```python
    {solution}
    ```
   
    YOUR RESPONSE SHOULD STRICTLY BE A JSON AND SHOULD FOLLOW THE FORMAT BELOW:
    {{"time_complexity": "O(n)", "space_complexity": "O(1)", "feedback": "The code is correct and efficient."}}
    """
 
    client = openai.Client(api_key=api_key)
 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI code evaluator. You will be provided with a Question and a code snippet. You need to check the provided question and code snippet. And provide time & space complexity and also the feedback if any syntax errors and logical errors are found."},
            {"role": "user", "content": PROMPT}
        ]
    )
 
    # Extracting data from the response
    time_complexity = json.loads(completion.choices[0].message.content)['time_complexity']
    space_complexity = json.loads(completion.choices[0].message.content)['space_complexity']
    feedback = json.loads(completion.choices[0].message.content)['feedback']
   
    return time_complexity, space_complexity, feedback
