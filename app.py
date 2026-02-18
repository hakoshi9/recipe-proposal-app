import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = "生成"
if 'ingredients_list' not in st.session_state:
    st.session_state.ingredients_list = ""
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = ""
if 'saved_recipes' not in st.session_state:
     st.session_state.saved_recipes = [] # お気に入り保存用

# --- CSS設定（モバイルファースト & 高コントラスト） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif !important;
        color: #000000 !important;
    }

    .stApp {
        background-color: #FFFFFF !important;
    }

    /* ナビゲーションバー風 */
    .nav-container {
        display: flex;
        justify-content: space-around;
        background-color: #F8F8F8;
        padding: 10px 0;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 1px solid #EEEEEE;
    }
    
    /* ボタンの共通スタイル */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    
    /* メインオレンジボタン */
    .primary-btn button {
        background-color: #FF9900 !important;
        color: white !important;
        height: 52px !important;
        font-size: 18px !important;
    }

    /* 保存済みレシピカード */
    .recipe-card {
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #EEEEEE !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    
    /* 特大見出し */
    h1 {
        font-size: 24px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 共通ユーティリティ ---
def change_page(page_name):
    st.session_state.page = page_name

# --- ナビゲーション ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🍳 作る", use_container_width=True): change_page("生成")
with col2:
    if st.button("📖 確認", use_container_width=True): change_page("確認")
with col3:
    if st.button("⭐ 保存", use_container_width=True): change_page("保存")

st.markdown("---")

# ==========================================
# 1. レシピ生成画面
# ==========================================
if st.session_state.page == "生成":
    st.markdown("<h1>レシピを作る</h1>", unsafe_allow_html=True)
    st.caption("食材を撮って、AIに献立をまかせましょう")

    # 設定
    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("ジャンル", ["一般的な料理", "離乳食(5-6ヶ月)", "離乳食(7-8ヶ月)", "離乳食(9-11ヶ月)", "離乳食(12-18ヶ月)"])
    with c2:
        num_dishes = st.radio("品数", (1, 2, 3), format_func=lambda x: f"{x}品", horizontal=True)

    # アップロード
    uploaded_files = st.file_uploader("食材の写真を撮影または選択", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    
    images = []
    if uploaded_files:
        cols = st.columns(4)
        for i, f in enumerate(uploaded_files):
            img = Image.open(f)
            images.append(img)
            with cols[i % 4]: st.image(img, use_column_width=True)
        
        if st.button("食材をチェックする", use_container_width=True):
            with st.spinner("食材を解析中..."):
                stream = gemini_handler.identify_ingredients(images)
                st.session_state.ingredients_list = st.write_stream(stream)

    if st.session_state.ingredients_list:
        st.markdown("### 2. 食材リスト（編集可）")
        edited = st.text_area("食材", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("🥕 ちょい足しモード（卵や野菜をプラス）", value=False)
        
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("この食材でレシピを生成！", use_container_width=True):
            with st.status("Geminiシェフが考案中...") as status:
                placeholder = st.empty()
                stream = gemini_handler.generate_recipe(edited, mode, num_dishes, is_choi)
                with placeholder:
                    result = st.write_stream(stream)
                st.session_state.recipe_result = result
                st.session_state.ingredients_list = edited
                placeholder.empty()
                status.update(label="完成しました！", state="complete")
            # 生成後、自動的に確認画面へ
            change_page("確認")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. 確認画面
# ==========================================
elif st.session_state.page == "確認":
    st.markdown("<h1>最新のレシピ案</h1>", unsafe_allow_html=True)
    
    if not st.session_state.recipe_result:
        st.info("まだレシピが生成されていません。「作る」画面から食材を撮ってください。")
    else:
        result_text = st.session_state.recipe_result
        
        # 警告文の抽出
        pattern = re.compile(r'##\s*案([A-C|Ａ-Ｃ])[:：]')
        matches = list(pattern.finditer(result_text))
        
        if matches:
            intro = result_text[:matches[0].start()].strip()
            if intro: st.warning(intro)

            # タブ表示
            tab_labels = []
            for m in matches:
                header = result_text[m.start():].split('\n')[0].replace('#', '').strip()
                tab_labels.append(header.replace("案", ""))
            
            tabs = st.tabs(tab_labels)
            for i, tab in enumerate(tabs):
                start = matches[i].start()
                end = matches[i+1].start() if i+1 < len(matches) else len(result_text)
                content = result_text[start:end]
                with tab:
                    st.markdown(f"<div class='recipe-card'>{content}</div>", unsafe_allow_html=True)
        
            # 保存ボタン
            st.markdown("---")
            if st.button("⭐ このレシピ案をまるごと保存する", use_container_width=True):
                new_entry = {
                    "date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
                    "content": result_text
                }
                st.session_state.saved_recipes.insert(0, new_entry)
                st.success("履歴に保存しました！")
        else:
            st.markdown(f"<div class='recipe-card'>{result_text}</div>", unsafe_allow_html=True)

# ==========================================
# 3. 保存画面（履歴）
# ==========================================
elif st.session_state.page == "保存":
    st.markdown("<h1>保存済みレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.saved_recipes:
        st.info("保存されたレシピはありません。")
    else:
        for i, item in enumerate(st.session_state.saved_recipes):
            with st.expander(f"📅 {item['date']} のレシピ"):
                st.markdown(f"<div class='recipe-card'>{item['content']}</div>", unsafe_allow_html=True)
                if st.button(f"削除", key=f"del_{i}"):
                    st.session_state.saved_recipes.pop(i)
                    st.rerun()

# --- フッター（デバッグ用・本番は不要） ---
# st.write(f"現在のページ: {st.session_state.page}")
