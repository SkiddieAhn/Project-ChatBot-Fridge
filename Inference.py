import torch
import cv2

#파일 실행전 'pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt' 로 패키지 설치필요!


def inference(img_path):
    
    #이미지 불러오기
    img=cv2.imread(img_path)

    #train된 weight로 yolov5 model불러오기
    #path에 weight 경로 넣어주기
    model=torch.hub.load('ultralytics/yolov5', 'custom',path="C:\\Users\\jemaj\\OneDrive\\바탕 화면\\종프\\best.pt")

    #inference 수행
    result=model(img,640)

    #Inference된 이미지에서 해당 영역만 추출
    crop=result.crop(save=False)

    return crop[0]['im']


