import os
import subprocess
from pysrt import SubRipFile


def search_subtitle_files(folder, keyword):
    """
    Search for subtitles containing the given keyword in the specified folder and its subfolders.
    """
    subtitle_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.srt'):
                subtitle_file_path = os.path.join(root, file)
                subs = SubRipFile.open(subtitle_file_path)
                for sub in subs:
                    if keyword in sub.text:
                        subtitle_files.append((subtitle_file_path, sub))
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


def extract_clips(selected_subtitle_files, base_folder, keyword):
    """
    Extract video clips based on the selected subtitle time ranges.
    """
    clips_folder = os.path.join(base_folder, 'clips')
    os.makedirs(clips_folder, exist_ok=True)

    for subtitle_file, subtitle_index in selected_subtitle_files:
        subs = SubRipFile.open(subtitle_file)
        subtitle = subs[subtitle_index]
        previous_subtitle = get_subtitle(subs, subtitle_index - 1)
        next_subtitle = get_subtitle(subs, subtitle_index + 1)

        if previous_subtitle:
            start_time = previous_subtitle.start.to_time()
        else:
            start_time = subtitle.start.to_time()

        if next_subtitle:
            end_time = next_subtitle.end.to_time()
        else:
            end_time = subtitle.end.to_time()

        video_file = find_video_file(subtitle_file)

        if video_file:
            start_seconds = convert_to_seconds(start_time)
            end_seconds = convert_to_seconds(end_time)
            start_str = format_time(start_time)
            end_str = format_time(end_time)

            video_name = extract_path_parts(video_file)

            output_clip = os.path.join(
                clips_folder,
                f"「{keyword}」_[{video_name}]_[{start_str}]_to_[{end_str}].mp4"
            )

            try:
                ffmpeg_command = [
                    'ffmpeg',
                    '-ss', format_ffmpeg_time(start_seconds),
                    '-i', video_file,
                    '-ss', '0',
                    '-to', format_ffmpeg_time(end_seconds - start_seconds),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    output_clip
                ]
                subprocess.run(ffmpeg_command, check=True)
                print(f"Extracted clip: {output_clip}")
            except subprocess.CalledProcessError as e:
                print(f"Error extracting clip from {video_file}: {e}")
        else:
            print(f"No corresponding video file found for subtitle file: {subtitle_file}")


def extract_path_parts(file_path):
    """
    Extract the last two directory names and the file name (without extension) from the given file path.
    """
    # Get the directory path and file name
    dir_path, file_name = os.path.split(file_path)

    dir_parts = dir_path.split(os.sep)

    # Combine the parts
    result = f"{dir_parts[-1]}-{file_name}"

    return result

def format_time(time_obj):
    """
    Format a datetime.time object to a string (HH-MM-SS).
    """
    return time_obj.strftime("%H-%M-%S")


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


def main():
    keyword = input("Enter the Japanese keyword to search for: ")
    base_folder = r'd:\1'  # Root folder to start searching

    subtitle_files = search_subtitle_files(base_folder, keyword)
    if subtitle_files:
        print("Found subtitles:")
        for i, (subtitle_file, subtitle) in enumerate(subtitle_files):
            print(f"[{i}] {subtitle_file} - {subtitle.text}")

        selected_indices = input("Enter the indices of subtitles to clip (comma separated): ")
        selected_indices = [int(index.strip()) for index in selected_indices.split(',')]
        selected_subtitle_files = [(subtitle_files[i][0], subtitle_files[i][1].index) for i in selected_indices]

        extract_clips(selected_subtitle_files, base_folder, keyword)
    else:
        print("No subtitles found with the given keyword.")


if __name__ == "__main__":
    main()