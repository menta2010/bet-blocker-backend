from openai import OpenAI
from fastapi import HTTPException
from app.config import settings
from anyio import to_thread

def _get_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)

async def analisar_diario(texto: str) -> tuple[str, str]:
    prompt = (
        f"Você é uma IA conselheira emocional. O usuário escreveu o seguinte desabafo:\n\n"
        f"{texto}\n\n"
        f"1. Qual é o principal sentimento nesse texto? Seja direto, como: Tristeza, Ansiedade, Raiva, Esperança, etc.\n"
        f"2. Responda de forma empática e motivadora, como se você fosse um terapeuta gentil."
    )

    try:
        client = _get_client()
        resposta = await to_thread.run_sync(lambda: client.chat.completions.create(
        model=settings.OPENAI_MODEL_DIARIO,  
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    ))
        
        partes = resposta.choices[0].message.content.split("\n", 1)
        sentimento = partes[0].strip().replace("1. ", "")
        resposta_ia = partes[1].strip().replace("2. ", "")
        return sentimento, resposta_ia
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar diário: {str(e)}")
