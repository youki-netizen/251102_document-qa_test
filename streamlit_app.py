import streamlit as st
import requests
import pandas as pd
import time

# Show title and description.
st.title("📄簡易配合変化確認システム")

# モデル選択
model_options = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro"
}
selected_model_label = st.selectbox("Gemini model を選んでください", list(model_options.keys()), index=0)
selected_model = model_options[selected_model_label]

# Google Gemini API Key入力
gemini_api_key = st.secrets['251102']['gemini_api_key']
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    uploaded_file = st.file_uploader(
        "配合変化データベースのcsvファイル（UTF8）を選んでください", type=("csv")
    )

    question = st.text_area(
        "質問内容を書き込んでください",
        placeholder="ここに質問内容を書く",
        disabled=not uploaded_file,
    )

    # --- ログ保存用: 初期化 ---
    if "qa_log" not in st.session_state:
        st.session_state.qa_log = []

    # --- 実行ボタン ---
    if st.button("質問する", disabled=not (uploaded_file and question)):
        file_type = uploaded_file.name.split('.')[-1]

        if file_type == "csv":
            df = pd.read_csv(uploaded_file)
            document = df.to_csv(index=False)
        else:
            document = uploaded_file.read().decode()

        prompt = f"Here's a document:\n{document}\n\n---\n\nQuestion: {question}\nAnswer:"

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": gemini_api_key}

        progress_text = "Gemini APIで回答を生成中です..."
        progress_bar = st.progress(0, text=progress_text)
        for percent_complete in range(1, 51):
            time.sleep(0.01)
            progress_bar.progress(percent_complete * 2, text=progress_text)
        
        response = requests.post(endpoint, headers=headers, params=params, json=payload)
        progress_bar.progress(100, text="回答が生成されました！")
        time.sleep(0.5)
        progress_bar.empty()

        if response.status_code == 200:
            try:
                answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.write(answer)
                # ログ追加（最大3件保持）
                st.session_state.qa_log.append({"question": question, "answer": answer})
                if len(st.session_state.qa_log) > 3:
                    st.session_state.qa_log = st.session_state.qa_log[-3:]
            except Exception as e:
                st.error(f"Unexpected response format: {response.json()}")
        else:
            st.error(f"API request failed: {response.status_code} {response.text}")

    # --- ログ表示 ---
    if st.session_state.qa_log:
        st.markdown("### 質問履歴（最大3件）")
        for idx, log in enumerate(reversed(st.session_state.qa_log), 1):
            st.markdown(f"**{idx}. 質問:** {log['question']}")
            st.markdown(f"**答え:** {log['answer']}")
            st.markdown("---")
