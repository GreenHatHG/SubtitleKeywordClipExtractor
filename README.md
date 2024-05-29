# SubtitleKeywordClipExtractor

SubtitleKeywordClipExtractor is a Python tool that searches for specific keywords in subtitle files and extracts corresponding video clips. It supports various video formats and uses `ffmpeg` for video processing.

## Features

- Search through `.srt` subtitle files for a specified keyword.
- Extract video clips based on the time ranges of the found subtitles.
- Supports multiple video formats including `.mp4`, `.mkv`, `.avi`, `.mov`, and `.flv`.
- Automatically finds the video file corresponding to a subtitle file.
- Creates a directory for storing extracted clips.
- Names the extracted clips based on the keyword, video name, and time range.

## Requirements

- Python 3.x
- Python library: requirements.txt
- `ffmpeg` installed and accessible from the command line

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/GreenHatHG/SubtitleKeywordClipExtractor
    cd SubtitleKeywordClipExtractor
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure `ffmpeg` is installed on your system. You can download it from [FFmpeg official website](https://ffmpeg.org/download.html).
     
## Usage

1. Modify the `base_folder` variable in `main.py` to point to your base directory, and ensure the directory structure matches the following:
    ```
    base_folder
      ├── Show1
      │     ├── 1.mp4
      │     └── 1.srt
      └── Show2
            ├── 2.mp4
            └── 2.srt
    ```

2. Run the script:
    ```bash
    python main.py
    ```
3. Follow the prompts:
    - Enter the Japanese keyword to search for.
    - Enter the indices of the subtitles you want to clip (comma-separated).

## Usage Example

```
D:\scoop\apps\python37\current\python.exe main.py
Enter the Japanese keyword to search for: 映画
Found subtitles:
[0] d:\Demo\show1\1.srt - 映画の ど頭にピラミッドみたいな
壮大な建物が出てくるでしょ
[1] d:\Demo\show1\1.srt - あっ 見てないです その映画
[2] d:\Demo\show1\1.srt - 私 メジャーな映画しか見なくて
[3] d:\Demo\show1\1.srt - （信介）十分メジャーだけど
（英治）オタク映画
[4] d:\Demo\show1\1.srt - 「ブレードランナー」を見る前に
押さえておく映画としては—
[5] d:\Demo\show1\1.srt - これ 映画本編じゃなくて
メーキングですけど—
[6] d:\Demo\show1\1.srt - 映画 見ても
同じじゃないですか
[7] d:\Demo\show1\3.srt - あっ よかったら この映画の
パート２ 入荷してますんで
Enter the indices of subtitles to clip (comma separated): 5
Extracted clip: d:\Demo\clips\「映画」_[show1-1.mp4]_[00-06-50]_to_[00-07-04].mp4
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
