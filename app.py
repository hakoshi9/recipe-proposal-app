import streamlit as st
from PIL import Image
import gemini_handler

st.set_page_config(
    page_title="食材画像deレシピ提案 AI",
    page_icon="🍳",
    layout="wide"
)

# Sidebar configuration
st.sidebar.title("設定 & モード")
mode = st.sidebar.radio(
    "レシピの種類を選んでください",
    (
        "一般的な料理",
        "離乳食(5-6ヶ月)",
        "離乳食(7-8ヶ月)",
        "離乳食(9-11ヶ月)",
        "離乳食(12-18ヶ月)"
    )
)

st.title("🍳 食材画像からレシピ・離乳食提案ツール")
st.markdown("""
冷蔵庫にある食材の写真をアップロードするだけで、AIがレシピを提案します！
忙しい日の献立や、離乳食のメニューにお悩みの方にぴったりです。
""")

uploaded_file = st.file_uploader("食材の写真をアップロードしてください", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='アップロードされた画像', use_column_width=True)

    if st.button("レシピを生成する", type="primary"):
        with st.spinner('Geminiシェフがレシピを考案中...🍳'):
            try:
                # Call Gemini API
                recipe_text = gemini_handler.get_recipe_from_image(image, mode)
                
                st.success("レシピが生成されました！")
                st.markdown("---")
                st.markdown(recipe_text)
                
                # Monetization/Affiliate Placeholder
                st.markdown("---")
                st.subheader("おすすめキッチンアイテム")
                st.info("💡 ここにハンドブレンダーや便利な調理器具、食材宅配サービスの広告リンクが表示されます（収益化プレースホルダー）。")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

else:
    st.info("画像をアップロードして、「レシピを生成する」ボタンを押してください。")

st.markdown("---")
st.caption("Powered by Google Gemini 1.5 Flash | Built with Streamlit")
