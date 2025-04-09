import os
import re
from typing import List, Dict, Any, Optional
import pysubs2


def parse_srt(content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT subtitle content.

    Args:
        content: SRT subtitle content as string

    Returns:
        List of subtitle entries with index, time_range, and text
    """
    subtitle_pattern = re.compile(
        r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.+\n)+)"
    )
    matches = subtitle_pattern.findall(content)

    subtitles = []
    for match in matches:
        index = int(match[0])
        start_time = match[1]
        end_time = match[2]
        text = match[3].strip()

        subtitles.append({
            "index": index,
            "start_time": start_time,
            "end_time": end_time,
            "text": text,
            "format": "srt",
        })

    return subtitles


def parse_ass(content: str, file_path: str = None) -> List[Dict[str, Any]]:
    """
    Parse ASS/SSA subtitle content using pysubs2.

    Args:
        content: ASS/SSA subtitle content as string
        file_path: Path to the subtitle file (optional, for format detection)

    Returns:
        List of subtitle entries
    """
    try:
        # Try to load from string
        subs = pysubs2.SSAFile.from_string(content)
    except Exception as e:
        # If loading from string fails and we have a file path, try loading from file
        if file_path:
            try:
                subs = pysubs2.load(file_path)
            except Exception as inner_e:
                raise ValueError(
                    f"Failed to parse ASS/SSA file: {inner_e}"
                ) from inner_e
        else:
            raise ValueError(f"Failed to parse ASS/SSA content: {e}") from e

    subtitles = []
    for i, line in enumerate(subs):
        # Get plain text without formatting codes
        raw_text = line.text

        plain_text = re.sub(r'\\n', r'\\N', raw_text, flags=re.IGNORECASE)
        plain_text = re.sub(r'(\{[^}]*\})', r'<*>', plain_text, flags=re.IGNORECASE | re.MULTILINE)

        subtitles.append({
            "index": i + 1,
            "start_time": str(line.start),  # in milliseconds
            "end_time": str(line.end),  # in milliseconds
            "text": plain_text,
            "raw_text": raw_text,
            "format": "ass",
            "line": line,  # Store the pysubs2 line object for later use
            "meta": {
                "style": line.style,
                "name": line.name,
                "effect": line.effect,
                "layer": line.layer,
                "marginl": line.marginl,
                "marginr": line.marginr,
                "marginv": line.marginv,
            },
            # Store parent SSAFile for later use
            "parent_file": subs
        })

    return subtitles


def format_timestamp_for_srt(ms: int) -> str:
    """
    Format milliseconds as SRT timestamp (HH:MM:SS,mmm).

    Args:
        ms: Time in milliseconds

    Returns:
        Formatted timestamp
    """
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_srt(subtitles: List[Dict[str, Any]], output_path: str) -> None:
    """
    Write subtitles to an SRT file.

    Args:
        subtitles: List of subtitle entries
        output_path: Path to save the SRT file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for subtitle in subtitles:
            f.write(f"{subtitle['index']}\n")

            # If stored as milliseconds (from pysubs2), format properly
            if subtitle["start_time"].isdigit():
                start_time = format_timestamp_for_srt(int(subtitle["start_time"]))
                end_time = format_timestamp_for_srt(int(subtitle["end_time"]))
                f.write(f"{start_time} --> {end_time}\n")
            else:
                f.write(f"{subtitle['start_time']} --> {subtitle['end_time']}\n")

            f.write(f"{subtitle['text']}\n\n")


def write_ass(
    subtitles: List[Dict[str, Any]], output_path: str, original_content: str = None
) -> None:
    """
    Write subtitles to an ASS/SSA file using pysubs2.

    Args:
        subtitles: List of subtitle entries
        output_path: Path to save the ASS file
        original_content: Original ASS content (only used as fallback)
    """
    # Check if we have pysubs2 line objects
    if subtitles and "line" in subtitles[0]:
        # Get the parent file if available
        parent_file = None
        for subtitle in subtitles:
            if "parent_file" in subtitle:
                parent_file = subtitle["parent_file"]
                break
                
        # Create a new SSA file
        if parent_file:
            # Clone the parent file (copy styles and info)
            subs = pysubs2.SSAFile()
            subs.styles = parent_file.styles.copy()
            subs.info = parent_file.info.copy()
        else:
            # Create new file with default settings
            subs = pysubs2.SSAFile()
        
        # Clear any existing events
        subs.events.clear()
        
        # Add all events with updated text
        for subtitle in subtitles:
            line = subtitle["line"].copy()
            # Update text with corrected version
            if "text" in subtitle:
                corrected_text: str = subtitle["text"]
                
                # Ensure \N is preserved in the corrected text
                # Convert \n to \N to maintain ASS format
                corrected_text = corrected_text.replace('\n', '\\N')
                corrected_text = corrected_text.replace('\\n', '\\N')
                
                # For ASS, we may need to preserve formatting tags
                if "{" in line.text and "}" in line.text:
                    # Extract and preserve formatting tags
                    actual_tags = re.findall(r"(\{[^}]*\})", line.text)
                    tags = re.findall("<*>", corrected_text)
                    for actual_tag, tag in zip(actual_tags, tags):
                        corrected_text = corrected_text.replace(tag, actual_tag, 1)
                else:
                    line.text = corrected_text
            
            # Add the line to the new file
            subs.events.append(line)
        
        # Save the file
        subs.save(output_path)
        
    else:
        # Fallback to old method if we don't have pysubs2 line objects
        if not original_content:
            raise ValueError("Original ASS content required for fallback ASS writing")

        header_match = re.search(
            r"(.*?\[Events\].*?Format:.*?\n)", original_content, re.DOTALL
        )
        if not header_match:
            raise ValueError("Invalid ASS format: couldn't find Events section")

        header = header_match.group(1)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header)

            for subtitle in subtitles:
                if "raw_text" in subtitle:
                    # Use the raw text with formatting codes
                    text = subtitle["raw_text"]
                else:
                    # If raw text not available, use the corrected text
                    text = subtitle["text"]

                if "line_data" in subtitle:
                    line_data = subtitle["line_data"].copy()

                    # Get format line to find the text index
                    format_line = re.search(r"Format:(.*?)$", header, re.MULTILINE)
                    if format_line:
                        fields = [
                            field.strip() for field in format_line.group(1).split(",")
                        ]
                        text_idx = fields.index("Text") if "Text" in fields else -1

                        if text_idx != -1 and text_idx < len(line_data):
                            line_data[text_idx] = text

                            # Write dialogue line
                            f.write(f"Dialogue: {','.join(line_data)}\n")
                else:
                    # Simple fallback if we don't have line data
                    f.write(
                        f"Dialogue: 0,{subtitle['start_time']},{subtitle['end_time']},Default,,0,0,0,,{text}\n"
                    )


def parse_subtitle_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Parse a subtitle file (SRT or ASS).

    Args:
        filepath: Path to the subtitle file

    Returns:
        List of subtitle entries
    """
    _, ext = os.path.splitext(filepath.lower())

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if ext == ".srt":
        return parse_srt(content)
    elif ext in [".ass", ".ssa"]:
        return parse_ass(content, filepath)
    else:
        raise ValueError(f"Unsupported subtitle format: {ext}")


def write_subtitle_file(subtitles: List[Dict[str, Any]], output_path: str) -> None:
    """
    Write subtitles to a file.

    Args:
        subtitles: List of subtitle entries
        output_path: Path to save the subtitle file
    """
    if not subtitles:
        raise ValueError("No subtitles to write")

    _, ext = os.path.splitext(output_path.lower())

    if ext == ".srt":
        write_srt(subtitles, output_path)
    elif ext in [".ass", ".ssa"]:
        # If we have a pysubs2 line object, we don't need the original content
        if "line" in subtitles[0]:
            write_ass(subtitles, output_path)
        else:
            original_path = subtitles[0].get("original_filepath", "")
            if not original_path:
                raise ValueError(
                    "Original filepath required for ASS/SSA format when pysubs2 line objects are unavailable"
                )
            else:
                with open(original_path, "r", encoding="utf-8") as f:
                    original_content = f.read()
                write_ass(subtitles, output_path, original_content)
    else:
        raise ValueError(f"Unsupported subtitle format: {ext}")
