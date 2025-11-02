import streamlit as st
import requests
import pandas as pd

# Show title and description.
st.title("📄 Document question answering (Gemini API版)")
st.write(
    "Upload a document below and ask a question about it – Gemini API will answer! "
    "To use this app, you need to provide a Google Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey). "
)

# Google Gemini API Key入力
gemini_api_key = st.text_input("Google Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "Upload a document (.txt, .md, or .csv)", type=("txt", "md", "csv")
    )

    # 質問入力
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # ファイル形式判定
        file_type = uploaded_file.name.split('.')[-1]

        # ドキュメント内容取得
        if file_type == "csv":
            # CSVファイルはデータフレームで読み込んで、テキスト化
            df = pd.read_csv(uploaded_file)
            document = df.to_csv(index=False)
        else:
            document = uploaded_file.read().decode()

        # Geminiプロンプト生成
        prompt = f"Here's a document:\n{document}\n\n---\n\nQuestion: {question}\nAnswer:"

        # Gemini APIエンドポイント
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        params = {
            "key": gemini_api_key
        }

        # APIリクエスト
        response = requests.post(endpoint, headers=headers, params=params, json=payload)
        if response.status_code == 200:
            try:
                answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.write(answer)
            except Exception as e:
                st.error(f"Unexpected response format: {response.json()}")
        else:
            st.error(f"API request failed: {response.status_code} {response.text}")
