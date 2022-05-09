import cv2
import requests
import numpy as np
import pyzbar.pyzbar as pyzbar
import json, urllib.request

# 유통기한 검색 API (1)
def BRCD_CD(apikey, startRow, endRow, BAR_BRCD_CD):
    output_list = []
    keyId = 'I2570'
    url = 'http://openapi.foodsafetykorea.go.kr/api/' + apikey + '/' + keyId + '/json/' + str(startRow) + '/' + str(
        endRow) + '/BRCD_NO=' + BAR_BRCD_CD

    data = urllib.request.urlopen(url).read()
    output = json.loads(data)
    output = output[keyId]

    try:
        output = output['row']
        output_1 = output[0]

        output_list.append(output_1['HTRK_PRDLST_NM'])
        output_list.append(output_1['HRNK_PRDLST_NM'])
        output_list.append(output_1['PRDLST_NM'])

        return output_list
    except:
        return 'no data'

    # (대분류,중분류,소분류) 리턴
    # 대분류 = HTRK_PRDLST_NM
    # 중분류 = HRNK_PRDLST_NM
    # 소분류 = PRDLST_NM

# 유통기한 검색 API (2)
def BAR_CD(apikey, startRow, endRow, BAR_BRCD_CD):
    output_list = []
    keyId = 'C005'
    url = 'http://openapi.foodsafetykorea.go.kr/api/' + apikey + '/' + keyId + '/json/' + str(startRow) + '/' + str(
        endRow) + '/BAR_CD=' + BAR_BRCD_CD

    data = urllib.request.urlopen(url).read()
    output = json.loads(data)
    output = output[keyId]

    try:
        output = output['row']
        output_1 = output[0]

        output_list.append('기타')
        output_list.append(output_1['PRDLST_DCNM'])
        output_list.append(output_1['PRDLST_NM'])

        return output_list
    except:
        return 'no data'

    # ('기타',중분류,소분류) 리턴
    # 중분류 = PRDLST_DCNM
    # 소분류 = PRDLST_NM

# 이미지 url -> cv2 이미지
def url2img(url):
    _url = url
    image_nparray = np.asarray(bytearray(requests.get(_url).content),
                               dtype=np.uint8)  # 전처리 (url image -> nparray)
    image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)  # 전처리 (nparray -> cv2 image)
    return image

# cv2 이미지 -> 바코드 문자열
def recognition(image):
    # 이미지가 너무 크면 리사이징
    if image.shape[0] >= 1000:
        image = cv2.resize(image, dsize=(0, 0), fx=0.2, fy=0.2)

    # 바코드 확인 가능한지 확인
    barcodeCnt = len(pyzbar.decode(image))

    # 확인 불가
    if barcodeCnt == 0:
        return 0
    # 확인 가능
    barcodeList = pyzbar.decode(image)
    maxArea = 0

    # 바코드가 여러 개 있으면 가장 Area가 큰 영역으로 지정
    for barcode in barcodeList:
        (_, _, w, h) = barcode.rect
        barcodeArea = w * h
        if barcodeArea > maxArea:
            maxArea = barcodeArea
            result = barcode.data.decode('utf-8')

    return result

# 바코드 문자열 -> 아이템 정보
def make_infor(barcode):
    apikey = '0acf2740895d47c4a77c'

    startRow = 1
    endRow = 1

    # 유통기한 검색 API (1)
    BRCD_CD_output = BRCD_CD(apikey, startRow, endRow, barcode)

    if BRCD_CD_output != 'no data':
        return BRCD_CD_output
    else:
        # 유통기한 검색 API (2)
        BAR_CD_output = BAR_CD(apikey, startRow, endRow, barcode)
        if BAR_CD_output != 'no data':
            return BAR_CD_output
        else:
            return 0

# 바코드 이미지 url -> 아이템 정보
def barcode_infor(url):
    # (1) 바코드 이미지 url -> 바코드 이미지
    image = url2img(url)
    # (2) 바코드 이미지 -> 바코드 문자열
    barcode = recognition(image)

    # 바코드 확인 완료
    if barcode:
        # (3) 바코드 문자열 -> 아이템 정보
            infor_list = make_infor(barcode)
            # 아이템 정보 획득 완료
            if infor_list:
                return infor_list
            # 아이템 정보를 획득하지 못 함
            else:
                return 0

    # 바코드를 확인할 수 없음
    else:
        return 0

def main():  # main 함수
    # ================================================
    # BARCODE 코드
    # 1. 카카오 이미지 URL을 cv2 이미지로 변환한다.
    # 2. phzbar 라이브러리로 바코드를 검출한다.
    # 3. 유통기한 검색 API(1,2)로 아이템 정보를 얻는다.
    # ================================================

    # 1->2->3 과정 수행
    infor_list=barcode_infor('http://dn-m.talk.kakao.com/talkm/bl41NyYKASs/vcgL0kHipWK7bZVmA4zUP1/i_f05c1ecba0ca.jpg')

    # 아이템 정보 획득 시 출력
    if infor_list:
        print(infor_list)
    else:
        print('error')

if __name__ == "__main__":
    main()