#-*- coding: euc-kr -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json, os, random, shutil
import pandas as pd
import dataframe_image as dfi
from matplotlib import font_manager, rc
import datetime
from . import models # DB 모델
from . import fp_ip # OCR 처리
from . import fp_ip2 # 바코드 처리
from . import response_select # OCR 성공 이후 메뉴 처리

# 한글 폰트 설정
font_fname = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
font_name = font_manager.FontProperties(fname=font_fname).get_name()
rc('font', family=font_name)

# Item Type Dictionary
IT = dict()
IT['음료류']=['차','커피','과일음료','탄산음료','이온음료','발효음료','직접 입력']
IT['주류']=['맥주','소주','탁주','과일주','위스키','브랜디','직접 입력']
IT['유가공품']=['우유','저지방우유','버터','치즈','분유','요거트','직접 입력']
IT['면류']=['소면','당면','칼국수','밀면','냉면','쫄면','직접 입력']
IT['두부,묵류']=['두부','순두부','가공두부','묵','유부','곤약','직접 입력']
IT['육류']=['소고기','돼지고기','닭고기','햄','소시지','베이컨','직접 입력']
IT['수산물류']=['생선','조개','게','새우','가재','알/내장','직접 입력']
IT['즉석식품류']=['도시락','햄버거','김밥','샌드위치','수프','만두','직접 입력']
IT['과자,빵,떡류']=['과자','껌','사탕','초콜릿','빵','떡','직접 입력']
IT['빙과류']=['아이스크림','하드','슬러시','빙수','쉐이크','얼음','직접 입력']
IT['기타']=[]

# DB 일부 초기화 (id, cicode 제외)
def init_db(user):
    user.menu = user.status = user.cinum = 0
    user.citype = user.ciname = user.b_choice = user.d_choice = user.cidesc = 'none'
    user.cidate = None
    user.save()

# 올바르지 않은 입력 -> 다시 시도
def regame():
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': '올바르지 않은 입력입니다. 다시 시도해주세요.'
                }
            }],
            'quickReplies': [
                {
                'label': '다시 시도',
                'action': 'message',
                'messageText': '다시 시도'
                },
                {
                'label': '처음으로',
                'action': 'message',
                'messageText': '처음으로'
                }
            ]
        }
    })

# 에러 발생 -> 처음으로
def init_rs():
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': '올바르지 않은 입력입니다. 처음부터 다시 진행해주세요.'
                }
            }],
            'quickReplies': [
                {
                'label': '처음으로',
                'action': 'message',
                'messageText': '처음으로'
                }
            ]
        }
    })

# DataFrame Hightlight function
def draw_color_cell(x,color):
    color = f'background-color:{color}'
    return color

# date1 < date2 -> True, else -> False
def last_day(date1,date2):
    year1 = int(date1[0:4]); year2 = int(date2[0:4]);
    month1 = int(date1[5:7]); month2 = int(date2[5:7]);
    day1 = int(date1[8:10]); day2 = int(date2[8:10]);
    if year1 < year2:
        return True
    elif year1 == year2 and month1 < month2:
        return True
    elif year1 == year2 and month1 == month2 and day1 < day2:
        return True
    else:
        return False

# DB -> DataFrame -> Image URL (ip/userId/random_table.jpg)
def DB2ImageUrl(table,userId,menu):
    # table row num
    row_num = table.count()

    # DB -> DataFrame
    df = pd.DataFrame.from_records(table.values())

    # '유통기한' 날짜 리스트
    day_default_list = df[['idate']].values.tolist()
    day_list = [str(day_default_list[i][0].strftime("%Y-%m-%d")) for i in range(0, row_num)]

    # 오늘 날짜 확인
    dt_now = datetime.datetime.now()
    today = str(dt_now.date())

    # 행 이름 변경 (0~row_num-1 -> 1:num)
    df.index = [str(i) for i in range(1, row_num + 1)]

    # 이상치 처리 (유통기한 생략해서 이상치가 저장된 경우)
    for i, uday in enumerate(day_list):
        # 이상치 확인
        if uday == "2099-12-31":
            # 정렬된 상태이므로 i행 이하는 모두 이상치
            # df에서 유통기한을 ''로 변경
            for j in range(i,len(day_list)):
                df.loc[str(j+1),'idate']=''
            break

    # 메뉴 = 리스트 확인
    if menu == 2:
        # 보여줄 데이터 선택 및 데이터 프레임 열 이름 변경
        df = df[['itype', 'iname', 'idesc', 'inum', 'idate']]
        df.rename(columns={"itype": "분류", "iname": "품목", "idesc": "상세", "inum": "개수", "idate": "유통기한"}, inplace=True)

        # 유통기한이 지난 아이템은 노란색 처리
        for i, uday in enumerate(day_list):
            # 유통기한이 안 지난 아이템을 발견
            if last_day(uday,today) == False:
                # 첫 행(i=0)에서 발견 -> 모든 아이템이 유통기한 안 지남
                # 첫 행이 아닌 곳에서 발견 -> 유통기한이 지난 아이템이 한 개 이상 존재
                if i != 0:
                    idx = pd.IndexSlice
                    slice=idx[idx[:str(i)],idx[:]]
                    df = df.style.applymap(draw_color_cell, color='#ffff66', subset=slice)
                break
            # 전부 유통기한이 지난 아이템임
            elif i == row_num - 1:
                idx = pd.IndexSlice
                slice = idx[idx[:str(i+1)], idx[:]]
                df = df.style.applymap(draw_color_cell, color='#ffff66', subset=slice)

    # 메뉴 = 아이템 삭제 (만료된 아이템 확인, 코드 확인, 변경된 리스트 확인)
    else:
        # 보여줄 데이터 선택 및 데이터 프레임 열 이름 변경
        df = df[['icode','itype', 'iname', 'idesc', 'inum', 'idate']]
        df.rename(columns={"icode":"코드","itype": "분류", "iname": "품목", "idesc": "상세", "inum": "개수", "idate": "유통기한"}, inplace=True)

        # 유통기한이 지난 아이템은 노란색 처리
        for i, uday in enumerate(day_list):
            # 유통기한이 안 지난 아이템을 발견
            if last_day(uday,today) == False:
                # 첫 행(i=0)에서 발견 -> 모든 아이템이 유통기한 안 지남
                if i==0:
                    df = df.style.applymap(draw_color_cell, color='#ff6666', subset=pd.IndexSlice[:, '코드'])
                # 첫 행이 아닌 곳에서 발견 -> 유통기한이 지난 아이템이 한 개 이상 존재
                else:
                    idx = pd.IndexSlice
                    slice=idx[idx[:str(i)],idx[:]]
                    df=df.style\
                        .applymap(draw_color_cell, color='#ffff66', subset=slice)\
                        .applymap(draw_color_cell, color='#ff6666', subset=pd.IndexSlice[:, '코드'])
                break
            # 전부 유통기한이 지난 아이템임
            elif i == row_num-1:
                idx = pd.IndexSlice
                slice = idx[idx[:str(i+1)], idx[:]]
                df=df.style\
                    .applymap(draw_color_cell, color='#ffff66', subset=slice) \
                    .applymap(draw_color_cell, color='#ff6666', subset=pd.IndexSlice[:, '코드'])

    # 이미지 저장 경로 설정
    _dir = os.path.join(settings.STATIC_ROOT, userId)  # 디렉토리 경로 설정
    _random = str(random.randint(1, 100))  # 랜덤 숫자 설정
    _target = os.path.join(_dir, _random + '_table.jpg')  # 파일 경로 및 이름 설정 (랜덤으로 설정해서 파일 업데이트 문제 안 생기도록)
    _url = 'http://125.180.136.226/static/' + userId + '/' + _random + '_table.jpg'

    # 이전 데이터가 포함된 디렉토리 존재시 삭제 <강제 삭제>
    if os.path.exists(_dir):
        shutil.rmtree(_dir)
    os.mkdir(_dir)  # 설정한대로 디렉토리 생성

    # 이미지 저장
    # df -> image (encoding 필요함,/home/ubuntu/jps/jps_ve/lib/python3.8/site-packages/dataframe_image/_screenshot.py)
    dfi.export(df, _target, max_cols=-1, max_rows=-1)  # 파일 생성 (df -> image)

    return _url

# Create your views here.
def home_list(request):
    dt_now = datetime.datetime.now()
    day=dt_now.date()
    return JsonResponse({
      'server':day
    })

@csrf_exempt
def message(request):
    answer = ((request.body).decode('utf-8'))
    return_json_str = json.loads(answer)
    return_str = return_json_str['userRequest']['utterance'] # 사용자 발화
    return_id = return_json_str['userRequest']['user']['id'] # 사용자 ID
    userId=str(return_id)[0:10]
    print(return_str)

    # 회원 찾기
    try:
        user=models.User.objects.get(id=userId)
    except:
        user=0

    # 등록된 회원인 경우
    if user:
        # =================================================
        # << 메뉴 선택 창 >>
        # 발화 = '프리지' or '처음으로'
        # [메뉴 상태(menu status) 상관 없이 동작]
        # =================================================

        if (return_str == "프리지야") or (return_str == "프리지") or (return_str == "야") or (return_str == "처음으로") or (
                return_str == "처음"):

            # DB 초기화
            init_db(user)

            # response
            return JsonResponse({
                'version': "2.0",
                'template': {
                    'outputs': [{
                        'simpleText': {
                            'text': "냉장고 유통기한 관리 챗봇 '프리지'입니다.\n\n무엇을 도와드릴까요?"
                        }
                    }],
                    'quickReplies': [
                        {
                            'label': '아이템 선택',
                            'action': 'message',
                            'messageText': '아이템 선택'
                        },
                        {
                            'label': '리스트 확인',
                            'action': 'message',
                            'messageText': '리스트 확인'
                        },
                        {
                            'label': '아이템 삭제',
                            'action': 'message',
                            'messageText': '아이템 삭제'
                        },
                        {
                            'label': '회원 탈퇴',
                            'action': 'message',
                            'messageText': '회원 탈퇴'
                        }
                    ]
                }
            })

        # =================================================
        # 메뉴 선택 이후
        # =================================================

        if user.menu == 0:
            # 발화 = '아이템 선택/추가' or <특수 케이스:분류 선택 -> 품목 입력 중 "이전으로">
            if (return_str == "아이템 선택") or (return_str == "아이템 추가"):
                # DB 수정
                user.menu = 1 # --> 메뉴1
                user.save()

            # 발화 = '리스트 확인'
            elif return_str == "리스트 확인":
                # DB 수정
                user.menu = 2 # --> 메뉴2
                user.save()

            # 발화 = '아이템 삭제'
            elif return_str == "아이템 삭제":
                # DB 수정
                user.menu = 3  # --> 메뉴3
                user.save()

            # 발화 = '회원 탈퇴'
            elif return_str == "회원 탈퇴":
                # DB 수정
                user.menu = 4  # --> 메뉴4
                user.save()

            # 올바르지 않은 메뉴 입력
            else:
                # DB 초기화 및 response
                init_db(user)
                return init_rs()

        # =================================================
        # 메뉴1 ('아이템 선택' 발화 이후)
        # =================================================
        if user.menu == 1:
            # --------------------
            # 아이템 선택 방식 선정
            # --------------------
            if user.status == 0 or (user.status == 0.5 and return_str == "다시 시도") or ((user.status == 1 or user.status == 11) and return_str == "이전으로") or (user.status == 12 and return_str == "아니요"):
                # <특수 케이스> 아이템 선택 방식 결정 중 이상한 데이터 입력 -> 다시 시도
                # <특수 케이스> 아이템 선택 방식 선정 -> 이전으로
                # <특수 케이스> 아이템 선택 방식 선정 -> (바코드 전송) 바코드 사진을 전송 -> 올바르지 않은 정보 획득('아니요')
                if (user.status == 0.5 and return_str == "다시 시도") or ((user.status == 1 or user.status == 11) and return_str == "이전으로") or (user.status == 12 and return_str == "아니요"):
                    re=1
                else:
                    re=0

                # DB 수정
                user.b_choice = 'none'  # 바코드 이용 여부 초기화 ('아니요' 대비)
                user.citype = user.ciname = user.cidesc = 'none'  # 아이템 저장 정보 초기화 ('아니요' 대비)
                user.status = 0.5  # --> 메뉴 선택 완료, 아이템 선택 방식 선정 예정
                user.save()

                # 다시 시도 확인
                if re==1:
                    txt="다시 "
                else:
                    txt=""

                # response
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': "아이템 선택 방식을 "+txt+"결정해주세요!!"
                            }
                        }],
                        'quickReplies': [
                            {
                                'label': '직접 선택',
                                'action': 'message',
                                'messageText': '직접 선택'
                            },
                            {
                                'label': '바코드 전송',
                                'action': 'message',
                                'messageText': '바코드 전송'
                            },
                            {
                                'label': '처음으로',
                                'action': 'message',
                                'messageText': '처음으로'
                            }
                        ]
                    }
                })

            # -------------------------
            # 아이템 선택 방식 선정 이후
            # -------------------------
            if user.status == 0.5 or (user.status == 1 and return_str == "다시 시도") or (user.status == 2 and return_str == "이전으로") or\
                    (user.status == 11 and return_str == "다시 시도") or (user.status == 12 and return_str == "다시 시도" and user.citype == "none") or\
                    (user.status == 12 and return_str == "이전으로"):

                # <특수 케이스> (직접 선택) 이미지 분류 선택 중 잘못된 입력 -> 다시 분류 선택
                # <특수 케이스> (직접 선택) 이미지 분류 선택 -> 이미지 품목 선택 중 '이전으로' -> 다시 분류 선택
                # <특수 케이스> (바코드 전송) 바코드 사진을 전송하지 않고 이상한 입력 -> 다시 바코드 전송 요구
                # <특수 케이스> (바코드 전송) 바코드 사진을 전송 후 올바르지 않은 아이템 정보 획득 -> 이상한 데이터 입력 -> 다시 바코드 전송 요구
                # <특수 케이스> (바코드 전송) 바코드 사진을 전송 후 아이템 정보 획득 -> '이전으로' -> 다시 바코드 전송 요구

                # (1) 직접 선택
                if return_str == "직접 선택" or (user.status == 1 and return_str == "다시 시도") or (user.status == 2 and return_str == "이전으로"):
                    # DB 수정
                    user.status = 1  # --> 아이템 선택 방식 선정 완료(직접 선택), 분류 선택 예정
                    user.save()

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                "carousel": {
                                    "type": "basicCard",
                                    "items":
                                        [
                                            {
                                                "title": "음료류",
                                                "description": "(차,커피,과일/탄산/이온/발효음료)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class1.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "음료류",
                                                        "messageText": "음료류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "주류",
                                                "description": "(맥주,소주,탁주,과일주,위스키,브랜디)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class2.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "주류",
                                                        "messageText": "주류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "유가공품",
                                                "description": "(우유,버터,치즈,분유,요거트)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class3.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "유가공품",
                                                        "messageText": "유가공품"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "면류",
                                                "description": "(소면,당면,칼국수,밀면,냉면,쫄면)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class4.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "면류",
                                                        "messageText": "면류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "두부,묵류",
                                                "description": "(두부,순두부,가공두부,묵,유부,곤약)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class5.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "두부,묵류",
                                                        "messageText": "두부,묵류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "육류",
                                                "description": "(소고기,돼지고기,닭고기,햄,소시지,베이컨)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class6.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "육류",
                                                        "messageText": "육류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "수산물류",
                                                "description": "(생선,조개,게,새우,가재,알,내장)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class7.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "수산물류",
                                                        "messageText": "수산물류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "즉석식품류",
                                                "description": "(도시락,햄버거,김밥,샌드위치,수프,만두)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class8.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "즉석식품류",
                                                        "messageText": "즉석식품류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "과자,빵,떡류",
                                                "description": "(과자,껌,사탕,초콜릿,빵,떡)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class9.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "과자,빵,떡류",
                                                        "messageText": "과자,빵,떡류"
                                                    }
                                                ]
                                            },
                                            {
                                                "title": "빙과류",
                                                "description": "(아이스크림,하드,슬러시,빙수,쉐이크,얼음)",
                                                "thumbnail": {
                                                    "imageUrl": "http://125.180.136.226/static/class10.jpg"
                                                },
                                                "buttons": [
                                                    {
                                                        "action": "message",
                                                        "label": "빙과류",
                                                        "messageText": "빙과류"
                                                    }
                                                ]
                                            }, {
                                            "title": "기타",
                                            "description": "(기타 음식)",
                                            "thumbnail": {
                                                "imageUrl": "http://125.180.136.226/static/class11.jpg"
                                            },
                                            "buttons": [
                                                {
                                                    "action": "message",
                                                    "label": "기타",
                                                    "messageText": "기타"
                                                }
                                            ]
                                        }
                                        ]
                                }
                            }
                            ],
                            'quickReplies': [
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # (2) 바코드 전송
                elif return_str == "바코드 전송" or (user.status == 11 and return_str == "다시 시도") or (user.status == 12 and return_str == "이전으로") or \
                        (user.status == 12 and return_str == "다시 시도" and user.citype == "none"):

                    # DB 수정
                    user.b_choice = 'none' # 바코드 이용 여부 초기화 ('이전으로' 대비)
                    user.citype = user.ciname = user.cidesc = 'none' # 아이템 저장 정보 초기화 ('이전으로' 대비)
                    user.status = 11 # --> 아이템 선택 방식 선정 완료(바코드 전송), 바코드 이미지 전송 예정
                    user.save()

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "바코드가 포함된 이미지를 전송해주세요. 바코드가 멀리 있거나 화질이 안 좋은 이미지는 인식률이 떨어집니다."
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # 이상한 발화
                else:
                    # 다시 시작
                    return regame()

            # --------------
            # 바코드 전송 이후
            # --------------
            if user.status == 11 or (user.status == 12 and return_str == "다시 시도" and user.citype != "none") or (user.status == 5 and user.b_choice == "예" and return_str=="이전으로"):
                # <특수 케이스> 아이템 정보를 확인하는 과정에서 올바르지 않은 입력
                # <특수 케이스> (바코드 전송) 바코드 사진 처리 후 아이템 수량 선택 중 '이전으로' -> 다시 바코드 전송 요구
                if (user.status == 12 and return_str == "다시 시도" and user.citype != "none") or (user.status == 5 and user.b_choice == "예" and return_str=="이전으로"):
                    # DB 수정
                    user.status = 12  # --> 아이템 정보 획득 및 확인 예정
                    user.save()

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "올바른 아이템 정보인지 확인해주세요!!\n\n■ 분류: " + user.citype + "\n■ 품목: " + user.ciname + "\n■ 상세 내용: " + user.cidesc + "\n\n이(가) 맞습니까?"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '예',
                                    'action': 'message',
                                    'messageText': '예'
                                },
                                {
                                    'label': '아니요',
                                    'action': 'message',
                                    'messageText': '아니요'
                                },
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # <일반 케이스>
                else:
                    # 이미지가 입력으로 왔는지 확인
                    try:
                        return_img = return_json_str['userRequest']['params']['media']['url']
                        print(return_img)

                        # DB 수정
                        user.status = 12  # --> 바코드 전송 완료, 아이템 정보 획득 및 확인 예정
                        user.save()

                        # 영상이 왔을 때
                        if return_img:
                            # 바코드로 아이템 정보 획득하기
                            infor_list=fp_ip2.barcode_infor(return_img)

                            # 아이템 정보 획득 완료
                            if infor_list:
                                # DB 저장
                                user.citype=infor_list[0] # 분류
                                user.ciname=infor_list[1] # 품목
                                user.cidesc=infor_list[2] # 상세 내용
                                user.save()

                                # response
                                return JsonResponse({
                                    'version': "2.0",
                                    'template': {
                                        'outputs': [{
                                            'simpleText': {
                                                'text': "올바른 아이템 정보인지 확인해주세요!!\n\n■ 분류: " + user.citype + "\n■ 품목: " + user.ciname + "\n■ 상세 내용: " + user.cidesc + "\n\n이(가) 맞습니까?"
                                            }
                                        }],
                                        'quickReplies': [
                                            {
                                                'label': '예',
                                                'action': 'message',
                                                'messageText': '예'
                                            },
                                            {
                                                'label': '아니요',
                                                'action': 'message',
                                                'messageText': '아니요'
                                            },
                                            {
                                                'label': '이전으로',
                                                'action': 'message',
                                                'messageText': '이전으로'
                                            },
                                            {
                                                'label': '처음으로',
                                                'action': 'message',
                                                'messageText': '처음으로'
                                            }
                                        ]
                                    }
                                })

                            # 아이템 정보 획득 실패
                            else:
                                # response
                                return JsonResponse({
                                    'version': "2.0",
                                    'template': {
                                        'outputs': [{
                                            'simpleText': {
                                                'text': "아이템 정보를 확인할 수 없습니다!!"
                                            }
                                        }],
                                        'quickReplies': [
                                            {
                                                'label': '이전으로',
                                                'action': 'message',
                                                'messageText': '이전으로'
                                            },
                                            {
                                                'label': '처음으로',
                                                'action': 'message',
                                                'messageText': '처음으로'
                                            }
                                        ]
                                    }
                                })

                    # 이미지가 입력으로 오지 않음
                    except:
                        # 다시 시도
                        return regame()

            # -------------------
            # 아이템 정보 획득 이후
            # -------------------
            if user.status == 12:
                if return_str == "예":
                    # DB 수정
                    user.b_choice = "예"
                    user.status = 4  # --> 올바른 정보인지 확인 완료, 아이템 수량 선택 예정
                    user.save()
                    return_str=user.cidesc # return_str을 description으로 설정하고 아이템 수량 선택 로직으로 이동

                # '아니요'는 위에서 처리

                # 이상한 발화
                else:
                    # 다시 시도
                    return regame()

            # -------------
            # 분류 선택 이후
            # -------------
            if user.status == 1 or (user.status == 2 and return_str == "다시 시도") or ((user.status == 2.5 or user.status == 3) and return_str == "이전으로"):
                # <특수 케이스> 분류 선택 -> 품목 선택 중 올바르지 않은 입력 -> 다시 시도
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 중 "이전으로"
                if (user.status == 2 and return_str == "다시 시도") or ((user.status == 2.5 or user.status == 3) and return_str == "이전으로"):
                    return_str=user.citype

                # 분류 선택이 IT 딕셔너리 키에 존재 or '기타'
                if (return_str in IT) or (return_str == "기타"):
                    # DB 수정
                    type = return_str
                    user.citype = type
                    user.status = 2  # --> 분류 선택 완료, 품목 선택 예정
                    user.save()

                    # response (기타)
                    if return_str == "기타":
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': "품목을 직접 입력해주세요!!"
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': '이전으로',
                                        'action': 'message',
                                        'messageText': '이전으로'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })

                    # response (품목 선택)
                    if return_str in IT:
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': "아이템 품목을 선택해주세요!!"
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': IT[type][0],
                                        'action': 'message',
                                        'messageText': IT[type][0]
                                    },
                                    {
                                        'label': IT[type][1],
                                        'action': 'message',
                                        'messageText': IT[type][1]
                                    },
                                    {
                                        'label': IT[type][2],
                                        'action': 'message',
                                        'messageText': IT[type][2]
                                    },
                                    {
                                        'label': IT[type][3],
                                        'action': 'message',
                                        'messageText': IT[type][3]
                                    },
                                    {
                                        'label': IT[type][4],
                                        'action': 'message',
                                        'messageText': IT[type][4]
                                    },
                                    {
                                        'label': IT[type][5],
                                        'action': 'message',
                                        'messageText': IT[type][5]
                                    },
                                    {
                                        'label': IT[type][6],
                                        'action': 'message',
                                        'messageText': IT[type][6]
                                    },
                                    {
                                        'label': '이전으로',
                                        'action': 'message',
                                        'messageText': '이전으로'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })

                # 분류 선택이 IT 딕셔너리 키에 존재하지 않음 or '기타'도 아님
                else:
                    # 다시 시도
                    return regame()

            # -------------------
            # 품목 '직접 입력' 선택
            # -------------------
            if user.status == 2:
                # 품목 선택이 '직접 입력'인 경우
                if return_str == "직접 입력":
                    # DB 수정
                    user.status = 2.5  # --> 품목 '직접 입력' 선택, 품목 입력 예정
                    user.save()

                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "품목을 입력해주세요!!"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

            # -----------------
            # 품목 직접 입력 이후
            # -----------------
            if user.status == 2.5:
                # DB 수정
                name = return_str
                user.ciname = name
                user.status = 3  # --> 품목 선택 완료, 상세 선택 예정
                user.save()

                # return
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': '아이템의 상세 내용을 입력하시겠습니까?'
                            }
                        }],
                        'quickReplies': [
                            {
                                'label': '예',
                                'action': 'message',
                                'messageText': '예'
                            },
                            {
                                'label': '아니요',
                                'action': 'message',
                                'messageText': '아니요'
                            },
                            {
                                'label': '이전으로',
                                'action': 'message',
                                'messageText': '이전으로'
                            },
                            {
                                'label': '처음으로',
                                'action': 'message',
                                'messageText': '처음으로'
                            }
                        ]
                    }
                })

            # -------------
            # 품목 선택 이후
            # -------------
            if user.status == 2 or (user.status == 3 and return_str == "다시 시도") or (user.status == 4 and return_str == "이전으로") or (user.status == 5 and user.d_choice == "아니요" and return_str == "이전으로"):
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 중 올바르지 않은 입력 -> 다시 시도
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택(예) -> 상세 내용 입력 중 "이전으로"
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택(아니요) -> 수량 입력 중 "이전으로"
                if (user.status == 3 and return_str == "다시 시도") or (user.status == 4 and return_str == "이전으로") or (user.status == 5 and user.d_choice == "아니요" and return_str == "이전으로"):
                    return_str=user.ciname

                # 품목 선택이 IT[type]에 존재 ex) '차'가 IT['음료류']에 속함 or '기타'->사용자가 입력한 품목인 경우
                if (return_str in IT[user.citype]) or (user.citype=='기타'):
                    # DB 수정
                    name = return_str
                    user.ciname = name
                    user.status = 3 # --> 품목 선택 완료, 상세 선택 예정
                    user.save()

                    # return
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': '아이템의 상세 내용을 입력하시겠습니까?'
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '예',
                                    'action': 'message',
                                    'messageText': '예'
                                },
                                {
                                    'label': '아니요',
                                    'action': 'message',
                                    'messageText': '아니요'
                                },
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # 품목 선택이 IT[type]에 존재하지 않음
                else:
                    # 다시 시도
                    return regame()

            # ----------------
            # 상세 여부 선택 이후
            # ----------------
            if user.status == 3 or (user.status == 5 and user.d_choice == "예" and return_str == "이전으로"):
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력(예) -> 수량 입력 중 "이전으로"
                if user.status == 5 and user.d_choice == "예" and return_str == "이전으로":
                    return_str=user.d_choice

                # 올바른 상세 내용 선택
                if return_str == "예" or return_str == "아니요":
                    # DB 수정
                    choice = return_str
                    user.d_choice = choice
                    user.status = 4 # --> 상세 선택 완료, 상세 내용 입력 예정
                    user.save()

                    if return_str == "예":
                        # return
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': '상세 내용을 입력해주세요!!'
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': '이전으로',
                                        'action': 'message',
                                        'messageText': '이전으로'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })

                # 올바르지 않는 선택
                else:
                    # 다시 시도
                    return regame()

            # ----------------
            # 상세 내용 입력 이후
            # ----------------
            if user.status == 4 or (user.status == 5 and return_str == "다시 시도") or (user.status == 6 and return_str == "이전으로"):
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 중 올바르지 않은 입력 -> 다시 시도
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 -> 유통기한 방식 선택 중 "이전으로"
                if (user.status == 5 and return_str == "다시 시도") or (user.status == 6 and return_str == "이전으로"):
                    return_str=user.cidesc # return_str='x' or description

                # 상세 내용을 입력하지 않아 이 조건문으로 넘어온 경우
                if return_str == "아니요":
                    return_str="" # 상세 내용: ''

                # DB 수정
                desc = return_str
                user.cidesc=desc
                user.status = 5  # --> 상세 내용 입력 완료, 수량 입력 예정
                user.save()

                # return
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': "아이템 수량을 선택해주세요!!\n\n(3개 이상이면 직접 수량 입력)"
                            }
                        }],
                        'quickReplies': [
                            {
                                'label': '1개',
                                'action': 'message',
                                'messageText': '1개'
                            },
                            {
                                'label': '2개',
                                'action': 'message',
                                'messageText': '2개'
                            },
                            {
                                'label': '이전으로',
                                'action': 'message',
                                'messageText': '이전으로'
                            },
                            {
                                'label': '처음으로',
                                'action': 'message',
                                'messageText': '처음으로'
                            }
                        ]
                    }
                })

            # -------------
            # 수량 선택 이후
            # -------------
            if user.status == 5 or (user.status == 6 and return_str == "다시 시도") or (user.status >= 7 and (return_str == "이전으로" or return_str == "없음")):
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 -> 유통기한 방식 선택 중 올바르지 않은 입력 -> 다시 시도
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 -> 유통기한 방식 선택 -> 유통기한 처리 중 잘못된 입력 -> 다시 시도
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 -> 유통기한 방식 선택 -> 유통기한 처리 중 "이전으로"
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 -> 유통기한 방식 선택 -> 유통기한 처리 중 "없음"
                if (user.status == 6 and return_str == "다시 시도") or (user.status >= 7 and (return_str == "이전으로" or return_str == "없음")):
                    return_str=str(user.cinum) # return_str=str(num)
                    re=1
                else:
                    re=0

                # 사용자가 수를 입력한 경우
                try:
                    # 입력된 수량 뒤에 "개" 추가
                    if return_str[-1] != "개":
                        return_str += "개"

                    # 의미있는 수치인 경우
                    if int(return_str[0:-1]) > 0:
                        num = int(return_str[0:-1])

                        # DB 수정
                        user.cinum = num
                        user.status = 6 # --> 수량 입력 완료, 유통기한 입력 방식 선택 예정
                        user.save()

                        # 다시 선택하는 경우
                        if re==1:
                            txt="다시 "
                        else:
                            txt=""

                        # response
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': '유통기한 입력 방식을 '+txt+'선택해주세요!!'
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': '이미지 전송',
                                        'action': 'message',
                                        'messageText': '이미지'
                                    },
                                    {
                                        'label': '날짜 선택',
                                        'action': 'message',
                                        'messageText': '날짜'
                                    },
                                    {
                                        'label': '유통기한 생략',
                                        'action': 'message',
                                        'messageText': '유통기한 생략'
                                    },
                                    {
                                        'label': '이전으로',
                                        'action': 'message',
                                        'messageText': '이전으로'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })

                    # 의미없는 수치인 경우
                    else:
                        # 다시 시도
                        return regame()

                # 사용자가 수를 입력하지 않은 경우
                except:
                    # 다시 시도
                    return regame()

            # -------------------------
            # 유통기한 입력 방식 선택 이후
            # -------------------------
            if user.status == 6 or (user.status >= 7 and return_str == "다시 시도"):
                # <특수 케이스> 분류 선택 -> 품목 선택 -> 상세 선택 -> 상세 내용 입력 -> 수량 입력 -> 유통기한 방식 선택(이미지) -> 이미지 전송 안 함 -> 다시 시도
                if user.status >= 7 and return_str == "다시 시도":
                    return_str = "이미지"

                # 날짜 선택 방식
                if return_str == "날짜":
                    # DB 수정
                    user.status = 7  # --> 유통기한 입력 방식 선택 완료, 날짜 지정 예정
                    user.save()

                    # 사용자 발화가 날짜인지 확인
                    try:
                        return_day=return_json_str['action']['detailParams']['date']['origin']
                        print(return_day)
                        if return_day:
                            print('day exist!!')
                            # DB 저장
                            user.cidate=return_day
                            user.save()
                            newItem = models.Item(user=user, icode=user.cicode, itype=user.citype, iname=user.ciname, idesc=user.cidesc, inum=user.cinum, idate=user.cidate)
                            newItem.save()
                            user.cicode+=1
                            user.save()

                            # DB 초기화
                            init_db(user)

                            # response
                            return JsonResponse({
                                'version': "2.0",
                                'template': {
                                    'outputs': [{
                                        'simpleText': {
                                            'text': "아이템 저장이 완료되었습니다!!"
                                        }
                                    }],
                                    'quickReplies': [
                                        {
                                            'label': '리스트 확인',
                                            'action': 'message',
                                            'messageText': '리스트 확인'
                                        },
                                        {
                                            'label': '아이템 추가',
                                            'action': 'message',
                                            'messageText': '아이템 추가'
                                        },
                                        {
                                            'label': '처음으로',
                                            'action': 'message',
                                            'messageText': '처음으로'
                                        },
                                    ]
                                }
                            })

                    # 사용자 발화가 날짜가 아님 (에러)
                    except:
                        # DB 초기화 및 response
                        init_db(user)
                        return init_rs()

                # 이미지 선택 방식
                elif return_str == "이미지":
                    # DB 수정
                    user.status = 7  # --> 유통기한 입력 방식 선택 완료, 이미지 전송 예정
                    user.save()

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "유통기한이 포함된 이미지를 전송해주세요. 글자가 너무 많거나 화질이 안 좋은 이미지는 인식률이 떨어집니다.\n\n(주의) 5초 이상 반응이 없으면 '이전으로'를 입력해서 다시 시도해주세요!!"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # 유통기한 생략
                elif return_str == "유통기한 생략":
                    # DB 수정
                    user.status = 7  # --> 유통기한 입력 방식 선택 완료, 생략하고 저장할 예정
                    user.save()

                    # 이상치 저장 ('DB2ImageUrl'함수에서 처리함)
                    newItem = models.Item(user=user, icode=user.cicode, itype=user.citype, iname=user.ciname,
                                          idesc=user.cidesc, inum=user.cinum, idate="2099-12-31")
                    newItem.save()
                    user.cicode += 1
                    user.save()

                    # DB 초기화
                    init_db(user)

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "아이템 저장이 완료되었습니다!!"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '리스트 확인',
                                    'action': 'message',
                                    'messageText': '리스트 확인'
                                },
                                {
                                    'label': '아이템 추가',
                                    'action': 'message',
                                    'messageText': '아이템 추가'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                },
                            ]
                        }
                    })

                # 의미없는 입력인 경우
                else:
                    # 다시 시도
                    return regame()

            # --------------------------
            # OCR 처리할 이미지 전송 이후
            # --------------------------
            if user.status == 7:
                # 사용자 발화가 영상인지 확인
                try:
                    return_img = return_json_str['userRequest']['params']['media']['url']
                    print(return_img)

                    # 영상이 왔을 때
                    if return_img:
                        # DB 수정
                        user.status = 8  # --> 이미지 전송 완료, 유통기한 선택 예정
                        user.save()

                        # =================================================
                        # OCR 코드
                        # 1. 카카오 이미지 URL을 cv2 이미지로 변환한다.
                        # 2. YOLOv5 인퍼런스를 통해 유통기한 이미지를 얻는다.
                        # 3. 영상처리를 통해 유통기한 이미지를 강조한다.
                        # 4. 구글 OCR로 텍스트를 찾는다.
                        # 5. 텍스트를 날짜 형식으로 변환한다.
                        # =================================================
                        ocr_result = 0
                        org_img = fp_ip.url2img(return_img)  # (1)
                        s, img = fp_ip.inference(org_img)  # (2)

                        # YOLOv5 Inference에서 올바르게 찾음
                        if s == 1:
                            pre_img = fp_ip.image_change(img)  # (3)
                            ocr_list = fp_ip.detectText(pre_img)  # (4)
                            # 구글 OCR API에서 올바르게 찾음
                            if len(ocr_list) >= 2:
                                ocr_result = fp_ip.result_word(ocr_list)  # (5)
                            print(ocr_result)

                            # 처리한 이미지 및 데이터는 삭제
                            del img
                            del pre_img
                            del ocr_list

                        # 올바른 날짜를 반환한 경우
                        if ocr_result != 0:
                            # make list and sorting
                            ocr_result=list(ocr_result)
                            ocr_result.sort()
                            # split
                            size = len(ocr_result)
                            dates = [[0 for col in range(3)] for row in range(size)]
                            for i in range(size):
                                year, month, date = fp_ip.ocr_split(ocr_result[i])
                                dates[i][0] = year
                                dates[i][1] = month
                                dates[i][2] = date

                            # response
                            if size == 1:
                                return response_select.one(dates,ocr_result)
                            elif size == 2:
                                return response_select.two(dates,ocr_result)
                            elif size == 3:
                                return response_select.three(dates,ocr_result)
                            elif size == 4:
                                return response_select.four(dates,ocr_result)
                            elif size == 5:
                                return response_select.five(dates,ocr_result)
                            elif size == 6:
                                return response_select.six(dates,ocr_result)
                            elif size == 7:
                                return response_select.seven(dates,ocr_result)
                            elif size == 8:
                                return response_select.eight(dates,ocr_result)
                            elif size == 9:
                                return response_select.nine(dates,ocr_result)
                            else:
                                return response_select.ten(dates,ocr_result)

                        # 올바른 날짜를 반환하지 못한 경우
                        else:
                            print('ocr fail')
                            # response
                            return JsonResponse({
                                'version': "2.0",
                                'template': {
                                    'outputs': [{
                                        'simpleText': {
                                            'text': "유통기한을 확인할 수 없습니다!!"
                                        }
                                    }],
                                    'quickReplies': [
                                        {
                                            'label': '이전으로',
                                            'action': 'message',
                                            'messageText': '이전으로'
                                        },
                                        {
                                            'label': '처음으로',
                                            'action': 'message',
                                            'messageText': '처음으로'
                                        }
                                    ]
                                }
                            })

                # 사용자 발화가 영상이 아님
                except:
                    # 다시 시도
                    return regame()


            # --------------------------
            # OCR로 나온 유통기한 선택 이후
            # --------------------------
            if user.status == 8:
                # 유통기한을 선택했으면 try문이 정상 작동됨
                try:
                    # DB 저장
                    user.cidate = return_str
                    user.save()
                    newItem = models.Item(user=user, icode=user.cicode, itype=user.citype, iname=user.ciname,
                                          idesc=user.cidesc, inum=user.cinum, idate=user.cidate)
                    newItem.save()
                    user.cicode += 1
                    user.save()

                    # DB 초기화
                    init_db(user)

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "아이템 저장이 완료되었습니다!!"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '리스트 확인',
                                    'action': 'message',
                                    'messageText': '리스트 확인'
                                },
                                {
                                    'label': '아이템 추가',
                                    'action': 'message',
                                    'messageText': '아이템 추가'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                },
                            ]
                        }
                    })

                # 유통기한을 선택하지 않음
                except:
                    # 다시 시도 (이미지 입력부터)
                    return regame()


        # =================================================
        # 메뉴2 ('리스트 확인' 발화 이후)
        # =================================================

        if user.menu == 2:
            # ---------------
            # ItemDB 유무 확인
            # ---------------
            table = models.Item.objects.filter(user=userId).order_by('idate')
            if table.exists():
                pass
            else:
                table = 0

            # 아이템 데이터가 존재 x
            if table == 0:
                # DB 초기화
                init_db(user)

                # response
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': "저장된 데이터가 없습니다!"
                            }
                        }],
                        'quickReplies': [{
                            'label': '처음으로',
                            'action': 'message',
                            'messageText': '처음으로'
                        }]
                    }
                })

            # -------------
            # 메뉴 선택 이후
            # -------------
            if user.status == 0:
                # DB 수정
                user.status = 1  # --> 메뉴 선택 완료, 리스트 리턴
                user.save()

                # DB -> Image url
                _url = DB2ImageUrl(table, userId, user.menu)

                # DB 초기화 <메뉴1로 갈 수 있도록>
                init_db(user)

                # response
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleImage': {
                                "imageUrl": _url,
                                "altText": "테이블"
                            }
                        }],
                        'quickReplies': [
                            {
                                'label': '아이템 추가',
                                'action': 'message',
                                'messageText': '아이템 추가'
                            },
                            {
                                'label': '처음으로',
                                'action': 'message',
                                'messageText': '처음으로'
                            }
                        ]
                    }
                })


        # =================================================
        # 메뉴3 ('아이템 삭제' 발화 이후)
        # =================================================

        if user.menu == 3:
            # ---------------
            # ItemDB 유무 확인
            # ---------------
            table = models.Item.objects.filter(user=userId).order_by('idate')
            if table.exists():
                pass
            else:
                table = 0

            # 아이템 데이터가 존재 x
            if table == 0:
                # DB 초기화
                init_db(user)

                # response
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': "저장된 데이터가 없습니다!"
                            }
                        }],
                        'quickReplies': [{
                            'label': '처음으로',
                            'action': 'message',
                            'messageText': '처음으로'
                        }]
                    }
                })

            # -------------
            # 메뉴 선택 이후
            # -------------
            if user.status == 0 or ((user.status == 1 or user.status == 2) and return_str == "다시 시도") or ((user.status >= 2 or user.status <= 4) and return_str == "이전으로"):
                # DB 수정
                user.status = 1  # --> 메뉴 선택 완료, '만료된 아이템 확인', '만료된 아이템 삭제', '한 개씩 삭제' 선택 예정
                user.save()

                # response
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': "1. 유통기한이 만료된 아이템을 한 번에 삭제할 수 있습니다!\n\n2. 코드를 입력해서 아이템을 한 개씩 삭제할 수 있습니다!"
                            }
                        }],
                        'quickReplies': [
                            {
                                'label': '만료된 아이템 확인',
                                'action': 'message',
                                'messageText': '만료된 아이템 확인'
                            },
                            {
                                'label': '만료된 아이템 삭제',
                                'action': 'message',
                                'messageText': '만료된 아이템 삭제'
                            },
                            {
                                'label': '한 개씩 삭제',
                                'action': 'message',
                                'messageText': '한 개씩 삭제'
                            },
                            {
                                'label': '처음으로',
                                'action': 'message',
                                'messageText': '처음으로'
                            }
                        ]
                    }
                })

            # ------------------------------------
            # '만료된 아이템' or '한 개씩 삭제' 선택 완료
            # ------------------------------------
            if user.status == 1 or ((user.status == 3 or user.status == 4) and return_str == "다시 시도"):
                if return_str == "만료된 아이템 확인" or return_str == "만료된 아이템 삭제":
                    # DB 수정
                    user.status = 2  # --> (1) '만료된 아이템 확인' or (2) '만료된 아이템 삭제' 선택 완료, 만료 아이템 확인 및 삭제
                    user.save()

                elif return_str == "한 개씩 삭제" or ((user.status == 3 or user.status == 4) and return_str == "다시 시도"):
                    # DB 수정
                    user.status = 3 # --> (3) '한 개씩 삭제' 선택 완료, '코드 확인' 입력 or 코드 입력 예정
                    user.save()

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "코드를 입력하면 해당 아이템이 삭제됩니다!\n\nex) '3' 입력\n(코드를 모르면 '코드 확인' 후 진행!)"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '코드 확인',
                                    'action': 'message',
                                    'messageText': '코드 확인'
                                },
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                else:
                    # 다시 시도
                    return regame()



            # ---------------------------------
            # 만료된 아이템 확인/삭제 선택 이후
            # ---------------------------------
            if user.status == 2:
                if return_str == "만료된 아이템 확인":
                    # 만료된 유통기한에 대한 테이블 생성
                    dt_now = datetime.datetime.now()
                    today = dt_now.date()
                    end_table = models.Item.objects.filter(user=userId, idate__lt=today).order_by('idate')  # __lt: <

                    # 만료된 아이템이 있으면 보여줌
                    if end_table.exists():
                        # DB -> Image url
                        _url = DB2ImageUrl(end_table, userId, user.menu)

                        # response
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleImage': {
                                        "imageUrl": _url,
                                        "altText": "테이블"
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': '만료된 아이템 삭제',
                                        'action': 'message',
                                        'messageText': '만료된 아이템 삭제'
                                    },
                                    {
                                        'label': '이전으로',
                                        'action': 'message',
                                        'messageText': '이전으로'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })

                    # 만료된 아이템이 없음
                    else:
                        # response
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': "만료된 아이템이 없습니다!"
                                    }
                                }],
                                'quickReplies': [{
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },{
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }]
                            }
                        })

                elif return_str == "만료된 아이템 삭제":
                    # 만료된 유통기한에 대한 테이블로 변경
                    dt_now = datetime.datetime.now()
                    today = dt_now.date()
                    end_table = models.Item.objects.filter(user=userId, idate__lt=today).order_by('idate')  # __lt: <

                    # 만료된 아이템이 있으면 삭제
                    if end_table.exists():
                        # delete
                        end_table.delete()
                        # response
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': "만료된 아이템(들)이 삭제되었습니다!!"
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': '변경된 리스트 확인',
                                        'action': 'message',
                                        'messageText': '변경된 리스트 확인'
                                    },
                                    {
                                        'label': '이전으로',
                                        'action': 'message',
                                        'messageText': '이전으로'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })

                    # 만료된 아이템이 없음
                    else:
                        # response
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': "만료된 아이템이 없습니다!"
                                    }
                                }],
                                'quickReplies': [{
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                }, {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }]
                            }
                        })

                # 일반 리스트 반환
                elif return_str == "변경된 리스트 확인":
                    # DB -> Image url
                    _url = DB2ImageUrl(table, userId, user.menu)

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleImage': {
                                    "imageUrl": _url,
                                    "altText": "테이블"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # 이상한 발화
                else:
                    # 다시 시도
                    return regame()


            # -------------------------------
            # 코드 입력 or '코드 확인' 입력 이후
            # -------------------------------
            if user.status >= 3:
                # '코드 확인' or '변경된 리스트 확인' 발화 처리
                if (return_str == "코드 확인") or (return_str == "변경된 리스트 확인"):
                    # DB 수정
                    user.status = 4  # --> '코드 확인' 완료, 리스트 리턴
                    user.save()

                    # DB -> Image url
                    _url = DB2ImageUrl(table,userId,user.menu)

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleImage': {
                                    "imageUrl": _url,
                                    "altText": "테이블"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '이전으로',
                                    'action': 'message',
                                    'messageText': '이전으로'
                                },
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # 아이템 코드로 리스트 데이터 삭제 (DB 레코드 삭제), 번외
                else:
                    # 아이템 코드가 입력으로 왔는지 확인
                    try:
                        code = int(return_str)
                        # 유효한 코드인지 확인 (사용자 ID와 아이템 CODE로 삭제할 레코드 찾기)
                        record = models.Item.objects.get(user=userId, icode=code)

                        if record:
                            # DB 수정
                            user.status = 4  # --> 코드 입력 완료, 코드에 해당되는 레코드 삭제
                            user.save()

                            # 삭제할 아이템의 품목
                            name = str(record.iname)
                            # delete
                            record.delete()
                            # response
                            return JsonResponse({
                                'version': "2.0",
                                'template': {
                                    'outputs': [{
                                        'simpleText': {
                                            'text': str(code) + "번 아이템("+name+")이 삭제되었습니다!!\n\n코드 입력 시 추가 삭제가 가능합니다!"
                                        }
                                    }],
                                    'quickReplies': [
                                        {
                                            'label': '변경된 리스트 확인',
                                            'action': 'message',
                                            'messageText': '변경된 리스트 확인'
                                        },
                                        {
                                            'label': '이전으로',
                                            'action': 'message',
                                            'messageText': '이전으로'
                                        },
                                        {
                                            'label': '처음으로',
                                            'action': 'message',
                                            'messageText': '처음으로'
                                        }
                                    ]
                                }
                            })

                        # 에러
                        else:
                            # 다시 시도
                            return JsonResponse({
                                'version': "2.0",
                                'template': {
                                    'outputs': [{
                                        'simpleText': {
                                            'text': '유효하지 않은 코드입니다. 다시 시도해주세요.'
                                        }
                                    }],
                                    'quickReplies': [
                                        {
                                            'label': '다시 시도',
                                            'action': 'message',
                                            'messageText': '다시 시도'
                                        },
                                        {
                                            'label': '처음으로',
                                            'action': 'message',
                                            'messageText': '처음으로'
                                        }
                                    ]
                                }
                            })

                    # 유효하지 않은 코드
                    except:
                        # 다시 시도
                        return JsonResponse({
                            'version': "2.0",
                            'template': {
                                'outputs': [{
                                    'simpleText': {
                                        'text': '유효하지 않은 코드입니다. 다시 시도해주세요.'
                                    }
                                }],
                                'quickReplies': [
                                    {
                                        'label': '다시 시도',
                                        'action': 'message',
                                        'messageText': '다시 시도'
                                    },
                                    {
                                        'label': '처음으로',
                                        'action': 'message',
                                        'messageText': '처음으로'
                                    }
                                ]
                            }
                        })


        # =================================================
        # 메뉴4 ('회원 탈퇴' 발화 이후)
        # =================================================

        if user.menu == 4:
            # -------------
            # 메뉴 선택 이후
            # -------------
            if user.status == 0 or (user.status==1 and return_str=="다시 시도"):
                # DB 수정
                user.status = 1  # --> 메뉴 선택 완료, 탈퇴 여부 되묻기 예정
                user.save()

                # response
                return JsonResponse({
                    'version': "2.0",
                    'template': {
                        'outputs': [{
                            'simpleText': {
                                'text': "회원 탈퇴 시 모든 데이터가 삭제됩니다.\n\n정말 탈퇴하시겠습니까?"
                            }
                        }],
                        'quickReplies': [
                            {
                                'label': '예',
                                'action': 'message',
                                'messageText': '예'
                            },
                            {
                                'label': '아니요',
                                'action': 'message',
                                'messageText': '아니요'
                            }
                        ]
                    }
                })

            # -----------------
            # 탈퇴 여부 선택 이후
            # -----------------
            if user.status == 1:
                # 탈퇴한다고 함
                if return_str == "예":
                    # DB 수정
                    user.status = 2  # --> 탈퇴 여부 선택 완료, 탈퇴 처리 진행
                    user.save()

                    # 삭제
                    user.delete()

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "탈퇴가 완료되었습니다!"
                                }
                            }]
                        }
                    })

                # 탈퇴하지 않는다고 함
                elif return_str == "아니요":
                    # DB 수정
                    user.status = 2  # --> 탈퇴 여부 선택 완료, 탈퇴 취소 처리 진행
                    user.save()

                    # DB 초기화
                    init_db(user)

                    # response
                    return JsonResponse({
                        'version': "2.0",
                        'template': {
                            'outputs': [{
                                'simpleText': {
                                    'text': "탈퇴가 취소되었습니다!"
                                }
                            }],
                            'quickReplies': [
                                {
                                    'label': '처음으로',
                                    'action': 'message',
                                    'messageText': '처음으로'
                                }
                            ]
                        }
                    })

                # 번외
                else:
                    # 다시 시도
                   return regame()

        # =================================================
        # < 메뉴 관련 코드 끝 >
        # =================================================

        # 프리지를 부른 것도 아니고 탈퇴도 아니고 메뉴도 아닌 발화
        else:
            # DB 초기화 및 response
            init_db(user)
            return init_rs()


    # 등록되지 않은 회원인 경우
    else:
        # 회원가입
        if (return_str == "프리지야") or (return_str == "프리지") or (return_str == "야"):
            new=models.User(id=userId)
            new.save()
            return JsonResponse({
                'version': "2.0",
                'template': {
                    'outputs': [{
                        'simpleText': {
                            'text': "회원가입 완료!!\n프리지를 다시 부르고 이용해주세요!"
                        }
                    }],
                    'quickReplies': [{
                        'label': '프리지~!',
                        'action': 'message',
                        'messageText': '프리지'
                    }]
                }
            })

        # 회원가입 권유
        else:
            return JsonResponse({
                'version': "2.0",
                'template': {
                    'outputs': [{
                        'simpleText': {
                            'text': "등록되지 않은 사용자입니다. '프리지'를 불러 사용자 등록을 해주세요!! \n\nex) '프리지' 전송"
                        }
                    }]
                }
            })





