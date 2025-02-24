# X_5

数字X5

digital_broadcaster_project/
│
├── api/
│   ├── deep_seek_api.py          # 用于调用 Deep Seek API 生成商品文案
│
├── voice_synthesis/
│   ├── voice_model.py            # 语音合成模型，加载训练好的语音数据并合成声音
│   ├── synthesizer.py            # 用于将文案转化为声音的合成逻辑
│
├── avatar/
│   ├── avatar_creation.py        # 数字主播形象创建模块，利用3D建模工具生成数字形象
│   ├── avatar_renderer.py        # 渲染数字形象并同步嘴型与声音
│
├── assets/
│   ├── models/                  # 存放数字形象的3D模型
│   ├── sounds/                  # 存放音频文件（合成的语音）
│   ├── textures/                # 存放3D模型的纹理和材质文件
│
├── config/
│   ├── settings.py              # 存放项目配置，如Deep Seek API密钥等
│
├── main.py                      # 项目入口，整合文案生成、语音合成、数字主播展示
├── requirements.txt             # 项目依赖包列表
└── README.md                    # 项目的说明文档
