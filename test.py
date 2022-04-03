import torch
import os
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import cv2
import datetime
from datetime import datetime
import numpy as np
import requests

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
        model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')

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
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']='visionapi-345714-015c99714d2d.json' # key가 포함되어 있는 json파일

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


# 후처리 함수 (yyyy-mm-dd)
def result_word(str_input, infor=0):
    if infor:
        print("입력:{}".format(str_input))

    date = []
    number = []

    try:
        for i in range(0, len(str_input), 1):  # 문장에 있는 단어를 하나하나 검사하면서 0,1,2,3,4,5,6,7,8,9에 포함 되면 해당단어가 리스트에 추가된다.
            if (str_input[i] == '0' or
                    str_input[i] == '1' or
                    str_input[i] == '2' or
                    str_input[i] == '3' or
                    str_input[i] == '4' or
                    str_input[i] == '5' or
                    str_input[i] == '6' or
                    str_input[i] == '7' or
                    str_input[i] == '8' or
                    str_input[i] == '9'):
                number.append(str_input[i])

        if len(number) == 8:  # yyyy mm dd일 경우
            year = "".join(number[0:4])
            month = "".join(number[4:6])
            day = "".join(number[6:8])

            return "{0}-{1}-{2}".format(year, month, day)  # yyyy-mm-dd 형식에 맞춰서 반환

        elif len(number) == 6:  # yy mm dd일 경우
            year = "".join(number[0:2])
            month = "".join(number[2:4])
            day = "".join(number[4:6])

            return "20{0}-{1}-{2}".format(year, month, day)  # yyyy-mm-dd 형식에 맞춰서 반환

        elif len(number) == 4:  # mm dd일 경우
            month = "".join(number[0:2])
            day = "".join(number[2:4])
            return "{0}-{1}-{2}".format(datetime.today().year, month, day)  # yyyy-mm-dd 형식에 맞춰서 반환

        else:
            return 0

    except:
        return 0

def main():  # main 함수
    # 파일 이름 및 경로 설정
    FILE_NAME = '안성현(0).jpg'
    FOLDER_PATH = "pictures"
    FILE_PATH = os.path.join(FOLDER_PATH, FILE_NAME)

    # 이미지 객체 생성
    org_img = cv2.imread(FILE_PATH)

    # 인퍼런스 함수 호출
    s, img = inference(org_img)

    if s:
        # 영상 전처리 함수 호출
        pre_img = image_change(img)

        # OCR 함수 호출
        ocr_text_list = detectText(pre_img)
        print(ocr_text_list)

        # 텍스트 처리 함수 호출
        result = result_word(ocr_text_list[1])

        # OCR 성공 시 출력
        if result:
            print(result)
        else:
            print("can't find")
    
    else:
        print("can't find")


if __name__ == "__main__":
    main()
