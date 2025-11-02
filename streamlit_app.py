import streamlit as st
import requests
import pandas as pd
import time

# Show title and description.
#st.title("📄 Document question answering (Gemini API版)")
st.title("📄簡易配合変化確認システム")
#st.write(
#    "Upload a document below and ask a question about it – Gemini API will answer! "
#    "To use this app, you need to provide a Google Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey). "
#)

# モデル選択
model_options = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro"
}
selected_model_label = st.selectbox("Gemini model を選んでください", list(model_options.keys()), index=0)
selected_model = model_options[selected_model_label]

# Google Gemini API Key入力
#gemini_api_key = st.text_input("Google Gemini API Key", type="password")
gemini_api_key = st.secrets['251102']['gemini_api_key']
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # ファイルアップロード
    #uploaded_file = st.file_uploader(
    #    "Upload a document (.txt, .md, or .csv)", type=("txt", "md", "csv")
    #)

    uploaded_file = st.file_uploader(
        "配合変化データベースのcsvファイル（UTF8）を選んでください", type=("csv")
    )

    # 質問入力
    question = st.text_area(
        "質問内容を書き込んでください",
        placeholder="ここに質問内容を書く",
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

        # Gemini APIエンドポイント（選択したモデルを使用）
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        params = {
            "key": gemini_api_key
        }

        # 進行状況バーの表示
        progress_text = "Gemini APIで回答を生成中です..."
        progress_bar = st.progress(0, text=progress_text)
        for percent_complete in range(1, 51):
            time.sleep(0.01)
            progress_bar.progress(percent_complete * 2, text=progress_text)
        
        # APIリクエスト
        response = requests.post(endpoint, headers=headers, params=params, json=payload)
        progress_bar.progress(100, text="回答が生成されました！")
        time.sleep(0.5)
        progress_bar.empty()

        if response.status_code == 200:
            try:
                answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.write(answer)
            except Exception as e:
                st.error(f"Unexpected response format: {response.json()}")
        else:
            st.error(f"API request failed: {response.status_code} {response.text}")
