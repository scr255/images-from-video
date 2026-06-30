import datetime
import json
import multiprocessing
import os
import shutil
import time

from tqdm.auto import tqdm

from common import ImagesFromVideo

# # Parameters
# Run id based on timestamp
NOW = datetime.datetime.now().strftime("%Y_%m_%d_____%H_%M_%S")

# Number of batches
NUM_PROCESSES = multiprocessing.cpu_count()

# Take snapshot every n seconds
FREQ_SECONDS = 30
# Resolution of the snapshot
SIZE_OUTPUT = (1920, 1080)

# Directories containing videos to process
DIRS_INPUT = sorted(set(x for x in [os.path.join("..", "sc")]))
# Video format (case sensitive)
PATTERN_VIDEO = ".mp4"

# Directory output
DIR_OUTPUT = os.path.join("..", "ft_{}".format(NOW))
# Image format
PATTERN_IMAGE = ".png"

# Log file
PATH_JSON = "json_data_{}.json".format(NOW)

# False for debugging
OUTPUT = True


# # Directory operations
try:
    shutil.rmtree(DIR_OUTPUT)
    print("Output directory deleted")
except:
    print("Output directory not found")

os.makedirs(os.path.join(DIR_OUTPUT, "all"))
print("Output directory created-validated")


# # List files to process
filenames = []
for d in DIRS_INPUT:
    for f in sorted(os.path.join(d, x) for x in os.listdir(d) if PATTERN_VIDEO in x):
        filenames.append(f)
print(len(filenames), "files matching pattern")


# # Images from videos
start = time.time()
counter = 0
d = {}
for f in tqdm(filenames):
    f_init = ImagesFromVideo(
        filename=f,
        freq_seconds=FREQ_SECONDS,
        pattern_video=PATTERN_VIDEO,
        pattern_image=PATTERN_IMAGE,
        dir_output=os.path.join(DIR_OUTPUT, "all"),
        size_output=SIZE_OUTPUT,
        num_processes=NUM_PROCESSES,
    )
    counter += f_init.n_frames()
    d[os.path.basename(f)] = f_init.list_frames_str()
    if OUTPUT == True:
        f_init.save_frames_chunks(f_init.list_frames_int())
if OUTPUT == True:
    assert counter == len(os.listdir(os.path.join(DIR_OUTPUT, "all")))
print(round((time.time() - start) / 60, 1), "minutes")


# Write summary as json
json_string = {
    "RUN_ID": NOW,
    "FREQ_SECONDS": FREQ_SECONDS,
    "SIZE_OUTPUT": SIZE_OUTPUT,
    "N_OF_FRAMES": counter,
    "FRAMES": d,
}
with open(os.path.join(DIR_OUTPUT, PATH_JSON), "w") as outfile:
    json.dump(json_string, outfile, indent=4)
