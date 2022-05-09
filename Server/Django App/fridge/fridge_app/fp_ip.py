import torch
import os
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import cv2
import datetime
from datetime import datetime
import numpy as np
import requests

# model은 글로벌 변수로 선언해서 어떤 한 사용자가 모델을 생성하면 다음 사용자는 생성된 모델을 사용하도록 함
# 서버의 전역변수는 모든 클라이언트가 공통으로 사용하기 때문!!
global model
model = 0

# 이미지 url -> cv2 이미지
def url2img(url):
    _url = url
    image_nparray = np.asarray(bytearray(requests.get(_url).content),
                               dtype=np.uint8)  # 전처리 (url image -> nparray)
    image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)  # 전처리 (nparray -> cv2 image)
    return image

# 인퍼런스 함수
def inference(img):
    try:
        # train된 weight로 yolov5 model불러오기
        # path에 weight 경로 넣어주기
        global model
        if model==0:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path='/home/ahnsunghyun/jps/fridge/fridge_app/best.pt')

        # inference 수행
        with torch.no_grad():
            result = model(img, 640)

        # Inference된 이미지에서 해당 영역만 추출
        crop = result.crop(save=False)

        # memory 초기화 및 캐시 삭제
        del result
        torch.cuda.empty_cache()

        return 1, crop[0]['im']

    except:
        return 0, 0

# 영상처리 함수(전처리)
def image_change(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  ## BGR 색상 이미지를 회색조 이미지로 변환
    image_blur = cv2.GaussianBlur(image_gray, ksize=(3, 3), sigmaX=0)  ## 가우시안블러 효과를 넣어준다.

    k = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

    erode = cv2.erode(image_blur, k)  # 이미지의 빈 공간을 매꿔준다 (1)from matplotlib import pyplot as plt
    for i in range(2):
        erode = cv2.erode(erode, k)

    opening = cv2.morphologyEx(erode, cv2.MORPH_OPEN, k)  # 이미지의 빈 공간을 매꿔준다 (2)
    for i in range(2):
        opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, k)

    output_img = opening

    return output_img

# openCV Image -> Bytes
def image_to_bts(frame):
    _, bts = cv2.imencode('.webp', frame)
    bts = bts.tostring()
    return bts

# 이미지 인식 함수(OCR) / (구글 API 코드)
def detectText(img,infor=0):

    # enroll environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']='/home/ahnsunghyun/jps/fridge/fridge_app/visionapi-sha.json' # key가 포함되어 있는 json파일

    # make client object
    client=vision_v1.ImageAnnotatorClient()

    # image -> bytes -> ocr image
    content=image_to_bts(img)
    image=types.Image(content=content)

    # text detection and recognition
    response=client.text_detection(image=image)
    texts=response.text_annotations

    if infor:
        # print text_annotation
        for idx,text in enumerate(texts):
            print('{}) {}'.format(idx+1,text.description))
            vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
            print('bounds: {}\n'.format(','.join(vertices)))

    # make list with description
    list=[]
    for text in texts:
        list.append(text.description)

    return list


# string -> number string
def change_num(string):
    nstring = ""
    # 문장에 있는 단어를 하나하나 검사하면서 0,1,2,3,4,5,6,7,8,9에 포함 되면 해당단어가 리스트에 추가된다.
    for i in range(0, len(string)):
        if (string[i] == '0' or
                string[i] == '1' or
                string[i] == '2' or
                string[i] == '3' or
                string[i] == '4' or
                string[i] == '5' or
                string[i] == '6' or
                string[i] == '7' or
                string[i] == '8' or
                string[i] == '9'):
            nstring += string[i]

    return nstring


# number string -> date string
def change_date(nstring):
    # number string의 크기
    size = len(nstring)

    # 리턴할 string array
    dstring = []

    # 예외 데이터 (해외 주류)
    if size == 8 and date_check(nstring[4:8], nstring[2:4], nstring[0:2]):
        dstring.append("{0}-{1}-{2}".format(nstring[4:8], nstring[2:4], nstring[0:2]))  # yyyy-mm-dd 형식에 맞춰서 반환

    # 일반 데이터
    else:
        # 충분한 정보가 없는 경우
        if size < 4:
            dstring.append("0000-00-00")

        # 충분한 정보가 있는 경우
        if size == 4 or size >= 5:  # mm dd일 경우, mm dd outlier, outlier mm dd일 경우
            # 앞에서 정보 얻기
            month = "".join(nstring[0:2])
            day = "".join(nstring[2:4])
            dstring.append("{0}-{1}-{2}".format(datetime.today().year, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환
            dstring.append("{0}-{1}-{2}".format(datetime.today().year + 1, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환
            # size가 5이상이면 뒤에서도 정보 얻음
            if size >= 5:
                month = "".join(nstring[-4:-2])
                day = "".join(nstring[-2:])
                dstring.append("{0}-{1}-{2}".format(datetime.today().year, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환
                dstring.append("{0}-{1}-{2}".format(datetime.today().year + 1, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환

        if size == 6 or size >= 7:  # yy mm dd일 경우, yy mm dd outlier, outlier yy mm dd일 경우
            # 앞에서 정보 얻기
            year = "".join(nstring[0:2])
            month = "".join(nstring[2:4])
            day = "".join(nstring[4:6])
            dstring.append("20{0}-{1}-{2}".format(year, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환
            # size가 7이상이면 뒤에서도 정보 얻음
            if size >= 7:
                year = "".join(nstring[-6:-4])
                month = "".join(nstring[-4:-2])
                day = "".join(nstring[-2:])
                dstring.append("20{0}-{1}-{2}".format(year, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환

        if size >= 8: # yyyy mm dd일 경우, yyyy mm dd outlier, outlier yyyy mm dd일 경우
            year = "".join(nstring[0:4])
            month = "".join(nstring[4:6])
            day = "".join(nstring[6:8])
            dstring.append("{0}-{1}-{2}".format(year, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환
            # size가 9 이상이면 뒤에서도 정보 얻음
            if size >= 9:
                year = "".join(nstring[-8:-4])
                month = "".join(nstring[-4:-2])
                day = "".join(nstring[-2:])
                dstring.append("{0}-{1}-{2}".format(year, month, day))  # yyyy-mm-dd 형식에 맞춰서 반환

    return dstring


# 올바른 유통기한인지 확인
def date_check(year, month, day):
    year = int(year)
    month = int(month)
    day = int(day)

    # -10~+10년 사이인 유톻기한만 처리
    interval_start = datetime.today().year - 10
    interval_end = datetime.today().year + 10

    if year < interval_start or year > interval_end:
        return 0

    # 올바른 월과 일인지 확인
    if month >= 1 and month <= 12:
        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
            if day >= 1 and day <= 31:
                return 1
        elif month == 4 or month == 6 or month == 9 or month == 11:
            if day >= 1 and day <= 30:
                return 1
        elif month == 2:
            # 윤년 판별
            if (year % 100 != 0 and year % 4 == 0) or (year % 400 == 0):
                if day >= 1 and day <= 29:
                    return 1
            elif day >= 1 and day <= 28:
                return 1
    return 0


# 후처리 함수 (yyyy-mm-dd)
def result_word(ocr_list):
    n = len(ocr_list)  # ocr_list의 크기

    n_list = []  # number string list
    d_list = []  # date string list
    a_list = set([])  # available date string list (set)

    # string -> number string
    for i in range(0, n - 1):
        n_list.append(change_num(ocr_list[i + 1]))
    # 정보가 나눠져 있는 경우를 대비해서 합칩 ex) 22,10,11
    if n == 3:
        n_list.append(change_num(ocr_list[1] + ocr_list[2]))
    elif n == 4:
        n_list.append(change_num(ocr_list[1] + ocr_list[2]))
        n_list.append(change_num(ocr_list[2] + ocr_list[3]))
        n_list.append(change_num(ocr_list[1] + ocr_list[2] + ocr_list[3]))

    # number string -> date string (length:5,7,9이상 -> any date string return)
    for i in range(len(n_list)):
        c_d_output = change_date(n_list[i])
        for j in range(len(c_d_output)):
            d_list.append(c_d_output[j])

    # check availability
    for i in range(len(d_list)):
        # year, month, day of list[i]
        year = d_list[i][0:4]
        month = d_list[i][5:7]
        day = d_list[i][8:10]
        # check if date string is available
        # if date string is available -> store date to a_list
        if date_check(year, month, day):
            a_list.add(d_list[i])

    # 최대 10개 후보 리턴
    if len(a_list) >= 10:
        return a_list[0:10]
    elif len(a_list) > 0:
        return a_list
    else:
        return 0


# 최종 출력에 필요한 변수 리턴
def ocr_split(ocr_result):
    year = ocr_result[0:4]
    month = ocr_result[5:7]
    date = ocr_result[8:10]

    if month[0]=='0':
        month=ocr_result[6]
    if date[0]=='0':
        date=ocr_result[9]

    return year, month, date

def main():  # main 함수
    # =================================================
    # OCR 코드
    # 1. 카카오 이미지 URL을 cv2 이미지로 변환한다.
    # 2. YOLOv5 인퍼런스를 통해 유통기한 이미지를 얻는다.
    # 3. 영상처리를 통해 유통기한 이미지를 강조한다.
    # 4. 구글 OCR로 텍스트를 찾는다.
    # 5. 텍스트를 날짜 형식으로 변환한다.
    # =================================================

    # 이미지 객체 생성
    org_img=url2img('http://dn-m.talk.kakao.com/talkm/bl436znhuQh/Qe2B357aKIVCQqv4nPA14K/i_02b9b3aa57f1.jpg')

    # 인퍼런스 함수 호출
    check,img = inference(org_img)

    # 영상 전처리 함수 호출
    pre_img = image_change(img)

    # OCR 함수 호출
    ocr_text_list = detectText(pre_img)

    # 텍스트 처리 함수 호출
    result = result_word(ocr_text_list)

    # OCR 성공 시 출력
    if result:
        print(result)
    else:
        print('error')


if __name__ == "__main__":
    main()