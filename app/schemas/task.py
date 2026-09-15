from pydantic import BaseModel, ConfigDict


#-----------------Модели задач-----------------
class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    completed: bool = False

class TaskCreateSchema(BaseModel):
    title: str

class TaskUpdateSchema(BaseModel):
    title : str | None = None
    completed : bool | None = None