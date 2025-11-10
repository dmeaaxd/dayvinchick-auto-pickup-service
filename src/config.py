from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    OPENAI_API_KEY: str
    TG_API_ID: int
    TG_API_HASH: str
    S3_URL: str


    class Config:
        env_file = ".env"

settings = Config()
