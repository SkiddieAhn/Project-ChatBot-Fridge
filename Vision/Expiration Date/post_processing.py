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
