from openai import OpenAI
from fastapi import HTTPException
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)


def _get_client() -> OpenAI:
    # instancia apenas no uso
    return OpenAI(api_key=settings.openai_api_key)

def gerar_aconselhamento_ia(mensagem: str) -> str:
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um conselheiro empático que ajuda pessoas viciadas em apostas a se sentirem acolhidas e motivadas a seguir em frente."},
                {"role": "user", "content": mensagem}
            ],
            max_tokens=350,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar aconselhamento: {str(e)}")
    
def analisar_texto_diario(texto: str) -> tuple[str, str]:
    prompt = (
        f"Você é uma IA conselheira emocional. O usuário escreveu o seguinte desabafo:\n\n"
        f"{texto}\n\n"
        f"1. Qual é o principal sentimento nesse texto? Seja direto, como: Tristeza, Ansiedade, Raiva, Esperança, etc.\n"
        f"2. Responda de forma empática e motivadora, como se você fosse um terapeuta gentil."
    )

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        partes = resposta.choices[0].message.content.split("\n", 1)
        sentimento = partes[0].strip().replace("1. ", "")
        resposta_ia = partes[1].strip().replace("2. ", "")
        return sentimento, resposta_ia
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar diário: {str(e)}")
    

async def gerar_conselho_emergencial() -> dict:
    prompt = (
        "Imagine que um usuário está prestes a recair no vício de apostas. Dê uma mensagem curta de apoio emocional "
        "e uma dica prática para ajudá-lo a resistir no momento de urgência."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )

    content = response.choices[0].message.content
    partes = content.split("\n", 1)
    return {
        "mensagem_apoio": partes[0].strip(),
        "dica_rapida": partes[1].strip() if len(partes) > 1 else ""
    }
