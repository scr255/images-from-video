import math
import multiprocessing
import os

import cv2


class ImagesFromVideo:
    def __init__(
        self,
        filename,
        freq_seconds,
        pattern_video,
        pattern_image,
        dir_output,
        size_output,
        num_processes,
    ):
        self.filename = filename
        self.freq_seconds = freq_seconds
        self.pattern_video = pattern_video
        self.pattern_image = pattern_image
        self.dir_output = dir_output
        self.size_output = size_output
        self.num_processes = num_processes
        self.filename_no_extension = os.path.basename(filename).split(
            self.pattern_video
        )[0]

        # Read video and get n_frames and rounded frame_rate
        cap = cv2.VideoCapture(self.filename)
        n_frames = math.floor(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        freq = math.floor(self.freq_seconds * frame_rate)
        # List containing frames to save from video
        self.frames_to_save_int = sorted(x for x in range(n_frames) if (x % freq == 0))
        # Integrity check
        assert len(self.frames_to_save_int) > 0
        # Point to last frame and read image
        last_frame = self.frames_to_save_int[-1]
        cap.set(cv2.CAP_PROP_POS_FRAMES, last_frame)
        _, frame = cap.read()
        if _ != True:
            print("\tLast frame not parsed:", self.filename, last_frame)
            self.frames_to_save_int.remove(last_frame)
        cap.release()

    def n_frames(self):
        """Returns number of frames in video, given a frequency in seconds"""
        return len(self.frames_to_save_int)

    def list_frames_int(self):
        """Returns list of frames in video as integers, given a frequency in seconds"""
        return self.frames_to_save_int

    def list_frames_str(self):
        """Returns list of frames in video as string, given a frequency in seconds"""
        return [
            (self.filename_no_extension + "_" + str(int(x)) + self.pattern_image)
            for x in self.frames_to_save_int
        ]

    def save_frames(self, frames_to_save):
        """Save frames, given a list of frames in video"""
        cap = cv2.VideoCapture(self.filename)
        for f in frames_to_save:
            # Point to frame f and read image
            cap.set(cv2.CAP_PROP_POS_FRAMES, f)
            _, frame = cap.read()
            if _ != True:
                print("\tERROR", self.filename, f)
                continue
            # Save snapshot
            cv2.imwrite(
                os.path.join(
                    self.dir_output,
                    self.filename_no_extension + "_" + str(int(f)) + ".png",
                ),
                cv2.resize(frame, dsize=self.size_output),
                [int(cv2.IMWRITE_PNG_COMPRESSION), 7],
            )
        cap.release()
        return None

    @staticmethod
    def chunks(l, n):
        """Yield n number of striped chunks from l"""
        for i in range(0, n):
            yield l[i::n]

    def save_frames_chunks(self, frames_to_save):
        """Save frames using multiprocessing, given a list of frames in video"""
        frames_to_save_chunks = sorted(
            self.chunks(l=self.frames_to_save_int, n=self.num_processes)
        )
        multiprocessing.Pool(self.num_processes).map(
            self.save_frames, frames_to_save_chunks
        )
