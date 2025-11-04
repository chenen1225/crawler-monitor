import requests
import os
from typing import Optional

class TextSummarizer:
    \"\"\"
    文本摘要生成器
    使用本地或远程AI模型生成一句话摘要
    \"\"\"
    
    def __init__(self):
        # 尝试使用环境变量中的API密钥，或使用本地模型
        self.api_key = os.getenv(\"OPENAI_API_KEY\")  # 支持OpenAI API
        self.base_url = os.getenv(\"OPENAI_BASE_URL\", \"https://api.openai.com/v1\")
    
    def summarize_text(self, text: str, max_length: int = 100) -> Optional[str]:
        \"\"\"
        对文本进行摘要
        \"\"\"
        if len(text) < 50:
            # 如果文本太短，直接返回
            return text[:max_length]
        
        # 截取文本的前1000个字符作为摘要输入
        input_text = text[:1000]
        
        try:
            # 这里我们使用简单的启发式方法作为占位符
            # 在实际部署中，可以替换为真实的AI模型调用
            sentences = input_text.split('。')
            if len(sentences) > 1:
                return sentences[0].strip() + \"。\" if sentences[0].strip().endswith('。') else sentences[0].strip() + \"...\"
            
            # 如果没有句号，按逗号分割
            sentences = input_text.split('，')
            if len(sentences) > 1:
                return sentences[0].strip() + \"...\"
            
            # 如果都没有，返回前50个字符
            return input_text[:50] + \"...\" if len(input_text) > 50 else input_text
        except Exception as e:
            print(f\"Error summarizing text: {str(e)}\")
            return input_text[:50] + \"...\" if len(input_text) > 50 else input_text

    def summarize_with_openai(self, text: str, max_length: int = 100) -> Optional[str]:
        \"\"\"
        使用OpenAI API进行摘要（如果配置了API密钥）
        \"\"\"
        if not self.api_key:
            return self.summarize_text(text, max_length)
        
        try:
            headers = {
                \"Content-Type\": \"application/json\",
                \"Authorization\": f\"Bearer {self.api_key}\"
            }
            
            prompt = f\"请用一句话总结以下内容，不超过{max_length}个字符：\\n\\n{text[:1000]}\"
            
            data = {
                \"model\": \"gpt-3.5-turbo\",
                \"messages\": [
                    {\"role\": \"system\", \"content\": \"你是一个文本摘要助手，能够用一句话简洁地总结文本内容。\"},
                    {\"role\": \"user\", \"content\": prompt}
                ],
                \"max_tokens\": 100,
                \"temperature\": 0.3
            }
            
            response = requests.post(f\"{self.base_url}/chat/completions\", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            return summary
        except Exception as e:
            print(f\"Error calling OpenAI API: {str(e)}\")
            # 如果API调用失败，回退到本地方法
            return self.summarize_text(text, max_length)

# 全局实例
summarizer = TextSummarizer()