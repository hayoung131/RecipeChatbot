import re #addddddddd
from collections import Counter
import string
from string import punctuation
from math import sqrt
import hashlib
import sys
import utils
import pymysql

weight = 0
chat_state = 0
status = False


# Based on a blog-post Here: http://rodic.fr/blog/python-chatbot-1/

import utils  # General utils including config params and database connection
conf = utils.get_config()

ACCURACY_THRESHOLD = 0.03
NO_DATA = "Sorry I don't know what to say"

toBool = lambda str: True if str == "True" else False # str 변수값이 t면 t반환, f면 f반환
#람다식 https://offbyone.tistory.com/73 참조

DEBUG_ASSOC = toBool(conf["DEBUG"]["assoc"])
DEBUG_WEIGHT = toBool(conf["DEBUG"]["weight"])
DEBUG_ITEMID = toBool(conf["DEBUG"]["itemid"])
DEBUG_MATCH = toBool(conf["DEBUG"]["match"])#각각의 변수에 저 boolean값들을 셋팅한듯.


DBHOST = conf["MySQL"]["server"]
DBUSER = conf["MySQL"]["dbuser"]
DBNAME = conf["MySQL"]["dbname"]

connection = utils.db_connection(DBHOST, DBUSER, DBNAME)
cursor = connection.cursor()
connectionID = utils.db_connectionID(cursor)
#Strip non-alpha chars out - basic protection for SQL strings built out of concat ops
##clean = lambda str: ''.join(ch for ch in str if ch.isalnum())

#
# def train_me(inputSentence, responseSentence, cursor):
#     print("질문 : ",inputSentence)
#     print("대답 : ",responseSentence)

def chat_flow(cursor, humanSentence):
    status = False
    if(humanSentence == '1'): ########################### 1. 이런식으로 다양하게 쓸 수도 있으니까 정규식으로 숫자만 거르게해야함.
        print("음식명으로 레시피 찾아줌")####################3여기에 재료명으로 레시피 찾는 메소드 호출. 즉 만들어뒀던걸 메소드화시키기
        ##재료도 입력할지 여부를 받고
        print("bot>>> 어떤 레시피가 궁금해? ")
        humanRecipe=input(">>> 레시피 명 : " ).strip('')
        print("bot>>> 재료도 입력할래?    [y/n]")
        humanRecipe2 = input().strip()#전처리
        if(humanRecipe2=='y' or humanRecipe2=='yes') :

            humanIngredient = input(" ,를 기준으로 재료 입력해줘 : ").strip()
            humanIngredient=humanIngredient.split(',')# 문자 ,를 기준으로 리스트로 변경시킴.
            #['고구마', '감자 ', ' 공주', '냠냠'] 이런식으로 공백도 함께 들어가 버림
            IngredientScore = "(" #이 변수는 select 문에 재료일치도 뽑아주기위해서 따로 만들어준것.
            IngredientSelect = "SELECT cooking_title,recipe_url,"
            IngredientSelect_sub=" FROM mainrecipe WHERE" # from 앞부분에 일치도부분 변수를 넣고 as 해줘야하기에 따로 뽑아둠.
            for i in humanIngredient:
                IngredientScore +="(ingredient LIKE '%"+i.strip()+"%')+"#
            IngredientScore=IngredientScore.rstrip('+') #맨마지막 재료뒤에도 붙어버린 +제거
            IngredientScore+=")/ingredient_num"
            IngredientSelect_sub+=IngredientScore+">=0.8"

            IngredientSelect+=IngredientScore +" as ingredient_score"+IngredientSelect_sub

            #print(IngredientScore)

            #완성된 쿼리문 예시
            # SELECT cooking_title,recipe_url
            # FROM mainrecipe
            # WHERE ((ingredient LIKE '%gredient LIKE '%식초%')+(ingredient LIKE '%물%')
            # +(ingredient LIKE '%설탕%')+(ingredient LIKE '%올리고당%')+(ingredient LIKE '%다시마%')
            # +(ingredient LIKE '%멸치가루%')+(ingredient LIKE '%양파%')+(ingredient LIKE '%대파%'))/ingredient_num >=0.8
            #작은 관호들의 결과는 재료가 있을경우 1, 없을 경우 0을 반환하여 최종적으로 나오는 결과는 db에서 재료문자열내에 존재하는
            #사용자입력재료들의 개수
            #저 식이 근데 잘못된거같으니 수정해야돼... 재료가 깻잎밖에 없는것도 뽑혀버렸어..ㅠㅠ

            #print(IngredientSelect)
            cursor.execute(IngredientSelect)
            b=cursor.fetchall()
            print(b)
            return b,True ##########################이부분도 해결해야됨. 전체 흐름도 좀 해결해야되고
        elif(humanRecipe2=='n' or humanRecipe2=='no') :
            print(humanRecipe)
            titleSelect="select cooking_title, recipe_url from mainrecipe m, title t " \
                        "where m.recipe_id = t.recipe_id " \
                        "and searching_title like '%"+humanRecipe+"%'"

            # 니가 정리했떤 가중치를 db에서 나열을 해서가져오기,
            print(titleSelect)
            cursor.execute(titleSelect)
            #받아오기
            a=cursor.fetchone()
            print(a)
        #레시피명과 일치하는 칼럼들중에, 만약 사용자가 재료도 입력했다면
        #재료도 데이터베이스에 넘겨주고, 재료 테이블에서 재료들과 비교하여 사용자가 넘겨준 재료의 80 %이상인 재료를 가진 레시피 정보를
        #모두 모아서  재료와 레시피명이 가장 일치하는것들을 기준으로 정렬하고,
        # 만약 같은 정확도라면 별점.댓글수를 기준으로 높은것들을 정렬하여 쳇봇에게 넘겨주기

        #이걸 sql 로 전부 해서 줘야겠지..
            status = True
            botSentence=a
            return a,status
    elif(humanSentence == '2'):
        print("재료명으로 레시피 찾아줌")
        status = True
        botSentence="크림파스타 url 출력하기 "

        print(status)
    return botSentence, status

if __name__ == "__main__":

    conf = utils.get_config()

    DBHOST = conf["MySQL"]["server"]
    DBUSER = conf["MySQL"]["dbuser"]
    DBNAME = conf["MySQL"]["dbname"]

    print("Starting Bot...")
    # initialize the connection to the database
    print("Connecting to database...")
    connection = utils.db_connection(DBHOST, DBUSER, DBNAME)
    cursor = connection.cursor()
    connectionID = utils.db_connectionID(cursor)
    print("...connected")

    status = False
    botSentence = '안녕 나는 냠냠봇이야!^^ 찾는 레시피 있니?\n' \
                  '1. 찾는 레시피명\n' \
                  '2. 가지고 있는 재료'
    while True:
        print('Bot> ' ,status,botSentence)# 봇 :  안녕 나는 냠냠봇이야
        if status:
            print("더 물어볼게 있니? [y/n]")
            humanSentence = input('>>> ').strip()
            if(humanSentence == 'y' ):
                print('안녕 나는 냠냠봇이야!^^ 찾는 레시피 있니?\n' \
                  '1. 찾는 레시피명\n' \
                  '2. 가지고 있는 재료')
            elif (humanSentence == 'n'):
                break

        # if trainMe:
        #     print('Bot> 나에게 알려줄래?')
        #     previousSentence = humanSentence
        #     humanSentence = input('>>>').strip()
        #
        #     if len(humanSentence) > 0:
        #         train_me(previousSentence, humanSentence, cursor)
        #         print("Bot> 더 찾고싶은 레시피가 있으면 말해줘")
        #     else:
        #         print("Bot> OK, moving on...")
        #         trainMe = False

        # Ask for user input; if blank line, exit the loop
        humanSentence = input('>>> ').strip() #.strip()양쪽 공백을 없애는것 #사용자가 질문함.
        # if humanSentence == '' or humanSentence.strip(punctuation).lower() == 'quit' or humanSentence.strip(punctuation).lower() == 'exit': #punctuation = 특수문자들
        #     break #사용자가 그냥 엔터치거나 quit나 exit를 치면 채팅이 종료됨.




        # 1번, 1  / 2번 2 이렇게오면 정규식을 사용하여 숫자만 받기, 만약 그 외의 숫자나, 문자를 사용하면 다시 입력 하도록 요청하기

        botSentence, status = chat_flow(cursor, humanSentence) #weight의 처음 값은 0

        connection.commit()
