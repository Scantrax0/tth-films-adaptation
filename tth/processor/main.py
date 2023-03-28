from vidgear.gears import CamGear
import math
import json
import numpy as np


class VideoProcessor:
    def __init__(self, youtube_url):
        self.youtube_url = youtube_url

    @staticmethod
    def _perceived_brightness(frame):
        r, g, b = frame.mean(axis=(0, 1))
        mn = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
        return map(int, [mn, r, g, b])

    @staticmethod
    def _find_peaks(data, spacing, limit):
        from libs.findpeaks import findpeaks
        return findpeaks(np.array(data), spacing=spacing, limit=limit)

    @staticmethod
    def _find_intervals(mn, peaks, framerate, threshold):
        min_safe_freq = 2
        window = int(framerate / min_safe_freq) + 1
        intervals = []

        for peak in peaks:
            left_idx, right_idx = peak, peak
            try:
                sl = mn[peak-window:peak]
                lowest_left_val = min(sl)
                lowest_left_idx = peak - len(sl) + sl.index(lowest_left_val)
            except Exception:
                sl = mn[:peak]
                lowest_left_val = min(sl)
                lowest_left_idx = peak - len(sl) + sl.index(lowest_left_val) + 1

            try:
                sl = mn[peak+1:peak+window+1]
                lowest_right_val = min(sl)
                lowest_right_idx = peak + len(sl) - sl[::-1].index(lowest_right_val)
            except Exception:
                sl = mn[peak:]
                lowest_right_val = min(sl)
                lowest_right_idx = peak + len(sl) - sl[::-1].index(lowest_right_val) - 1

            if abs(mn[peak] - lowest_left_val) >= threshold:
                left_idx = lowest_left_idx

            if abs(mn[peak] - lowest_right_val) >= threshold:
                right_idx = lowest_right_idx

            if left_idx != right_idx:
                cur_interval_left = left_idx / framerate
                cur_interval_right = right_idx / framerate

                try:
                    prev_interval = intervals[-1]
                except Exception:
                    prev_interval = None
                if prev_interval:
                    if prev_interval[1] >= cur_interval_left:
                        prev_interval[1] = cur_interval_right
                        continue
                intervals.append([cur_interval_left, cur_interval_right])

        return intervals

    def analyze_brightness(self):
        result = {
            'success': False,
            'data': {}
        }
        i = 0
        x = []
        mean = []
        red = []
        green = []
        blue = []

        try:
            stream = CamGear(source=self.youtube_url, stream_mode=True).start()
            framerate = stream.framerate
        except Exception:
            return result
        while True:
            frame = stream.read()
            if frame is None:
                break
            i += 1
            mn, r, g, b = self._perceived_brightness(frame)  # list(map(str, ))
            x.append(i)
            mean.append(mn)
            red.append(r)
            green.append(g)
            blue.append(b)

        # Тут можно играться с spacing и limit
        peaks = self._find_peaks(mean, spacing=2, limit=7)
        # можно играться threshold
        intervals = self._find_intervals(mean, peaks, framerate, threshold=0.2)

        result['success'] = True
        result['data'] = {
            'total_frames': i,
            'x': x,
            'mean': mean,
            'red': red,
            'green': green,
            'blue': blue,
        }
        result['danger_intervals'] = intervals
        stream.stop()
        return result


def main():
    url = 'https://www.youtube.com/watch?v=nWBeexdXEKU'
    v = VideoProcessor(url)
    r = v.analyze_brightness()

    with open('out.json', 'w') as f:
        f.write(json.dumps(r.get('data')))


if __name__ == "__main__":
    main()
