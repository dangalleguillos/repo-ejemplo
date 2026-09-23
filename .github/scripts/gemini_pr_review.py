import os
from pathlib import Path

from google import genai


def read_diff(path: str) -> str:
    diff_file = Path(path)
    if not diff_file.exists():
        return ""

    text = diff_file.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return ""

    max_chars = 25000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[...diff truncado por longitud...]"

    return text


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Falta GEMINI_API_KEY en los secrets del repositorio.")

    diff = read_diff("pr.diff")
    if not diff:
        Path("gemini_review.md").write_text("No encontré cambios relevantes para revisar.", encoding="utf-8")
        return

    prompt = f"""Eres un revisor de código senior. Revisa este diff de Pull Request y responde en español. 

Haz lo siguiente:
- Identifica errores reales, riesgos o bugs.
- Señala problemas concretos con un ejemplo si aplica.
- Da sugerencias pequeñas y útiles.
- Si no encuentras problema importante, responde exactamente: No encontré riesgos importantes.
- No hagas comentarios vacíos de estilo.

Diff:
```diff
{diff}
```"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    review = getattr(response, "text", None) or str(response)
    Path("gemini_review.md").write_text(review, encoding="utf-8")
    print(review)


if __name__ == "__main__":
    main()
