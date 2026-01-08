import ollama
from google import genai
from google.genai import types

def call_llm(prompt, system_prompt, model_id, client):
    """
    Tries Gemini first.
    Falls back to Ollama if quota / API error occurs.
    """

    # ---------- TRY GEMINI ----------
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text, "gemini"

    except Exception as e:
        error_msg = str(e).lower()

        # ---------- FALLBACK CONDITIONS ----------
        if (
            "quota" in error_msg or
            "429" in error_msg or
            "exceeded" in error_msg or
            "resource exhausted" in error_msg
        ):
            pass
        else:
            raise e  # real error, not quota

    # ---------- OLLAMA FALLBACK ----------
    ollama_response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return ollama_response["message"]["content"], "ollama"
