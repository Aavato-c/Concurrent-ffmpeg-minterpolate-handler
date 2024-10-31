import concurrent.futures
import multiprocessing
import os
import random
import subprocess
import datetime

import concurrent
import dotenv

dotenv.load_dotenv()

AVAILABLE_PROCESSORS = multiprocessing.cpu_count()
TEMP_DIR = ".temp_vidit"

me_modes_available = [
    "bidir",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
    "bilat",
]

me_available = [
    "epzs",
    "tss",
    "tdls",
    "ntss",
    "fss",
    "ds",
    "hexbs",
    "epzs",
    "umh",
    "esa",
    "tss",
    "tdls",
    "ntss",
    "fss",
    "hexbs",
]

mc_available = [
    "aobmc",
    "aobmc",
]

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def cleanup():
    print("Cleaning up...")
    if os.path.exists(TEMP_DIR):
        if len(os.listdir(TEMP_DIR)) > 0:
            for file in os.listdir(TEMP_DIR):
                os.remove(os.path.join(TEMP_DIR, file))
        os.rmdir(TEMP_DIR)


def print_green(text: str):
    print(f"\n==============================\n\n\033[92m{text}\033[00m\n\n")



def cut_video_to_chunks(source_video_path: str, chunk_duration_seconds: int, temp: str = None):
    if not temp:
        temp = TEMP_DIR
    if not os.path.exists(temp):
        os.makedirs(temp)

    cmd = f"ffmpeg -i {source_video_path} -c copy -f segment -segment_time {chunk_duration_seconds} {temp}/_s_%05d.mp4"

    try:
        output = subprocess.check_output(cmd, shell=True)
        print_green(f"Cut video to chunks: {output}")
    except Exception as e:
        print(f"Error cutting video to chunks: {e}")
        raise e

    chunk_filenames = os.listdir(temp)
    chunk_paths = [os.path.join(temp, chunk_filename) for chunk_filename in chunk_filenames]
    return chunk_paths



def blend_video_frames_of_video_object_multiproc(
    source_video_path: str,
    export_path: str,
    pts_factor: float = 62.2,
    fps: int = 25,
    mb_size: int = 16,
    search_param: int = 400,
    vsbmc: int = 0,
    scd: str = "none",
    mc_mode: str = "aobmc",
    me_mode: str = "bidir",
    me: str = "epzs",
    scale_str: str = "",
    use_random_params: bool = False,
    end_time_seconds: int = None,
    chunk_duration_seconds: int = 2
):
    
    if use_random_params:
        #mb_size = str(int(random.randint(4, 16)))
        mb_size = str(int(random.randint(4, 16)))
        #search_param = random.choice([4, 100, 400, 800])
        search_param = random.choice([4, 100])
        vsbmc = random.choice([0, 1])
        scd = "none"
        mc_mode = random.choice(["aobmc", "obmc"])
        me_mode = random.choice(["bidir", "bilat"])
        me = random.choice(["epzs", "tss", "tdls", "ntss", "fss", "ds", "hexbs", "umh", "esa", "tss", "tdls", "ntss", "fss", "hexbs"])
        #scale_str = random.choice(["scale=1280:-2,", "scale=1920:-2,", ""])
        scale_str = "scale=1280:-2,"


    params_for_print = f"""\
    pts_factor: {pts_factor}
    fps: {fps}
    mb_size: {mb_size}
    search_param: {search_param}
    vsbmc: {vsbmc}
    scd: {scd}
    mc_mode: {mc_mode}
    me_mode: {me_mode}
    me: {me}
    scale_str: {scale_str}
    source_video_path: {source_video_path}
    start_time: {datetime.datetime.now().strftime("%d.%m.%Y, klo %H:%M:%S")}
    chunk_duration_seconds: {chunk_duration_seconds}
    """
    print_green(params_for_print)

    if not os.path.exists(export_path.split('.')[0]):
        os.makedirs(export_path.split('.')[0])
    
    if os.path.exists(export_path):
        n=1
        while os.path.exists(export_path):
            export_path = export_path.split('.')[0] + f"_{n}.mp4"
            n += 1
	
    chunks = cut_video_to_chunks(source_video_path, chunk_duration_seconds)
    
    output_paths = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=AVAILABLE_PROCESSORS) as executor:
        futures = []
        for chunk in chunks:
            output_path = os.path.join(export_path.split('.')[0], f"{chunk.split('.')[0]}_output.mp4")
            output_paths.append(output_path)
            cmd = f"""ffmpeg -i {chunk} -filter:v "{scale_str}setpts={pts_factor}*PTS,minterpolate='fps={fps}:mb_size={mb_size}:search_param={search_param}:vsbmc={vsbmc}:scd={scd}:mc_mode={mc_mode}:me_mode={me_mode}:me={me}'" -c:v h264 -preset slow -crf 20 -y {output_path}"""
            futures.append(executor.submit(subprocess.run, cmd, shell=True))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

    # Concatenate the result
    with open(os.path.join(export_path.split('.')[0], "_list.txt"), "w") as f:
        for output_path in output_paths:
            f.write(f"file '{output_path}'\n")
    concat_cmd = f"ffmpeg -f concat -safe 0 -i {os.path.join(export_path.split('.')[0], '_list.txt')} -c copy {export_path}"
    try:
        output = subprocess.check_output(concat_cmd, shell=True)
        print_green(f"Concatenated video: {output}")
    except Exception as e:
        print(f"Error concatenating video: {e}")
        raise e
    
    cleanup()

    print_green(f"Finished processing video: {source_video_path} to {export_path}")


if __name__ == "__main__":
    source_video_path = os.environ.get("SOURCE_VIDEO_PATH")
    export_path = "output.mp4"
    try:
        blend_video_frames_of_video_object_multiproc(source_video_path, export_path, use_random_params=False)
    finally:
        cleanup()

