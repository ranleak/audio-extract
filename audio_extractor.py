import os
import sys
from typing import List

# Attempt to handle different versions of MoviePy (v1.x vs v2.x)
try:
    # Try legacy/v1 style first
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        # Try new v2 style
        from moviepy import VideoFileClip
    except ImportError:
        print(f"\n[!] Error: Could not find 'moviepy'.")
        print(f"Current Python path: {sys.executable}")
        print(f"Try running: {sys.executable} -m pip install moviepy")
        sys.exit(1)

# Import Rich
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.theme import Theme
except ImportError:
    print(f"\n[!] Error: Could not find 'rich'.")
    print(f"Try running: {sys.executable} -m pip install rich")
    sys.exit(1)

# Custom theme for a professional look
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "magenta"
})

console = Console(theme=custom_theme)

class AudioExtractor:
    def __init__(self):
        self.supported_formats = ["mp3", "m4a", "wav"]
        self.bitrates = ["128k", "192k", "256k", "320k"]

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_header(self):
        console.print(Panel.fit(
            "[bold cyan]🎬 Video to Audio Extractor Pro[/bold cyan]\n"
            "[italic white]High-quality extraction using MoviePy & Rich[/italic white]",
            border_style="cyan"
        ))

    def get_video_files(self) -> List[str]:
        """Scan current directory for mp4 files."""
        files = [f for f in os.listdir('.') if f.lower().endswith('.mp4')]
        return sorted(files)

    def display_file_table(self, files: List[str]):
        table = Table(title="Available MP4 Videos", expand=True)
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Filename", style="white")
        table.add_column("Size (MB)", justify="right", style="green")

        for idx, file in enumerate(files, 1):
            size = os.path.getsize(file) / (1024 * 1024)
            table.add_row(str(idx), file, f"{size:.2f}")
        
        console.print(table)

    def run(self):
        self.clear_screen()
        self.show_header()

        # 1. Locate Files
        video_files = self.get_video_files()
        if not video_files:
            console.print("[error]No .mp4 files found in the current directory![/error]")
            console.print("[info]Tip: Make sure your .mp4 files are in this same folder.[/info]")
            return

        self.display_file_table(video_files)

        # 2. Select File
        choice = IntPrompt.ask(
            "\n[info]Select a file ID to process[/info]", 
            choices=[str(i) for i in range(1, len(video_files) + 1)]
        )
        input_file = video_files[choice - 1]

        # 3. Select Format
        console.print(f"\n[info]Supported formats:[/info] {', '.join(self.supported_formats)}")
        output_format = Prompt.ask(
            "[info]Choose output format[/info]", 
            choices=self.supported_formats, 
            default="mp3"
        )

        # 4. Select Bitrate
        bitrate = Prompt.ask(
            "[info]Choose bitrate (higher = better quality)[/info]", 
            choices=self.bitrates, 
            default="192k"
        )

        # 5. Process Extraction
        output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
        
        console.print(f"\n[highlight]Processing:[/highlight] {input_file} ➔ {output_file}\n")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
                transient=True
            ) as progress:
                
                task = progress.add_task("[cyan]Initializing...", total=100)
                
                # Load video
                video = VideoFileClip(input_file)
                progress.update(task, completed=30, description="[cyan]Analyzing audio stream...")
                
                # Extract audio
                audio = video.audio
                if audio is None:
                    console.print("[error]This video file has no audio track![/error]")
                    video.close()
                    return

                progress.update(task, completed=60, description="[cyan]Encoding audio (FFmpeg)...")
                
                # Write file
                audio.write_audiofile(
                    output_file, 
                    bitrate=bitrate, 
                    logger=None 
                )
                
                progress.update(task, completed=100, description="[success]Done!")

            # Cleanup
            audio.close()
            video.close()

            console.print(Panel(
                f"[success]Success![/success]\n\n"
                f"File: [white]{output_file}[/white]\n"
                f"Bitrate: [white]{bitrate}[/white]\n"
                f"Location: [italic]{os.path.abspath(output_file)}[/italic]",
                title="Conversion Complete",
                border_style="green"
            ))

        except Exception as e:
            console.print(f"\n[error]An error occurred during extraction:[/error] {str(e)}")

if __name__ == "__main__":
    try:
        extractor = AudioExtractor()
        extractor.run()
    except KeyboardInterrupt:
        console.print("\n[warning]Operation cancelled by user.[/warning]")
        sys.exit(0)