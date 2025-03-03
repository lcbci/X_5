import openai

# 设置 API 密钥
openai.api_key = 'okpEeej2VMQK8WRU43De430fA8F4425191CaFe0991Ef8575'

# 设置基础 URL
openai.base_url = "http://activity.scnet.cn:61080/v1/"

# 创建完成任务
completion = openai.chat.completions.create(
    model="DeepSeek-R1-Distill-Qwen-32B",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,  # 设置为流式输出
)

# 打印完成任务的结果
for chunk in completion:
    if len(chunk.choices) > 0:
        print(chunk.choices[0].delta.content)