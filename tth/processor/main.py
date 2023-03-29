import itertools
import json
import math
import multiprocessing as mp
import numpy as np
from pathlib import Path

import cv2 as cv
from vidgear.gears import CamGear

BASE_DIR = Path(__file__).resolve().parent


class VideoProcessor:
    def __init__(self, service, path):
        self.service = service
        self.path = path

    def get_perceived_brightness(self, frame):
        r, g, b = frame.mean(axis=(0, 1))
        mean_brightness = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
        return mean_brightness, r, g, b

    def find_peaks(self, data, spacing, limit):
        from processor.libs.findpeaks import findpeaks
        # from libs.findpeaks import findpeaks
        return findpeaks(np.array(data), spacing=spacing, limit=limit)

    def get_intervals(self, mean_brightness, peaks, framerate, threshold):
        min_safe_video_freq = 2
        bandwidth = int(framerate / min_safe_video_freq)
        window = int(bandwidth / 2) + 1

        intervals = []
        frames = []
        for peak_idx in peaks:
            left_interval_idx, right_interval_idx = peak_idx, peak_idx
            try:
                left_mean_brightness = (
                    mean_brightness[peak_idx-window:peak_idx]
                )
                lowest_left_mean_brightness_val = min(left_mean_brightness)
                lowest_left_mean_brightness_idx = peak_idx - window
            except Exception:
                left_mean_brightness = mean_brightness[:peak_idx]
                lowest_left_mean_brightness_val = min(left_mean_brightness)
                lowest_left_mean_brightness_idx = 0
            try:
                right_mean_brightness = (
                    mean_brightness[peak_idx+1:peak_idx+window+1]
                )
                lowest_right_mean_brightness_val = min(right_mean_brightness)
                lowest_right_mean_brightness_idx = peak_idx + window
            except Exception:
                right_mean_brightness = mean_brightness[peak_idx:]
                lowest_right_mean_brightness_val = min(right_mean_brightness)
                lowest_right_mean_brightness_idx = len(mean_brightness)-1

            if (mean_brightness[peak_idx] * (1 - threshold)
                    >= lowest_left_mean_brightness_val):
                left_interval_idx = lowest_left_mean_brightness_idx

            if (mean_brightness[peak_idx] * (1 - threshold)
                    >= lowest_right_mean_brightness_val):
                right_interval_idx = lowest_right_mean_brightness_idx

            if left_interval_idx != right_interval_idx:
                left_interval_time = left_interval_idx / framerate
                right_interval_time = right_interval_idx / framerate
                try:
                    prev_interval = intervals[-1]
                    prev_frame = frames[-1]
                except Exception:
                    pass
                else:
                    # тут можно увеличить/уменьшить сглаживание в сек с 0.3
                    smoothing_time = 0.3
                    if (prev_interval[1] - left_interval_time <= smoothing_time
                            or prev_interval[1] >= left_interval_time):
                        prev_interval[1] = right_interval_time
                        prev_frame[1] = right_interval_idx
                        continue
                intervals.append([left_interval_time, right_interval_time])
                frames.append([left_interval_idx, right_interval_idx])
        return intervals, frames

    def get_frame_brightness_data(self, frame, result):
        mean_brightness, red, green, blue = (
            self.get_perceived_brightness(frame)
        )
        result['data']['x'].append(result['data']['total_frames'])
        result['data']['mean_brightness'].append(mean_brightness)
        result['data']['red'].append(red)
        result['data']['green'].append(green)
        result['data']['blue'].append(blue)
        result['data']['total_frames'] += 1
        return result

    def get_youtube_brightness_data(self, result):
        try:
            stream = CamGear(source=self.path, stream_mode=True).start()
        except Exception:
            return result

        result['data']['framerate'] = stream.framerate
        while True:
            frame = stream.read()
            if frame is None:
                stream.stop()
                break

            result = self.get_frame_brightness_data(frame, result)
        return result

    def get_drive_brightness_data(self, result):
        try:
            cap = cv.VideoCapture(self.path)
        except Exception:
            return result

        result['data']['framerate'] = cap.get(cv.CAP_PROP_FPS)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break

            result = self.get_frame_brightness_data(frame, result)
        return result

    def analyze_brightness(self):
        result = {}
        result['success'] = False
        result['data'] = {
            'x': [],
            'mean_brightness': [],
            'red': [],
            'green': [],
            'blue': [],
            'framerate': 0,
            'total_frames': 0,
        }

        if self.service == 'drive':
            result = self.get_drive_brightness_data(result)
        if self.service == 'youtube':
            result = self.get_youtube_brightness_data(result)

        if result['data']['mean_brightness']:
            # Теоретически тут можно играться с spacing и limit
            spacing = int(result['data']['framerate'] / 2)
            limit = 0
            peaks = self.find_peaks(result['data']['mean_brightness'],
                                    spacing=spacing, limit=limit)
            # Тут можно играться threshold (% от пика) чем меньше - тем чувствительнее алгоритм
            threshold = 0.6
            intervals, frames = self.get_intervals(
                result['data']['mean_brightness'], peaks,
                result['data']['framerate'], threshold=threshold
            )
            result['danger_intervals'] = {
                'peaks': list(map(int, peaks.tolist())),
                'intervals': list(map(lambda x: [float(x[0]), float(x[1])], intervals)),
                'frames': list(map(lambda x: [int(x[0]), int(x[1])], frames)),
            }
            result['success'] = True
        return result

    def process_video_multiprocessing(self, iter):
        group_number, num_processes = iter
        cap = cv.VideoCapture(self.path)
        num_of_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        frame_jump_unit = num_of_frames // num_processes
        cap.set(cv.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)
        proc_frames = 0

        result = {}
        result['group'] = group_number
        result['data'] = {
            'x': [],
            'mean_brightness': [],
            'red': [],
            'green': [],
            'blue': [],
            'framerate': 0,
            'total_frames': 0,
        }

        result['data']['framerate'] = cap.get(cv.CAP_PROP_FPS)
        while proc_frames < frame_jump_unit:
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break

            result = self.get_frame_brightness_data(frame, result)
            proc_frames += 1
        return result

    def multithread_analyze_brightness(self):
        num_processes = mp.cpu_count()
        pool = mp.Pool(num_processes)
        results = pool.map(
            self.process_video_multiprocessing,
            zip(range(num_processes), itertools.repeat(num_processes))
        )

        result = {}
        result['success'] = False
        result['data'] = {
            'x': [],
            'mean_brightness': [],
            'red': [],
            'green': [],
            'blue': [],
            'framerate': 0,
            'total_frames': 0,
        }

        for mult_result in results:
            result['data']['mean_brightness'] += (
                mult_result['data']['mean_brightness']
            )
            result['data']['red'] += mult_result['data']['red']
            result['data']['green'] += mult_result['data']['green']
            result['data']['blue'] += mult_result['data']['blue']
            result['data']['framerate'] = mult_result['data']['framerate']
            result['data']['total_frames'] += (
                mult_result['data']['total_frames']
            )
        result['data']['x'] = list(range(result['data']['total_frames']))

        if result['data']['mean_brightness']:
            spacing = int(result['data']['framerate'] / 2)
            limit = 0
            peaks = self.find_peaks(result['data']['mean_brightness'],
                                    spacing=spacing, limit=limit)
            threshold = 0.3
            intervals, frames = self.get_intervals(
                result['data']['mean_brightness'], peaks,
                result['data']['framerate'], threshold=threshold
            )
            result['danger_intervals'] = {
                'peaks': peaks,
                'intervals': intervals,
                'frames': frames,
            }
            result['success'] = True
        return result


def main():
    # https://www.youtube.com/watch?v=nWBeexdXEKU
    # https://www.youtube.com/watch?v=sGBkneu30Aw

    url = 'https://www.youtube.com/watch?v=sGBkneu30Aw'
    v = VideoProcessor('youtube', url)
    r = v.analyze_brightness()

    # path = '/home/chupss/Dev/tth-films-adaptation/tth/processor/test.mp4'
    # v = VideoProcessor('drive', path)
    # r = v.analyze_brightness()

    # path = '/home/chupss/Dev/tth-films-adaptation/tth/processor/test.mp4'
    # v = VideoProcessor('drive', path)
    # r = v.multithread_analyze_brightness()

    with open('out.json', 'w') as f:
        f.write(json.dumps(r.get('data')))


if __name__ == "__main__":
    main()
