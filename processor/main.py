import cv2
import os
import math
import json

class VideoProcessor:

    def __init__(self, path):
        if os.path.isfile(path):
            self.videopath = path
        else:
            raise Exception('Cannot locate the video file')
    
    @staticmethod
    def _perceived_brightness(frame):
        r, g, b = frame.mean(axis=(0,1))
        return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    
    def analyze_brightness(self, SHOW=False):
        result = {
            'success': False,
            'data': {}
        }
        i = 0
        x = []
        y = []

        cap = cv2.VideoCapture(self.videopath) 
        if not cap.isOpened():
            raise Exception('Cannot open video file')
        while True:
            i += 1
            ret, frame = cap.read()
            if not ret:
                print('Cannot receive frame, finishing analysis')
                cap.release()
                break
            brightness = str(int(self._perceived_brightness(frame)))
            x.append(i)
            y.append(brightness)

            if SHOW:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, 
                    brightness, 
                    (50, 50), 
                    font, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        result['success'] = True
        result['data'] = {
            'total_frames': i,
            'x': x,
            'y': y,
        }
        cap.release()

        return result

v = VideoProcessor("C:/projects/hackathon/tth-films-adaptation/tth/media/raw_video/SampleVideo_1280x720_2mb.mp4")
r = v.analyze_brightness()
with open('out.json', 'w') as f:
    f.write(json.dumps(r.get('data')))

