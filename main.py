import argparse
import os
import shutil
import subprocess
import time

from pysrt import SubRipFile, SubRipItem, SubRipTime


def search_subtitle_files(folder, keyword):
    """
    Search for subtitles containing the given keyword in the specified folder and its subfolders,
    excluding the 'clips' folder.
    """
    subtitle_files = []
    for root, dirs, files in os.walk(folder):
        # Skip the 'clips' folder
        dirs[:] = [d for d in dirs if d != 'clips']
        for file in files:
            if file.endswith('.srt'):
                subtitle_file_path = os.path.join(root, file)
                subs = SubRipFile.open(subtitle_file_path)
                for i, sub in enumerate(subs):
                    if keyword in sub.text:
                        subtitle_files.append((subtitle_file_path, i))
    return subtitle_files


def get_subtitle(subs, index):
    """
    Get the subtitle at the given index.
    """
    if 0 <= index < len(subs):
        return subs[index]
    return None


def find_video_file(subtitle_file):
    """
    Find the corresponding video file for a given subtitle file.
    """
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv']
    base_name = os.path.splitext(subtitle_file)[0]
    for ext in video_extensions:
        video_file = base_name + ext
        if os.path.exists(video_file):
            return video_file
    return None


def format_ffmpeg_time(seconds):
    """
    Format seconds to HH:MM:SS.mmm format for ffmpeg.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"


def convert_to_seconds(time_obj):
    """
    Convert a datetime.time object to seconds.
    """
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6


def format_time(time_obj):
    """
    Format a datetime.time object to a string (HH-MM-SS).
    """
    return time_obj.strftime("%H-%M-%S")


def extract_path_parts(file_path):
    """
    Extract the last two directory names and the file name (without extension) from the given file path.
    """
    dir_path, file_name = os.path.split(file_path)
    dir_parts = dir_path.split(os.sep)
    result = f"{dir_parts[-1]}-{file_name}"
    return result


def create_output_paths(clips_folder, keyword, video_name, start_str, end_str):
    """
    Create output paths for video clip and SRT file.
    """
    output_clip = os.path.join(
        clips_folder,
        f"「{keyword}」_[{video_name}]_[{start_str}]_to_[{end_str}].mp4"
    )

    output_srt = os.path.join(
        clips_folder,
        f"「{keyword}」_[{video_name}]_[{start_str}]_to_[{end_str}].srt"
    )

    return output_clip, output_srt


def create_temp_paths():
    return f"{int(time.time())}.mp4", f"{int(time.time())}.srt"


def calculate_padding_height(subtitle_file, line_height=40, line_spacing=10):
    """
    Calculate the padding height needed based on the maximum number of lines in the subtitles.
    """
    max_lines = 0
    with open(subtitle_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        current_lines = 0
        for line in lines:
            if line.strip() == '':
                if current_lines > max_lines:
                    max_lines = current_lines
                current_lines = 0
            else:
                current_lines += 1
        if current_lines > max_lines:
            max_lines = current_lines

    return max_lines * line_height + (max_lines - 1) * line_spacing


def extract_video_clip(video_file, start_seconds, end_seconds, output_clip, output_srt):
    """
    Extract the video clip using ffmpeg and embed the subtitles.
    """
    padding_height = calculate_padding_height(output_srt)
    vf_filter = f"[0:v]pad=iw:ih+{padding_height}:0:0:black[sub];[sub]subtitles={output_srt}:force_style='Alignment=2'"

    ffmpeg_command = [
        'ffmpeg',
        '-ss', format_ffmpeg_time(start_seconds),
        '-i', video_file,
        '-ss', '0',
        '-to', format_ffmpeg_time(end_seconds - start_seconds),
        '-vf', vf_filter,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_clip
    ]
    subprocess.run(ffmpeg_command, check=True)


def create_srt_file(subs, start_time, end_time, output_srt):
    """
    Create a new SRT file for the extracted clip.
    """
    new_subs = SubRipFile()
    for sub in subs:
        if start_time <= sub.start.to_time() <= end_time:
            new_start_ms = (
                    sub.start.ordinal - start_time.hour * 3600000 - start_time.minute * 60000 - start_time.second * 1000 - start_time.microsecond // 1000)
            new_end_ms = (
                    sub.end.ordinal - start_time.hour * 3600000 - start_time.minute * 60000 - start_time.second * 1000 - start_time.microsecond // 1000)
            new_start = SubRipTime.from_ordinal(new_start_ms)
            new_end = SubRipTime.from_ordinal(new_end_ms)
            new_subs.append(SubRipItem(index=sub.index, start=new_start, end=new_end, text=sub.text))
    new_subs.save(output_srt, encoding='utf-8')


def delete_existing_files(clips_folder, keyword):
    """
    Delete all files in the clips folder that contain the keyword.
    """
    for root, dirs, files in os.walk(clips_folder):
        for file in files:
            if f"「{keyword}」" in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted existing file: {file_path}")


def extract_clips(selected_subtitle_files, base_folder, keyword, prev_count, next_count, overwrite):
    """
    Extract video clips based on the selected subtitle time ranges.
    Also save the corresponding SRT file.
    """
    clips_folder = os.path.join(base_folder, 'clips')
    os.makedirs(clips_folder, exist_ok=True)

    if overwrite:
        delete_existing_files(clips_folder, keyword)

    for subtitle_file, subtitle_index in selected_subtitle_files:
        subs = SubRipFile.open(subtitle_file)
        subtitle = subs[subtitle_index]
        previous_subtitle = get_subtitle(subs, subtitle_index - prev_count)
        next_subtitle = get_subtitle(subs, subtitle_index + next_count)

        start_time = previous_subtitle.start.to_time() if previous_subtitle else subtitle.start.to_time()
        end_time = next_subtitle.end.to_time() if next_subtitle else subtitle.end.to_time()

        video_file = find_video_file(subtitle_file)
        if video_file:
            start_seconds = convert_to_seconds(start_time)
            end_seconds = convert_to_seconds(end_time)
            start_str = format_time(start_time)
            end_str = format_time(end_time)
            video_name = extract_path_parts(video_file)
            temp_clip, temp_srt = create_temp_paths()

            try:
                create_srt_file(subs, start_time, end_time, temp_srt)
                extract_video_clip(video_file, start_seconds, end_seconds, temp_clip, temp_srt)
                output_clip, output_srt = create_output_paths(clips_folder, keyword, video_name, start_str, end_str)
                shutil.move(temp_clip, output_clip)
                shutil.move(temp_srt, output_srt)
                print(f"Extracted clip: {output_clip}")
                print(f"Saved SRT: {output_srt}")
            except Exception as e:
                print(f"Error extracting clip from {video_file}: {e}")
        else:
            print(f"No corresponding video file found for subtitle file: {subtitle_file}")


def main():
    parser = argparse.ArgumentParser(description="Subtitle Keyword Search and Clip Extractor")
    parser.add_argument("--keyword", "-k", type=str, help="Japanese keyword to search for", required=True)
    parser.add_argument("--base_folder", "-b", type=str, help="Root folder to start searching", required=True)
    parser.add_argument("--prev_count", "-p", type=int, default=2,
                        help="Number of subtitles to include before the keyword match")
    parser.add_argument("--next_count", "-n", type=int, default=2,
                        help="Number of subtitles to include after the keyword match")
    parser.add_argument("--overwrite", "-o", action='store_true',
                        help="Delete all existing clips and SRT files containing the keyword before extracting new ones")
    args = parser.parse_args()

    keyword = args.keyword
    base_folder = args.base_folder
    prev_count = args.prev_count
    next_count = args.next_count
    overwrite = args.overwrite

    subtitle_files = search_subtitle_files(base_folder, keyword)
    if subtitle_files:
        print("Found subtitles:")
        for i, (subtitle_file, index) in enumerate(subtitle_files):
            subs = SubRipFile.open(subtitle_file)
            relative_path = os.path.relpath(subtitle_file, base_folder)
            print(f"[{i}] {relative_path} - {subs[index].text}")

        selected_indices = input("Enter the indices of subtitles to clip (comma separated): ")
        selected_indices = [int(index.strip()) for index in selected_indices.split(',')]
        selected_subtitle_files = [(subtitle_files[i][0], subtitle_files[i][1]) for i in selected_indices]

        extract_clips(selected_subtitle_files, base_folder, keyword, prev_count, next_count, overwrite)
    else:
        print("No subtitles found with the given keyword.")


if __name__ == "__main__":
    main()
