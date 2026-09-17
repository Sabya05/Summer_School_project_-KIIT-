# NewsLens AI

AI-powered news research & summarization assistant, built as a Streamlit app.

**Pipeline:** your question → Tavily live web search → source cleaning/dedup → Gemini synthesis → structured research report + sources + 3 follow-up questions.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your keys
streamlit run app.py
```

`.env`
```
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Research modes
- **Quick Brief** — fast, high-level overview.
- **Deep Research** — structured multi-section investigation with sourced claims.
- **Explain Simply** — plain-language explanation for non-experts.

## Structure
```
app.py                  Streamlit UI + orchestration
config.py                Env vars, constants, mode metadata
services/tavily_service.py   Live web search + cleanup
services/gemini_service.py   Prompting Gemini, parsing response
utils/text_utils.py      Cleaning, dedup, truncation helpers
styles/style.css          Cinematic dark UI theme
```

## Notes
- Gemini is instructed to cite sources as `[n]` and never invent facts beyond what Tavily returns.
- Model is set in `config.py` (`GEMINI_MODEL`) — update there if Google renames/deprecates it.
- Never commit `.env`; only `.env.example` is tracked.
