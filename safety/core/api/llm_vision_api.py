"""对接大模型"""

import json
import os
import base64
import requests
from dotenv import load_dotenv


# 读取 .env 文件
load_dotenv()

class DoubaoVisionClient:
    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY")
        self.endpoint = os.getenv("DOUBAO_ENDPOINT")
        self.model_id = os.getenv("DOUBAO_MODEL_ID")
        if not self.api_key:
            raise Exception('未配置 DOUBAO_API_KEY')

    def encode_image(self, image_path: str) -> str:
        """图片转base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf8')

    def analyze_image(self, image_path: str, prompt: str) -> dict:
        base64_img = self.encode_image(image_path)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}},
                    ]
                }
            ],
            "temperature": 0.1
        }

        try:
            resp = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            resp.raise_for_status()
            res_json = resp.json()
            content = res_json["choices"][0]["message"]["content"].strip()

            # 核心：清洗大模型输出，剔除markdown标记
            content = content.replace("```json", "").replace("```", "").strip()
            # 解析JSON
            parse_data = json.loads(content)
            # 字段校验
            if "risk_list" not in parse_data:
                raise ValueError("返回JSON缺少risk_list字段")
            return {
                "risk_list": parse_data["risk_list"],
            }

        except requests.exceptions.Timeout:
            return {"error": "API调用超时", "risk_list": []}
        except requests.exceptions.RequestException as e:
            return {"error": f"网络请求异常：{str(e)}", "risk_list": []}
        except json.JSONDecodeError:
            return {"error": "大模型返回内容不是合法JSON", "raw_text": content, "risk_list": []}
        except Exception as e:
            return {"error": f"未知异常：{str(e)}", "risk_list": []}