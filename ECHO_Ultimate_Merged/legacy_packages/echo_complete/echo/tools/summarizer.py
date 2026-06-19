from core.exceptions import ToolException

def summarizer(text: str, max_sentences: int = 5) -> str:
    """Summarize text locally with a lightweight extractive heuristic."""
    try:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s for s in sentences if s]
        if len(sentences) <= max_sentences:
            return text.strip()
        scored = []
        words = re.findall(r"\w+", text.lower())
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        for idx, s in enumerate(sentences):
            score = sum(freq.get(w.lower(), 0) for w in re.findall(r"\w+", s))
            scored.append((score, idx, s))
        top = sorted(scored, reverse=True)[:max_sentences]
        top = sorted(top, key=lambda x: x[1])
        return " ".join(s for _, _, s in top)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta summarizer: {e}") from e
