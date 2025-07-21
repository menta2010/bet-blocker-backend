from pydantic import BaseModel

def to_pydantic(model_instance, schema: type[BaseModel]):
    """
    Converte uma instância de um modelo SQLAlchemy para um schema Pydantic
    utilizando os atributos do ORM (from_attributes=True).
    """
    return schema.model_validate(model_instance, from_attributes=True)
