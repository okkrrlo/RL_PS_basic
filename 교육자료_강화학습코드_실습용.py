from builtins import range
import xlwings as xw
import pandas as pd
import os
# import random
# import gym
import numpy as np
# from gym import spaces
# import tensorflow as tf
# import numpy as np
# from sqlalchemy.sql.functions import random


# 엑셀 공정 설정 데이터 불러오기
# 엑셀 모듈 실행
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "강화학습_똑똑이.xlsm")
xw.Book(file_path).set_mock_caller()
wb = xw.Book.caller()

locations = {
    2: [300, 100],
    3: [500, 100],
    4: [700, 100],
    6: [300, 300],
    7: [500, 300],
    8: [700, 300],
    10: [300, 500],
    11: [500, 500],
    12: [700, 500],
    14: [300, 700],
    15: [500, 700],
    16: [700, 700],
}

#한번의 시뮬에서 한번의 액션 발생
def action(act, location_num):
    if act == 1 and location_num[0] > 2:
        location_num[0] -= 1
    elif act == 2 and location_num[0] < 4:
        location_num[0] += 1
        
    elif act == 3 and location_num[1] > 6:
        location_num[1] -= 1
    elif act == 4 and location_num[1] < 8:
        location_num[1] += 1
        
    elif act == 5 and location_num[2] > 10:
        location_num[2] -= 1
    elif act == 6 and location_num[2] < 12:
        location_num[2] += 1
        
    elif act == 7 and location_num[3] > 14:
        location_num[3] -= 1
    elif act == 8 and location_num[3] < 16:
        location_num[3] += 1

    print(location_num)

    for i, Lnum in enumerate(location_num):
        cell_range = f"F{i+8}"
        wb.sheets["data"].range(cell_range).value = Lnum

    # 선택된 번호의 좌표를 엑셀 시트에 입력
    for i, num in enumerate(location_num):
        x_coord, y_coord = locations[num]
        cell_range = f"D{i+8}:E{i+8}"
        wb.sheets["data"].range(cell_range).value = [[x_coord, y_coord]]

    return location_num

#1,1 의 값을 가져와서 계속 비교해주는 친구 되겟습니다
def calculate_reward(selected_numbers):
    sheet2 = wb.sheets['reward']
    # VBA 코드 내 시뮬레이션 수행 메소드 실행
    sim_macro = wb.macro('dataload')
    #아 이게 지금 vba 실행시키는 코드네
    sim_macro()
    reward = sheet2.range('A1').value
    print("리워드는 ", reward)
    #reward = sheet2.range('B4').value + sheet2.range('C4').value + sheet2.range('D4').value + sheet2.range('D4').value
    return reward

#설비배치에 있어서 가장 까다로운 부분
#설비배치에 대해 어떠한 상태를 정의한 부분인데
#이 코드에서는 각 location num을 더한 값에서 31을 뺀 값(0~9)을 state로 정의
def State(location_num):
    state = -31
    for state_value in location_num:
        state += state_value
    print("state: ", state)
    return state



# 테이블 생성
q_table = pd.DataFrame(columns=[1, 2, 3, 4, 5, 6, 7, 8], index=range(0, 10))
q_table = q_table.fillna(0)  # Q Table 초기화
print(q_table)
global epsilon
global terminate
global past_reward

terminate = True
terminate_num = 0
past_reward = 0

while terminate:
    for i in range(1, 10):
        print("---------------------------------------------")
        print(i)
        print("---------------------------------------------")
        # 입실론 그리디 정책을 위한 초기 입실론 값
        if i == 1:
            epsilon = 0.5
        else:
            epsilon = epsilon * (0.95 ** (i - 1))  # 에피소드가 증가할수록 입실론 값을 작은 값으로 업데이트

        sheet1 = wb.sheets['data']
        sheet2 = wb.sheets['reward']
        location_num = sheet1.range("F8:F11").value
        location_num_int= list(map(int, location_num))
        state = State(location_num_int)
        if i < 3:
            act = int(np.random.choice(8))
            #print("act:", act)
        else:
            if state == 9 or np.random.uniform() < epsilon:
                act = int(np.random.choice(8))
            else:
                act = np.argmin(q_table.iloc[state]) + 1
        print("act:", act)
        selected_numbers = action(act, location_num_int)
        reward = calculate_reward(selected_numbers)

        #원래 q-table 업데이트는 q-value값으로 해야함
        # table 업데이트
        q_table.loc[state, act] = reward
        print("Q TABLE:")
        print(q_table)
        #이건 쪼개야쓰겄네
        #q-table은 행(state) - 열(action) 에 따른 reward값. 으로 읽으면 됨
        print(reward)
        print("---------------------------------------------")
        print("---------------------------------------------")

        if past_reward <= reward:
            terminate_num += 1
            if terminate_num > 6:
                break
        else:
            terminate_num = 0
        past_reward = reward
    terminate = False


