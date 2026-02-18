import streamlit as st
from PIL import Image
import gemini_handler
import re

# --- ページ設定とカスタムCSS ---
st.set_page_config(
    page_title="レシピ提案",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 高コントラスト・全要素視認性確保CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
    
    html, body {
        font-family: 'Noto Sans JP', sans-serif !important;
    }

    .stApp {
        background-color: #FFFFFF !important;
    }
    
    .stMarkdown p, .stMarkdown span:not([data-testid="stIconMaterial"]), 
    label, p, li, .stCaption, div[data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    h1 {
        font-size: 26px !important;
        color: #FF9900 !important;
        font-weight: 900 !important;
        border-bottom: 4px solid #FF9900 !important;
        padding-bottom: 10px !important;
        margin-bottom: 25px !important;
    }
    
    h2, h3, h4 {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stSelectbox"] label p, 
    div[data-baseweb="select"] > div {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    div[data-baseweb="popover"] ul {
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] li {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }

    div.stButton > button:first-child {
        width: 100%;
        height: 52px;
        background-color: #FF9900 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 4px 0 #CC7A00 !important;
    }

    section[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #FF9900 !important;
        background-color: #FAFAFA !important;
    }
    section[data-testid="stFileUploadDropzone"] p {
        color: #000000 !important;
    }

    .recipe-card {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 12px !important;
        border: 2px solid #DDDDDD !important;
        color: #000000 !important;
        line-height: 1.7 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    .recipe-card b, .recipe-card strong {
        color: #FF9900 !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #444444 !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FF9900 !important;
        border-bottom: 4px solid #FF9900 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- セッション状態 ---
if 'ingredients_list' not in st.session_state:
    st.session_state.ingredients_list = ""
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = ""

# --- ヘッダー ---
st.markdown("<h1>レシピ提案AI</h1>", unsafe_allow_html=True)
st.caption("冷蔵庫の食材を撮るだけで、今日の献立をご提案します")

# --- 設定セクション ---
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    mode = st.selectbox(
        "料理ジャンル",
        ["一般的な料理", "離乳食(5-6ヶ月)", "離乳食(7-8ヶ月)", "離乳食(9-11ヶ月)", "離乳食(12-18ヶ月)"]
    )
with c2:
    num_dishes = st.radio(
        "品数",
        (1, 2, 3),
        format_func=lambda x: f"{x}品",
        horizontal=True
    )

# --- 写真アップロード ---
uploaded_files = st.file_uploader(
    "食材の写真を撮影または選択してください", 
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

images = []
if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 4))
    for i, uploaded_file in enumerate(uploaded_files):
        image = Image.open(uploaded_file)
        images.append(image)
        with cols[i % 4]:
            st.image(image, use_column_width=True)
    
    if st.button("① 食材をチェックする"):
         with st.spinner('AIが食材を読み取っています...'):
            try:
                stream = gemini_handler.identify_ingredients(images)
                st.session_state.ingredients_list = st.write_stream(stream)
                st.session_state.recipe_result = ""
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 食材リスト・生成 ---
if st.session_state.ingredients_list:
    st.markdown("---")
    st.markdown("### 2. 食材リスト（編集可）")
    
    edited_ingredients = st.text_area(
        "認識された食材",
        value=st.session_state.ingredients_list,
        height=120
    )
    
    is_choi_tashi = st.checkbox("🥕 ちょい足しモード（卵や定番食材を足して提案）", value=False)
    
    if st.button("② この食材でレシピを作る"):
        st.session_state.recipe_result = ""
        st.session_state.ingredients_list = edited_ingredients
        
        # 進行状況表示用コンテナ
        status_box = st.empty()
        with status_box.status("レシピを考案中...", expanded=True) as status:
            stream_placeholder = st.empty()
            try:
                stream = gemini_handler.generate_recipe(
                    edited_ingredients, mode, num_dishes, is_choi_tashi
                )
                with stream_placeholder:
                    full_response = st.write_stream(stream)
                
                # 生成完了！一時的な表示を消去
                stream_placeholder.empty()
                st.session_state.recipe_result = full_response
                # 「完成しました」コンテナ自体を少し待ってから消去（一瞬だけ見せる）
                status.update(label="完成しました", state="complete")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        status_box.empty() # 完成後、ステータスアコーディオンを完全に消去

# --- レシピ結果表示エリア ---
if st.session_state.recipe_result:
    st.markdown("---")
    
    result_text = st.session_state.recipe_result
    
    # 正規表現で「案A」以降を分割
    pattern = re.compile(r'##\s*案([A-C|Ａ-Ｃ])[:：]')
    matches = list(pattern.finditer(result_text))
    
    # 案Aの前にテキスト（警告文など）があるかチェック
    if matches:
        intro_text = result_text[:matches[0].start()].strip()
        # 注意書きがあれば、レシピ全体の前に表示
        if intro_text:
            if "⚠️" in intro_text or "注意" in intro_text or "アレルギー" in intro_text:
                st.warning(intro_text)
            else:
                st.info(intro_text)

        # レシピ案をタブ表示
        tab_labels = []
        for m in matches:
            label_match = re.search(r'##\s*(.*?案[A-C|Ａ-Ｃ][:：].*)', result_text[m.start():])
            if label_match:
                full_label = label_match.group(1).split('\n')[0].replace('#', '').strip()
                # ラベルを短縮（案A: 〇〇）
                tab_labels.append(full_label.replace("案", ""))
            else:
                tab_labels.append(f"案{len(tab_labels)+1}")
        
        tabs = st.tabs(tab_labels)
        for i, tab in enumerate(tabs):
            start_idx = matches[i].start()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(result_text)
            content = result_text[start_idx:end_idx]
            with tab:
                st.markdown(f"<div class='recipe-card'>{content}</div>", unsafe_allow_html=True)
    else:
         # 分割できない場合はそのまま表示
         st.markdown(f"<div class='recipe-card'>{result_text}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🛒 買い出しリスト")
    c1, c2 = st.columns(2)
    with c1:
        st.info("🥦 食材宅配サービス")
    with c2:
        st.info("🔪 おすすめ調理器具")
