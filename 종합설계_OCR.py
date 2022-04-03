

#-----------------------------패키지-----------------------------------------------


import os, io
from google.cloud import vision
from google.cloud.vision import types
import pandas as pd
import cv2
from datetime import datetime


#----------------------------------------------------------------------------------


def image_change(image_path):# 영상처리 함수(전처리)

    image = cv2.imread(image_path) ##이미지 읽어오기

    image_gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) ## BGR 색상 이미지를 회색조 이미지로 변환

    image_blur=cv2.GaussianBlur(image_gray,ksize=(3,3),sigmaX=0) ## 가우시안블러 효과를 넣어준다.

    
    k=cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))


    erode = cv2.erode(image_blur,k) # 이미지의 빈 공간을 매꿔준다 (1)
    for i in range(2): 
        erode = cv2.erode(erode,k)


    opening=cv2.morphologyEx(erode,cv2.MORPH_OPEN,k) # 이미지의 빈 공간을 매꿔준다 (2)
    for i in range(2):
        opening=cv2.morphologyEx(opening,cv2.MORPH_OPEN,k)


    image_path = "{}_change.jpg".format(image_path) # 이미지를 저장할 경로를 지정한다.
    cv2.imwrite(image_path, opening) # 이미지를 저장한다.

    return image_path # 이미지가 존재하는 경로를 반환한다.


#----------------------------------------------------------------------------------


def detectText(img): # 이미지 인식 함수(OCR) / (구글 API 코드) 

    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'visionapi-345714-015c99714d2d.json' # key가 포함되어 있는 json파일
    client=vision.ImageAnnotatorClient()
    
    with io.open(img,'rb') as image_file:
        content = image_file.read()

    image=vision.types.Image(content=content)

    
    response=client.text_detection(image=image)
    texts=response.text_annotations

    df=pd.DataFrame(columns=['locale','description'])
    for text in texts:
        df=df.append(
            dict(
                locale=text.locale,
                description=text.description
            ),
            ignore_index=True
        )

    return df['description'][0] # 인식된 Text 반환



#----------------------------------------------------------------------------------


def result_word(str_input): # 후처리 함수 (yyyy-mm-dd) 

    date=[]
    number=[]
    
    try:  
    
        for i in range(0,len(str_input),1): # 문장에 있는 단어를 하나하나 검사하면서 0,1,2,3,4,5,6,7,8,9에 포함 되면 해당단어가 리스트에 추가된다.
            
            
                 if ( str_input[i]=='0' or
                     str_input[i]=='1' or 
                     str_input[i]=='2' or 
                     str_input[i]=='3' or 
                     str_input[i]=='4' or 
                     str_input[i]=='5' or
                     str_input[i]=='6' or
                     str_input[i]=='7' or
                     str_input[i]=='8' or
                     str_input[i]=='9'):
                
                        number.append(str_input[i]) 
                        
        if len(number)==8: # yyyy mm dd일 경우
                year="".join(number[0:4])
                month="".join(number[4:6])
                day="".join(number[6:8])
                
                return "{0}-{1}-{2}".format(year,month,day) # yyyy-mm-dd 형식에 맞춰서 반환
                
        elif len(number)==6: # yy mm dd일 경우
                year="".join(number[0:2])
                month="".join(number[2:4])
                day="".join(number[4:6])
                
                return "20{0}-{1}-{2}".format(year,month,day) # yyyy-mm-dd 형식에 맞춰서 반환

        elif len(number)==4: # mm dd일 경우
                month="".join(number[0:2])
                day="".join(number[2:4])
                return "{0}-{1}-{2}".format(datetime.today().year,month,day) # yyyy-mm-dd 형식에 맞춰서 반환

        else:
                return "다시입력하세요"

    except:
        return "Text 인식오류" # 오류가 있을 경우 반환
        


#----------------------------------------------------------------------------------
    

def main(): # main 함수
    
    FILE_NAME='24 (2).jpg' # 파일이름
    FOLDER_PATH=r"F:/exam/" # 파일 경로

    change_path=image_change(os.path.join(FOLDER_PATH, FILE_NAME)) # 영상처리 함수 호출

    output=detectText(change_path) # 이미지 인식 함수 호출

    print(result_word(output)) # 후처리 함수 호출


if __name__ == "__main__":
    main()

    
#----------------------------------------------------------------------------------
