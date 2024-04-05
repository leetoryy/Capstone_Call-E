import cv2

vfile = cv2.VideoCapture(0)

if vfile.isOpened():
    while True:
        vret, img = vfile.read()
        if vret:
            cv2.imshow('webcam', img)
            if cv2.waitKey(1) != 1:
                break
        else:
            print("프레임 정상적이지 않음")
            break
else:
    print("오류 발생")

vfile.release()
cv2.destroyAllWindows()
