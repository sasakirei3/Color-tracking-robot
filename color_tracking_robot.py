# -*- coding: utf-8 -*-
import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
FL_pin = 26
FL_dir1 = 19

FR_pin = 13
FR_dir1 = 6

BL_pin = 21
BL_dir1 = 20

BR_pin = 16
BR_dir1 = 12

GPIO.setup(FL_pin,GPIO.OUT)
GPIO.setup(FL_dir1,GPIO.OUT)
GPIO.setup(FR_pin,GPIO.OUT)
GPIO.setup(FR_dir1,GPIO.OUT)

GPIO.setup(BL_pin,GPIO.OUT)
GPIO.setup(BL_dir1,GPIO.OUT)

GPIO.setup(BR_pin,GPIO.OUT)
GPIO.setup(BR_dir1,GPIO.OUT)

pwmFL = GPIO.PWM(FL_pin,200)
pwmFR = GPIO.PWM(FR_pin,200)
pwmBL = GPIO.PWM(BL_pin,200)
pwmBR = GPIO.PWM(BR_pin,200)

#moter drive dir (forward)


def red_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 赤色のHSVの値域1

    hsv_min = np.array([0,127,0])
    hsv_max = np.array([30,255,255])

    mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

    # 赤色のHSVの値域2
    hsv_min = np.array([150,127,0])
    hsv_max = np.array([179,255,255])
    mask2 = cv2.inRange(hsv, hsv_min, hsv_max)
    
    return mask1 + mask2

# ブロブ解析
def analysis_blob(binary_img):
    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(binary_img)

    # ブロブ情報を項目別に抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center = np.delete(label[3], 0, 0)

    # ブロブ面積最大のインデックス
    max_index = np.argmax(data[:, 4])

    # 面積最大ブロブの情報格納用
    maxblob = {}

    # 面積最大ブロブの各種情報を取得
    maxblob["upper_left"] = (data[:, 0][max_index], data[:, 1][max_index]) # 左上座標
    maxblob["width"] = data[:, 2][max_index]  # 幅
    maxblob["height"] = data[:, 3][max_index]  # 高さ
    maxblob["area"] = data[:, 4][max_index]   # 面積
    maxblob["center"] = center[max_index]  # 中心座標
    
    return maxblob

def main():
    #videofile_path = "C:/github/sample/python/opencv/video/color_tracking/red_pendulum.mp4"

    # カメラのキャプチャ
    cap = cv2.VideoCapture(0)
    
    while(cap.isOpened()):
        # フレームを取得
        ret, frame = cap.read()

        # 赤色検出
        mask = red_detect(frame)

        # マスク画像をブロブ解析（面積最大のブロブ情報を取得）
        target = analysis_blob(mask)
        
        # 面積最大ブロブの中心座標を取得
        center_x = int(target["center"][0])
        center_y = int(target["center"][1])
        
        area = int(target["area"])
        print(area)
        # フレームに面積最大ブロブの中心周囲を円で描く
        cv2.circle(frame, (center_x, center_y), 30, (0, 200, 0),
                   thickness=3, lineType=cv2.LINE_AA)
        x = center_x - 320

        if x > 100:
                pwmFL.start(15)  
                pwmBL.start(15)
                pwmFR.start(15)  
                pwmBR.start(15)
                GPIO.output(FL_dir1,True)
                GPIO.output(FR_dir1,False)  
                GPIO.output(BL_dir1,True)
                GPIO.output(BR_dir1,False)
        elif x < -100:
                pwmFR.start(15)  
                pwmBR.start(15)
                pwmFL.start(15)  
                pwmBL.start(15)
                GPIO.output(FL_dir1,False)
                GPIO.output(FR_dir1,True)  
                GPIO.output(BL_dir1,False)
                GPIO.output(BR_dir1,True)
        elif area < 50000:              
                pwmFR.start(10)  
                pwmBR.start(10)
                pwmFL.start(10)  
                pwmBL.start(10)
                GPIO.output(FL_dir1,True)
                GPIO.output(FR_dir1,True)  
                GPIO.output(BL_dir1,True)
                GPIO.output(BR_dir1,True)
        else:
                pwmFR.start(0)  
                pwmBR.start(0)
                pwmFL.start(0)  
                pwmBL.start(0)            

        # 結果表示
        #cv2.imshow("Frame", frame)
        #print(x)
        #cv2.imshow("Mask", mask)

        # qキーが押されたら途中終了
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == '__main__':
    main() 