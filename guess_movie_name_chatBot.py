# -*- coding: utf-8 -*-
import json
import urllib.request
import random

from slackclient import SlackClient
from flask import Flask, request, make_response
from datetime import datetime

app = Flask(__name__)
TASK_IDS = {}

slack_token =
slack_client_id = 
slack_client_secret =
slack_verification =
sc = SlackClient(slack_token)

task_id = 'LB-2375'

attachments_json = [
    {
        "callback_id": "quizGame",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "actions": [
            {
                "name": "game",
                "text": "정답 확인",
                "style": "danger",
                "type": "button",
                "value": "war",
                "confirm": {
                    "title": "정답은?",
                    "text": "quiz 또는 QUIZ를 입력해 주세요",
                    "ok_text": "맞음",
                    "dismiss_text": "틀림"
                }
            },
            {
                "name": "game",
                "text": "개봉일 힌트 보기",
                "type": "button",
                "value": "war",
                "confirm": {
                    "title": "Hint!",
                    "text": "quiz 또는 QUIZ를 입력해 주세요"
                }
            },
            {
                "name": "game",
                "text": "첫글자 힌트 보기",
                "type": "button",
                "value": "war",
                "confirm": {
                    "title": "Hint!",
                    "text": "quiz 또는 QUIZ를 입력해 주세요"
                }
            },
            {
                "name": "game",
                "text": "감독 힌트 보기",
                "type": "button",
                "value": "war",
                "confirm": {
                    "title": "Hint!",
                    "text": "quiz 또는 QUIZ를 입력해 주세요"
                }
            }
        ]
    }
]


def get_director(mv_name):
    base_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    api_key = "9e24d40e601d03984a93fc216b030a09"

    query_url = '{}?key={}&movieNm={}'.format(base_url, api_key, urllib.parse.quote(mv_name))  # 박스오피스

    with urllib.request.urlopen(query_url) as fin:
        return json.loads(fin.read().decode('utf-8'))


def simplify_director(result, mv_code):
    name = [entry.get("directors")[0].get("peopleNm") for entry in result.get('movieListResult').get('movieList') if entry.get("movieCd") == mv_code]

    return name[0]


def isHangul(ch):  # 주어진 문자가 한글인지 아닌지 리턴해주는 함수
    JAMO_START_LETTER = 44032
    JAMO_END_LETTER = 55203
    return ord(ch) >= JAMO_START_LETTER and ord(ch) <= JAMO_END_LETTER


def cho(text):
    CHOSUNG_START_LETTER = 4352
    JAMO_START_LETTER = 44032
    JAMO_END_LETTER = 55203
    JAMO_CYCLE = 588
    chosung = ""

    for ch in text:
        if isHangul(ch):  # 한글인 경우에만 초성을 추출하고 그렇지 않은 경우엔 문자를 그대로 출력합니다.
            chosung += chr(int((ord(ch) - JAMO_START_LETTER) / JAMO_CYCLE) + CHOSUNG_START_LETTER)
        else:
            chosung += ch

    print("안녕하세요! 즐거운 초성 퀴즈 시간입니다. 어떤 영화의 초성인지 맞춰보세요!")
    return chosung


def get_date():
    start = datetime.strptime('11/11/2003 08:30 AM', '%m/%d/%Y %I:%M %p')  # 최초DB 2003/11/11 부터~
    end = datetime.now()
    random_date = start + (end - start) * random.random()
    target_dt_str = random_date.strftime('%Y%m%d')
    return target_dt_str


def get_movies():
    base_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    api_key = "9e24d40e601d03984a93fc216b030a09"
    target_dt_str = get_date()

    query_url = '{}?key={}&targetDt={}&itemPerPage={}'.format(base_url, api_key, target_dt_str, "8")  # 박스오피스
    with urllib.request.urlopen(query_url) as fin:
        return json.loads(fin.read().decode('utf-8'))


def simplify(result):
    temp_num = random.randrange(6, 9)
    return [

        result.get('boxOfficeResult').get('dailyBoxOfficeList')[temp_num].get('movieNm'),
        result.get('boxOfficeResult').get('dailyBoxOfficeList')[temp_num].get('openDt'),
        result.get('boxOfficeResult').get('dailyBoxOfficeList')[temp_num].get('movieCd')
    ]


def check_input(text):
    keywords = []
    text = text.lower()
    if 'quiz' in text or '퀴즈' in text:
        movies = get_movies()  # movies 타입은 dict
        movie_info = simplify(movies)  # 영화제목과 개봉일, 타입은 list
        # movie_info[0] = 영화제목
        # movie_info[1] = 개봉일
        # movie_info[2] = 영화 코드
        print(movie_info)
        keywords.append(movie_info[0])
        keywords.append(cho(movie_info[0]))
        keywords.append(movie_info[1])
        keywords.append(movie_info[2])
        # keywords 에는 영화제목, 영화제목 초성, 개봉일이 순서대로 들어감.
        return u'\n'.join(keywords)  # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    else:
        keywords.append("quiz <- 를 입력해 주세요 \n quiz <- 를 입력해 주세요 \n \n")
        return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        keywords = check_input(text)

        movie_name, movie_chosung, movie_open_day, movie_code = keywords.split('\n')
        print(type(movie_name))
        if not 'quiz' in movie_name:

            dir_info = get_director(movie_name)
            dir_name = simplify_director(dir_info, movie_code)
            print(type(movie_chosung))
            print(movie_name[0])
            attachments_json[0].get('actions')[0].get('confirm')['text'] = movie_name + "\t/\t감독 : " + dir_name + "\t/\t 개봉일 - " + movie_open_day
            attachments_json[0]['text'] = "영화 제목 초성 : \t" + movie_chosung
            attachments_json[0].get('actions')[1].get('confirm')['text'] = "\t 개봉일 - " + movie_open_day
            attachments_json[0].get('actions')[2].get('confirm')['text'] = movie_name[0] + movie_chosung[1:]
            attachments_json[0].get('actions')[3].get('confirm')['text'] = "\t 감독 - " + dir_name

            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text="안녕하세요! 즐거운 초성 퀴즈 시간입니다. 어떤 영화의 초성인지 맞춰보세요!!",
                attachments=attachments_json
            )
            return make_response("App mention message has been sent", 200, )

        else:
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text="quiz <- 를 입력하세요",
            )
            return make_response("App mention message has been sent", 200, )


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready!!!!!!.</h1>"


if __name__ == '__main__':
    app.run(debug=True)