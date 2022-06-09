# ChatBot Fridge
2022년 1학기 가톨릭대학교 캡스톤 디자인 프로젝트 (프리지팀)

## 💡 Description
![frg](https://user-images.githubusercontent.com/52392658/172750686-dc39c1bd-b2ac-495f-80dd-483f0a9c835d.jpg)

카카오톡 챗봇을 이용해서 냉장고 속 식품 유통기한을 관리할 수 있습니다.
[[View](https://shacoding.com/2022/06/05/ai-%ea%b8%b0%eb%b0%98-%eb%83%89%ec%9e%a5%ea%b3%a0-%ec%9c%a0%ed%86%b5%ea%b8%b0%ed%95%9c-%ea%b4%80%eb%a6%ac-%ec%b1%97%eb%b4%87-%ec%ba%a1%ec%8a%a4%ed%86%a4-%ed%94%84%eb%a1%9c%ec%a0%9d%ed%8a%b8/)]

## ⚙ Main Function
**아이템 선택 및 리스트 확인**

> 바코드 인식, 유통기한 인식으로 식품을 선택하고 저장할 수 있습니다. <br>
> 저장된 식품을 리스트 이미지로 확인할 수 있습니다.
 
| 아이템 선택 및 리스트 확인                                                                                             |
|----------------------------------------------------------------------------------------------------------------------|
| ![number2 (1)](https://user-images.githubusercontent.com/52392658/172047083-6461cd4b-f9d1-4dbe-9c98-550b055c89bb.gif) |

## 🎞 YouTube Video
<a href="https://youtu.be/fbPuuA-hL9E" target="_blank">
<img src="https://user-images.githubusercontent.com/52392658/172044284-471fb3b0-4c52-4b47-8dcc-a270e35ef498.png" width="700" height="393"></a><br>
<strong>발표:</strong> 윤지원 팀원<br>
<strong>링크:</strong> https://youtu.be/fbPuuA-hL9E

## 🛠 Tech Stack
### 1. Server 
<strong>웹 앱:</strong> Django Framework<br>
<strong>웹 서버:</strong> Apache2 Web Server<br>
<strong>데이터베이스:</strong> SQLite3<br>
<strong>챗봇 API:</strong> Kakao I Open Builder [[View](https://i.kakao.com/)]<br>

### 2. Vision
<strong>프레임워크:</strong> pyTorch, OpenCV<br>
<strong>머신러닝 학습 환경:</strong> Colab Pro (T4, P100, 25GB RAM)<br>
<strong>머신러닝 알고리즘:</strong> YOLOv5<br>
<strong>식품 정보 API:</strong> 식품의약품안전처_유통바코드 [[View](https://www.data.go.kr/data/15064775/openapi.do)]<br>
<strong>OCR API:</strong> Google Cloud Vision [[View](https://cloud.google.com/vision/?hl=ko&utm_source=google&utm_medium=cpc&utm_campaign=japac-KR-all-ko-dr-bkws-all-all-trial-e-dr-1009882&utm_content=text-ad-none-none-DEV_c-CRE_601679911354-ADGP_Hybrid%20%7C%20BKWS%20-%20EXA%20%7C%20Txt%20~%20AI%20%26%20ML%20~%20Vision%20AI_Vision-google%20cloud%20vision-en-KWID_43700071503458155-aud-970366092687%3Akwd-203288730967&userloc_1009846-network_g&utm_term=KW_google%20cloud%20vision&gclid=CjwKCAjwkYGVBhArEiwA4sZLuJQP9_E-jUUsb1tPLLr70tAM3ljpEt5Dtz03wsK8N4Ha6mEhJlgbthoCT5wQAvD_BwE&gclsrc=aw.ds)]<br>


## 👨‍👨‍👦Team Member
| <a href="https://github.com/skiddieahn">안성현 (팀장)</a> | <a href="https://github.com/JIWON0520">윤지원</a> | <a href="https://github.com/HanInGoo">한인구</a>
| :----------: | :----------: | :----------: 
| Server | Vision | Vision |
