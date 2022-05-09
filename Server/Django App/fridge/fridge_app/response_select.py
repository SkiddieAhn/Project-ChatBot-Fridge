from django.http import JsonResponse

def one(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def two(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def three(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def four(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def five(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': date[4][0] + "년 " + date[4][1] + "월 " + date[4][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[4]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def six(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': date[4][0] + "년 " + date[4][1] + "월 " + date[4][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[4]
                },
                {
                    'label': date[5][0] + "년 " + date[5][1] + "월 " + date[5][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[5]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def seven(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': date[4][0] + "년 " + date[4][1] + "월 " + date[4][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[4]
                },
                {
                    'label': date[5][0] + "년 " + date[5][1] + "월 " + date[5][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[5]
                },
                {
                    'label': date[6][0] + "년 " + date[6][1] + "월 " + date[6][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[6]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def eight(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': date[4][0] + "년 " + date[4][1] + "월 " + date[4][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[4]
                },
                {
                    'label': date[5][0] + "년 " + date[5][1] + "월 " + date[5][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[5]
                },
                {
                    'label': date[6][0] + "년 " + date[6][1] + "월 " + date[6][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[6]
                },
                {
                    'label': date[7][0] + "년 " + date[7][1] + "월 " + date[7][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[7]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def nine(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': date[4][0] + "년 " + date[4][1] + "월 " + date[4][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[4]
                },
                {
                    'label': date[5][0] + "년 " + date[5][1] + "월 " + date[5][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[5]
                },
                {
                    'label': date[6][0] + "년 " + date[6][1] + "월 " + date[6][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[6]
                },
                {
                    'label': date[7][0] + "년 " + date[7][1] + "월 " + date[7][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[7]
                },
                {
                    'label': date[8][0] + "년 " + date[8][1] + "월 " + date[8][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[8]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })

def ten(date,ocr_result):
    return JsonResponse({
        'version': "2.0",
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "아래 목록에서 올바른 유통기한을 선택해주세요!!"
                }
            }],
            'quickReplies': [
                {
                    'label': date[0][0]+"년 "+date[0][1]+"월 "+date[0][2]+"일",
                    'action': 'message',
                    'messageText': ocr_result[0]
                },
                {
                    'label': date[1][0] + "년 " + date[1][1] + "월 " + date[1][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[1]
                },
                {
                    'label': date[2][0] + "년 " + date[2][1] + "월 " + date[2][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[2]
                },
                {
                    'label': date[3][0] + "년 " + date[3][1] + "월 " + date[3][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[3]
                },
                {
                    'label': date[4][0] + "년 " + date[4][1] + "월 " + date[4][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[4]
                },
                {
                    'label': date[5][0] + "년 " + date[5][1] + "월 " + date[5][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[5]
                },
                {
                    'label': date[6][0] + "년 " + date[6][1] + "월 " + date[6][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[6]
                },
                {
                    'label': date[7][0] + "년 " + date[7][1] + "월 " + date[7][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[7]
                },
                {
                    'label': date[8][0] + "년 " + date[8][1] + "월 " + date[8][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[8]
                },
                {
                    'label': date[9][0] + "년 " + date[9][1] + "월 " + date[9][2] + "일",
                    'action': 'message',
                    'messageText': ocr_result[9]
                },
                {
                    'label': '없음',
                    'action': 'message',
                    'messageText': '없음'
                },
                {
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                },
            ]
        }
    })