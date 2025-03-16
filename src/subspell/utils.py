from typing import List, Dict, Any, Tuple
import re


def count_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text.
    This is a simple approximation; actual tokens depend on the tokenizer.

    Args:
        text: The text to count tokens for

    Returns:
        Estimated token count
    """
    # A simple approximation: count words and punctuation
    # This is not perfect but works as a conservative estimate
    words = re.findall(r"\w+", text)
    punctuation = re.findall(r"[^\w\s]", text)
    return len(words) + len(punctuation)


def chunk_text(text: str, max_tokens: int = 5000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks that fit within the token limit.

    Args:
        text: Text to split
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks for context

    Returns:
        List of text chunks
    """
    if count_tokens(text) <= max_tokens:
        return [text]

    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)

        # If a single paragraph is too large, split it by sentences
        if paragraph_tokens > max_tokens:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence)

                # If adding this sentence would exceed the limit, start a new chunk
                if current_tokens + sentence_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence
                    current_tokens = sentence_tokens
                else:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                    current_tokens += sentence_tokens
        else:
            # If adding this paragraph would exceed the limit, start a new chunk
            if current_tokens + paragraph_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
                current_tokens = paragraph_tokens
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_tokens += paragraph_tokens

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    # Add overlaps between chunks for better context
    if len(chunks) > 1 and overlap > 0:
        overlap_chunks = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlap_chunks.append(chunk)
            else:
                # Get the last part of the previous chunk for overlap
                prev_chunk = chunks[i - 1]
                overlap_text = get_overlap_text(prev_chunk, overlap)
                overlap_chunks.append(overlap_text + chunk)

        return overlap_chunks

    return chunks


def get_overlap_text(text: str, overlap_tokens: int) -> str:
    """
    Get the last N tokens of text for overlap.

    Args:
        text: Source text
        overlap_tokens: Number of tokens to include

    Returns:
        Overlap text
    """
    words = re.findall(r"\S+", text)
    if len(words) <= overlap_tokens:
        return text

    return " ".join(words[-overlap_tokens:]) + " "


def merge_corrected_chunks(
    original_text: str,
    corrected_chunks: List[str],
    chunk_boundaries: List[Tuple[int, int]],
) -> str:
    """
    Merge corrected chunks back into a single text.

    Args:
        original_text: Original text before chunking
        corrected_chunks: List of corrected text chunks
        chunk_boundaries: List of (start, end) positions of each chunk

    Returns:
        Merged corrected text
    """
    if len(corrected_chunks) == 1:
        return corrected_chunks[0]

    # For more complex merging, we'd need to align the original and corrected text
    # This is a simplified version that works best when chunks are based on natural boundaries
    result = ""
    for i, (chunk, (start, end)) in enumerate(zip(corrected_chunks, chunk_boundaries)):
        # For all except the first chunk, we need to handle the overlap
        if i > 0:
            # Simple approach: take the second half of each chunk except the first
            # This is not perfect but avoids most duplications from overlaps
            words = chunk.split()
            half_point = max(1, len(words) // 2)
            result += " " + " ".join(words[half_point:])
        else:
            result = chunk

    return result


def batch_items(
    items: List[Dict[str, Any]], max_tokens: int, text_key: str = "text"
) -> List[List[Dict[str, Any]]]:
    """
    Group items into batches that fit within the token limit.
    Uses a queue-based approach to maximize resource usage.

    Args:
        items: List of items (dictionaries) with text to batch
        max_tokens: Maximum tokens per batch
        text_key: Key in the dictionary that contains the text

    Returns:
        List of batches, where each batch is a list of items
    """
    if not items:
        return []

    batches = []
    current_batch = []
    current_token_count = 0
    separator_tokens = count_tokens("\n===SUBTITLE_SEPARATOR===\n")

    for item in items:
        item_text = item[text_key]
        item_tokens = count_tokens(item_text)

        # If this item alone exceeds the token limit, add it as its own batch
        if item_tokens >= max_tokens:
            # If we have existing items in the batch, finalize it first
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_token_count = 0

            # Add this large item as its own batch
            batches.append([item])
            continue

        # Check if adding this item would exceed the token limit
        # Include separator tokens as well
        if (
            current_batch
            and current_token_count + item_tokens + separator_tokens > max_tokens
        ):
            batches.append(current_batch)
            current_batch = [item]
            current_token_count = item_tokens
        else:
            current_batch.append(item)
            if current_batch:
                # Add separator tokens if this isn't the first item
                current_token_count += item_tokens + (
                    separator_tokens if len(current_batch) > 1 else 0
                )
            else:
                current_token_count = item_tokens

    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches
