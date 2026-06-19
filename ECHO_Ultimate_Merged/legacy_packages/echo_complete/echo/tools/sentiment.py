from core.exceptions import ToolException

def sentiment(text: str) -> str:
    """Analyse sentiment using TextBlob or VADER."""
    try:
        try:
            from textblob import TextBlob
            pol = TextBlob(text).sentiment.polarity
            label = "positivo" if pol > 0.05 else "negativo" if pol < -0.05 else "neutro"
            return f"{label} (polaridade={pol:.3f})"
        except Exception:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            sia = SentimentIntensityAnalyzer()
            score = sia.polarity_scores(text)
            return str(score)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta sentiment: {e}") from e
