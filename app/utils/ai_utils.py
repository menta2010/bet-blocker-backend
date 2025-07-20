from openai import OpenAI
from fastapi import HTTPException
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def gerar_aconselhamento_ia(mensagem: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um conselheiro empático que ajuda pessoas viciadas em apostas a se sentirem acolhidas e motivadas a seguir em frente."},
                {"role": "user", "content": mensagem}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar aconselhamento: {str(e)}")