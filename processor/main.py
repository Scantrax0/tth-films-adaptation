from vidgear.gears import CamGear
import math
import json


class VideoProcessor:
    def __init__(self, youtube_url):
        self.youtube_url = youtube_url

    @staticmethod
    def _perceived_brightness(frame):
        r, g, b = frame.mean(axis=(0, 1))
        return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))

    def analyze_brightness(self):
        result = {
            'success': False,
            'data': {}
        }
        i = 0
        x = []
        y = []

        stream = CamGear(source=self.youtube_url, stream_mode=True).start()
        while True:
            frame = stream.read()
            if frame is None:
                break
            i += 1
            brightness = str(int(self._perceived_brightness(frame)))
            x.append(i)
            y.append(brightness)
        result['success'] = True
        result['data'] = {
            'total_frames': i,
            'x': x,
            'y': y,
        }
        stream.stop()
        return result


def main():
    url = "https://www.youtube.com/watch?v=nWBeexdXEKU"
    v = VideoProcessor(url)
    r = v.analyze_brightness()

    with open('out.json', 'w') as f:
        f.write(json.dumps(r.get('data')))


if __name__ == "__main__":
    main()
