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

## Directory Structure Example

```
base_folder
  ├── Show1
  │     ├── 1.mp4
  │     └── 1.srt
  └── Show2
        ├── 2.mp4
        └── 2.srt
```
     
## Usage

1. Make sure your video files and corresponding subtitle files are in the same directory or subdirectories.
2. Run the script:
    ```bash
    python main.py
    ```
3. Follow the prompts:
    - Enter the Japanese keyword to search for.
    - Enter the indices of the subtitles you want to clip (comma-separated).
  
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any questions or suggestions, please submit issue.
