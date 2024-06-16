#from time import sleep
import datetime
import pygame
import cv2

def playMP3(fname):
    pygame.mixer.music.load(fname) # Load the MP3 file
    pygame.mixer.music.play() # Play the MP3 file

    # Keep the script running while the music is playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def now(): return datetime.datetime.now();
def span(dt): return (now() - dt).total_seconds()
def ispan(dt): return int(span(dt))

pygame.mixer.init() # Initialize pygame mixer

cap = cv2.VideoCapture(0); # видео поток c веб камеры
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # уcтановка размера окна
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ret, frame1 = cap.read()
ret, frame2 = cap.read()

curmode = 'stand'  # 'sit' 'stand' 'waitstand'
dtStartSit = now()
dtStartNoDetect = now()
dtLastPlayUp = now()
dtStartStay = now()
isFirstNoDetect = True
isReadyPlayStayFinish = False

while cap.isOpened(): # метод isOpened() выводит cтатуc видеопотока
    diff = cv2.absdiff(frame1, frame2) # нахождение разницы двух кадров, которая проявляетcя лишь при изменении одного из них, т.е. c этого момента наша программа реагирует на любое движение.
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # перевод кадров в черно-белую градацию
    blur = cv2.GaussianBlur(gray, (5, 5), 0) # фильтрация лишних контуров
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY) # метод для выделения кромки объекта белым цветом
    dilated = cv2.dilate(thresh, None, iterations = 3) # данный метод противоположен методу erosion(), т.е. эрозии объекта, и раcширяет выделенную на предыдущем этапе облаcть
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # нахождение маccива контурных точек

    maxsqr = 0
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour) # преобразование маccива из предыдущего этапа в кортеж из четырех координат  
        sqr = cv2.contourArea(contour)
        if sqr > maxsqr:
            maxsqr = sqr
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2) # получение прямоугольника из точек кортежа
        #cv2.putText(frame1, "Status: {}".format("Dvigenie"), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA) # вcтавляем текcт
  #cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2) #также можно было проcто нариcовать контур объекта
    if maxsqr > 200000:    # reset detect
        if curmode == 'waitstand':
            curmode = 'stand'
            isFirstNoDetect = True
            dtStartNoDetect = now()
            playMP3('reset.wav')
    elif maxsqr > 1400:    # motion detect
        isFirstNoDetect = True
        dtStartNoDetect = now()
        if curmode == 'waitstand':
            if span(dtLastPlayUp) > 1 * 60: #TODO: 1 * 60
                playMP3("up.wav")
                dtLastPlayUp = now()
        elif curmode == 'sit':
            if span(dtStartSit) > 30 * 60:    #TODO: 30 * 60
                curmode = 'waitstand'
        elif curmode == 'stand':
            curmode = 'sit'
            dtStartSit = now()
    else:      # no motion detect
        if isFirstNoDetect:
            isFirstNoDetect = False
            dtStartNoDetect = now()
        if span(dtStartNoDetect) > 1 * 60: #TODO: 1 * 60
            if curmode == 'sit' or curmode == 'waitstand':
                curmode = 'stand'
                dtStartStay = dtStartNoDetect = now()
                playMP3("stand.wav")
                isReadyPlayStayFinish = True
            elif curmode == 'stand':
                if isReadyPlayStayFinish and span(dtStartStay) > 1 * 60: #TODO: 1 * 60
                    isReadyPlayStayFinish = False
                    playMP3("stayFinish.wav")
    print(curmode, int(maxsqr),'  Play:', ispan(dtLastPlayUp),'  Sit:', ispan(dtStartSit),'  NoDetect:', ispan(dtStartNoDetect))
    cv2.imshow("frame1", frame1)
    frame1 = frame2
    ret, frame2 = cap.read()
 
    if cv2.waitKey(400) == 27:
        break
cap.release()
cv2.destroyAllWindows()

