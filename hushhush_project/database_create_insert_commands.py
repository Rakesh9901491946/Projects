import database_ddl_commands
import pandas as pd
from sklearn.model_selection import train_test_split

#Database path
database_path = 'candidate_data.db'
#Dropping all the tables before
database_ddl_commands.drop_all_tables(database_path)

#SQL create table query for Training
create_table_query = '''
CREATE TABLE IF NOT EXISTS train_data (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    job_role TEXT,
    tags TEXT,
    member_since TEXT,
    gold_badges INTEGER,
    silver_badges TEXT,
    bronze_badges TEXT,
    reputation TEXT,
    reached TEXT,
    questions TEXT,
    answers TEXT,
    location TEXT,
    posts_edited TEXT,
    helpful_tags TEXT,
    votes_cast TEXT
);
'''

# Call the function to create a table
database_ddl_commands.create_table(database_path, create_table_query)

#Creating table for testing
create_table_query = '''
CREATE TABLE IF NOT EXISTS test_data (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    job_role TEXT,
    tags TEXT,
    member_since TEXT,
    gold_badges INTEGER,
    silver_badges TEXT,
    bronze_badges TEXT,
    reputation TEXT,
    reached TEXT,
    questions TEXT,
    answers TEXT,
    location TEXT,
    posts_edited TEXT,
    helpful_tags TEXT,
    votes_cast TEXT
);
'''

# Call the function to create a table
database_ddl_commands.create_table(database_path, create_table_query)

#Creating Table for 
create_table_query = '''
CREATE TABLE IF NOT EXISTS unseen_data (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    job_role TEXT,
    tags TEXT,
    member_since TEXT,
    gold_badges INTEGER,
    silver_badges TEXT,
    bronze_badges TEXT,
    reputation TEXT,
    reached TEXT,
    questions TEXT,
    answers TEXT,
    location TEXT,
    posts_edited TEXT,
    helpful_tags TEXT,
    votes_cast TEXT
);
'''

# Call the function to create a table
database_ddl_commands.create_table(database_path, create_table_query)


# ## Reading the data from CSV

# In[18]:


df1 = pd.read_csv('0to50k_profile_data.csv')
print('df1 :',df1.shape)
df2 = pd.read_csv('50to100k_profile_data.csv')
print('df2 :',df2.shape)
df3 = pd.read_csv('0to50k_activity_data.csv')
print('df3 :',df3.shape)
df4 = pd.read_csv('50to100k_activity_data.csv')
print('df4 :',df4.shape)

# joining df1 and df2
df_p = pd.concat([df1,df2])
df_p = df_p.drop_duplicates(['user_id'])
print('concat profiles:', df_p.shape)
df_a = pd.concat([df3,df4])
df_a.drop(columns=['Name'],inplace=True)
df_a = df_a.drop_duplicates(['user_id'])
print('concat activities:', df_a.shape)

df_p['user_id'] = df_p['user_id'].astype(str)
df_a['user_id'] = df_a['user_id'].astype(str)

#merging profiles and activities
df = pd.merge(df_p, df_a, how = 'inner', on = 'user_id')
df = df.drop_duplicates(['user_id'])
print('merging profiles and activities :', df.shape)

#keeping only necessary columns
df.columns = df.columns.str.lower()
df = df.reindex(['user_id', 'name', 'job_role', 'tags', 'member_since', 'gold_badges',
       'silver_badges', 'bronze_badges', 'reputation', 'reached', 'questions',
       'answers', 'location', 'posts_edited', 'helpful_tags', 'votes_cast'],axis=1)
df['user_id'] = df['user_id'].astype(float).astype(int)
print('finaldf :', df.shape)


# Splitting Train, Test, Unseen

# Split the DataFrame into two parts: 50% for training and the remaining 50%
df_train, temp_df = train_test_split(df, test_size=0.5, random_state=42)

# From the remaining 50%, split 15% for testing and 35% for unseen
df_unseen, df_test = train_test_split(temp_df, test_size=0.3, random_state=42)  

# Data dimensions
print('train data :', df_train.shape)
print('test data :', df_test.shape)
print('unseen data :', df_unseen.shape)

#insert the data
database_ddl_commands.insert_data_from_dataframe('candidate_data.db', 'train_data', df_train)
database_ddl_commands.insert_data_from_dataframe('candidate_data.db', 'test_data', df_test)
database_ddl_commands.insert_data_from_dataframe('candidate_data.db', 'unseen_data', df_unseen)


# In[ ]:




