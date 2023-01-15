import requests
import pandas as pd
from pathlib import Path
import datetime

def personal_workouts_function():
    s = requests.Session()

    with open('peloton_username.txt') as h:
        username = h.read()
    #
    with open('peloton_pwd.txt') as i:
        pwd = i.read()

    # raw_path = r'C:\Users\Owner\OneDrive\Documents\Python'
    #
    # formatted_path = raw_path.replace("\\", "/")
    #
    # filepath = Path(formatted_path)
    #
    # pwd_path = filepath / 'pwd.txt'
    #
    # username_path = filepath / 'username.txt'
    #
    # with open(username_path) as h:
    #     username = h.read()
    #
    # with open(pwd_path) as i:
    #     pwd = i.read()

    payload = {'username_or_email':username, 'password':pwd}
    s.post('https://api.onepeloton.com/auth/login', json=payload)

    query_personal = s.get('https://api.onepeloton.com/api/me')

    user_id = query_personal.json()['id']

    # personal workout query string
    pw_query_string = r"https://api.onepeloton.com/api/user/{}/workouts?joins=ride&limit=100".format(user_id)

    q_personal_workouts = s.get(pw_query_string)

    ## Show an example of information in the 'data' key

    personal_workout_columns = q_personal_workouts.json()['data'][0].keys()

    personal_workout_columns_list = list(personal_workout_columns)

    q_per_dict = q_personal_workouts.json()['summary']
    sum_of_workouts = sum(q_per_dict.values())
    df = pd.DataFrame(columns=personal_workout_columns_list)

    pw_list = []
    counter = 0
    while counter in range(0, sum_of_workouts - 1):
        for i in personal_workout_columns_list:
            pw_list.append(q_personal_workouts.json()['data'][counter][i])
        # print(pw_list)
        df.loc[len(df)] = pw_list
        pw_list.clear()
        counter = counter + 1

    df.drop('ride', inplace=True, axis=1)

    date_offset = pd.DateOffset(hours=5)
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s') - date_offset
    df['end_time'] = pd.to_datetime(df['end_time'], unit='s') - date_offset
    df['start_time'] = pd.to_datetime(df['start_time'], unit='s') - date_offset
    df['created'] = pd.to_datetime(df['created'], unit='s') - date_offset
    df['device_time_created_at'] = pd.to_datetime(df['device_time_created_at'], unit='s') - date_offset
    return df
    # print(df)
    # df.to_csv('peloton.csv')






