import os
import re
from typing import List, Dict, Optional, Any, Tuple

from .providers.base import ModelProvider
from .providers.gemini import GeminiProvider
from .utils import chunk_text, merge_corrected_chunks, count_tokens, batch_items


class SpellChecker:
    """Main spellchecker class that handles text correction."""

    def __init__(
        self,
        provider_name: str = "gemini",
        max_tokens_per_chunk: int = 8192,
        chunk_overlap: int = 200,
        system_instruction: Optional[str] = None,
        system_instruction_file: Optional[str] = None,
        temperature: float = 0.2,
        top_k: int = 40,
        top_p: float = 0.95,
        model: str = "gemini-2.0-flash",
        **provider_kwargs,
    ):
        """
        Initialize the spellchecker with a model provider.

        Args:
            provider_name: Name of the model provider to use
            max_tokens_per_chunk: Maximum tokens per chunk for batch processing
            chunk_overlap: Number of tokens to overlap between chunks for context
            system_instruction: Inline system instruction text for the model
            system_instruction_file: Path to a file containing system instructions
            temperature: Controls randomness in the output (0.0 to 1.0)
            top_k: Controls diversity via top-k sampling
            top_p: Controls diversity via nucleus sampling
            model: The model to use (e.g. "gemini-2.0-flash", "gemini-pro-vision")
            **provider_kwargs: Additional arguments for the provider
        """
        self.provider = self._get_provider(
            provider_name,
            system_instruction=system_instruction,
            system_instruction_file=system_instruction_file,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            model=model,
            **provider_kwargs
        )
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.chunk_overlap = chunk_overlap

    def _get_provider(self, provider_name: str, **kwargs) -> ModelProvider:
        """Get the model provider based on name."""
        if provider_name.lower() == "gemini":
            api_key = kwargs.get("api_key") or os.environ.get("GEMINI_API_KEY")
            return GeminiProvider(
                api_key=api_key,
                system_instruction=kwargs.get("system_instruction"),
                system_instruction_file=kwargs.get("system_instruction_file"),
                temperature=kwargs.get("temperature"),
                top_k=kwargs.get("top_k"),
                top_p=kwargs.get("top_p"),
                model=kwargs.get("model", "gemini-2.0-flash"),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def correct_subtitles(self, subtitles: list[str], batch_size: int = 0) -> list[str]:
        """
        Correct spelling, punctuation, and grammar in the given subtitles.

        Args:
            subtitles: The subtitle text[s] to correct
            batch_size: Max batch size (0 means use token-based batching)
        Returns:
            The corrected subtitles
        """
        # Process subtitles in token-optimized batches
        separator_str = "§SEP§"
        if batch_size == 0:
            # Use token-based batching - fill each batch to maximum capacity
            batches = batch_items(
                [{"text": subtitle} for subtitle in subtitles],
                self.max_tokens_per_chunk,
                "text",
                separator_str,
            )
            batches = [[subtitle["text"] for subtitle in batch] for batch in batches]
        else:
            # Use fixed batch size if explicitly specified
            total_subtitles = len(subtitles)
            batches = [
                subtitles[i : min(i + batch_size, total_subtitles)]
                for i in range(0, total_subtitles, batch_size)
            ]

        # Process each batch
        corrected_subtitles = []
        for batch in batches:
            # Skip empty batches
            if not batch:
                continue

            # Combine texts with markers to separate them
            combined_text = str.join(separator_str, batch)

            # Process the combined text
            corrected_combined = self.provider.correct_text(combined_text)

            
            if corrected_combined.endswith(
                separator_str[:-1]
            ) or corrected_combined.endswith(separator_str[:-2]):
                corrected_combined += "\n"  # Ensure it ends with a newline

            # Split the corrected text back into individual subtitles
            corrected_texts = corrected_combined.split(separator_str)
            corrected_subtitles.extend(corrected_texts)

        return corrected_subtitles

    def correct_text(self, text: str) -> str:
        """
        Correct spelling, punctuation, and grammar in the given text.
        Handles batching for long texts.

        Args:
            text: The text to correct

        Returns:
            The corrected text
        """
        # Short texts can be processed directly
        if count_tokens(text) <= self.max_tokens_per_chunk:
            return self.provider.correct_text(text)

        # For longer texts, chunk and process in batches
        chunks = chunk_text(text, self.max_tokens_per_chunk, self.chunk_overlap)
        corrected_chunks = []

        for chunk in chunks:
            corrected_chunk = self.provider.correct_text(chunk)
            corrected_chunks.append(corrected_chunk)

        # Create chunk boundaries for merging
        chunk_boundaries = []
        pos = 0
        for chunk in chunks:
            chunk_len = len(chunk)
            chunk_boundaries.append((pos, pos + chunk_len))
            pos += chunk_len - self.chunk_overlap  # Adjust for overlap

        # Merge the corrected chunks
        return merge_corrected_chunks(text, corrected_chunks, chunk_boundaries)

    def correct_subtitle_file(
        self, filepath: str, output_filepath: Optional[str] = None, batch_size: int = 0
    ) -> str:
        """
        Correct spelling, punctuation, and grammar in a subtitle file.
        Uses queue-based batching to maximize resource usage.

        Args:
            filepath: Path to the subtitle file
            output_filepath: Path to save the corrected file (optional)
            batch_size: Max batch size (0 means use token-based batching)

        Returns:
            Path to the corrected file
        """
        from .subtitle import parse_subtitle_file, write_subtitle_file

        subtitle_data = parse_subtitle_file(filepath)

        # Store original filepath for ASS format
        for item in subtitle_data:
            item["original_filepath"] = filepath

        # Process subtitles in token-optimized batches
        if batch_size == 0:
            # Use token-based batching - fill each batch to maximum capacity
            batches = batch_items(subtitle_data, self.max_tokens_per_chunk)
        else:
            # Use fixed batch size if explicitly specified
            total_subtitles = len(subtitle_data)
            batches = [
                subtitle_data[i : min(i + batch_size, total_subtitles)]
                for i in range(0, total_subtitles, batch_size)
            ]

            # Verify each batch doesn't exceed token limit
            filtered_batches = []
            for batch in batches:
                # Keep reducing batch size until it fits
                while batch:
                    combined_text = "\n===SUBTITLE_SEPARATOR===\n".join(
                        item["text"] for item in batch
                    )
                    if (
                        count_tokens(combined_text) <= self.max_tokens_per_chunk
                        or len(batch) == 1
                    ):
                        filtered_batches.append(batch)
                        break
                    batch = batch[:-1]  # Remove last item

            batches = filtered_batches

        # Process each batch
        for batch in batches:
            # Skip empty batches
            if not batch:
                continue
            
            # For ASS subtitles, temporarily convert \N to a placeholder that won't be modified
            for item in batch:
                if item.get("format") == "ass":
                    # Use a unique placeholder that won't be changed by the model
                    item["text"] = item["text"].replace("\\N", "§LINEBREAK§")
            
            # Combine texts with markers to separate them
            combined_text = "\n===SUBTITLE_SEPARATOR===\n".join(item["text"] for item in batch)
            
            # Process the combined text
            corrected_combined = self.correct_text(combined_text)
            
            # Split the corrected text back into individual subtitles
            corrected_texts = corrected_combined.split("\n===SUBTITLE_SEPARATOR===\n")
            
            # Update the subtitle data - match by index in the batch
            for i, corrected_text in enumerate(corrected_texts):
                if i < len(batch):
                    # Convert the placeholders back to \N
                    corrected = corrected_text.strip()
                    if batch[i].get("format") == "ass":
                        corrected = corrected.replace("§LINEBREAK§", "\\N")
                    
                    # Update the text while preserving formatting codes for ASS/SSA
                    if batch[i].get("format") == "ass" and "line" in batch[i]:
                        # For ASS with pysubs2 line objects, update the text
                        batch[i]["text"] = corrected
                    else:
                        # For SRT or other formats, just update the text
                        batch[i]["text"] = corrected

        # If no output path provided, create one
        if not output_filepath:
            base, ext = os.path.splitext(filepath)
            output_filepath = f"{base}_corrected{ext}"

        # Write the corrected subtitle file
        write_subtitle_file(subtitle_data, output_filepath)

        return output_filepath
