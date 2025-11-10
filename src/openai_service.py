import aiohttp
from openai import OpenAI

from src.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:
    file_path: str = "/photos"

    async def send_file_to_s3(self) -> str:
        headers = {'accept': '*/*'}

        async with aiohttp.ClientSession() as session:
            with open(self.file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field(
                    'file',
                    f,
                    filename=self.file_path.replace('temp/', ''),
                    content_type='application/octet-stream'
                )

                async with session.post(settings.S3_URL,
                                        headers=headers,
                                        data=data,
                                        ssl=False) as resp:
                    resp_text = await resp.text()
                    return resp_text.strip()

    async def check_image(self) -> bool:
        # 1. Загружаем файл на сервис
        url = await self.send_file_to_s3()
        print("Uploaded file URL:", url)

        # 2. Отправляем запрос в OpenAI
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Мне нужно чтобы ты по моему описанию моего будущую девушку"
                            "определила подходит он мне или нет. Я люблю молодых девушек (от 18 до 27 лет), "
                            "не толстых, не рыжих. На фото обязательно должно быть лицо. "
                            "Ты должна ответить однозначно одним из двух символов и никак иначе: + или -."
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": url
                    }
                ],
            }],
        )

        # 3. Проверяем ответ
        text = response.output_text.strip()
        print(text)
        if text == '+':
            return True
        elif text == '-':
            return False
        else:
            # на всякий случай — если модель прислала что-то непонятное
            raise ValueError(f"Unexpected model output: {text}")
