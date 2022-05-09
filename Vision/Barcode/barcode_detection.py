import cv2
import pyzbar.pyzbar as pyzbar

def detect_barcode(dir):

  image = cv2.imread(dir)
  if image.shape[0]>=1000:
    image=cv2.resize(image,dsize=(0,0),fx=0.2,fy=0.2)

  barcodeCnt=len(pyzbar.decode(image))

  if barcodeCnt==0: return 0

  barcodeList=pyzbar.decode(image)

  maxArea=0
  for barcode in barcodeList:
    (_,_,w,h)=barcode.rect
    barcodeArea=w*h
    if barcodeArea>maxArea:
      maxArea=barcodeArea
      result=barcode.data.decode('utf-8')
  
  return result

