import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
    page_icon="🍳",
    layout="wide", # モバイルでも中央に寄せつつ広さを確保
    initial_sidebar_state="collapsed"
)

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = "作る"
if 'ingredients_list' not in st.session_state:
    st.session_state.ingredients_list = ""
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = ""
if 'saved_recipes' not in st.session_state:
     st.session_state.saved_recipes = []

# --- CSS設定（下部ナビゲーション対応） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body {
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
    }

    /* メインコンテンツエリアの余白（フッター分を空ける） */
    .main .block-container {
        padding-bottom: 100px !important;
        padding-top: 20px !important;
        max-width: 500px !important; /* スマホで見やすい幅に固定 */
    }

    /* 下部ナビゲーション固定バー */
    div[data-testid="stVerticalBlock"] > div:last-child {
        /* このセレクタはStreamlitの構造に依存するため、より確実な方法として
           以下の .fixed-footer を使用します */
    }

    /* フッター専用のボトムバー */
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #FFFFFF;
        border-top: 1px solid #EEEEEE;
        padding: 10px 0;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    
    /* ボタンの共通スタイル再定義（フッター用） */
    .footer-btn-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        max-width: 500px;
        margin: 0 auto;
    }

    /* ボタンカスタマイズ */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        background-color: transparent !important;
        color: #666666 !important;
        transition: 0.2s;
    }
    
    /* 選択中のボタン強調 */
    .active-btn button {
        color: #FF9900 !important;
        border-bottom: 2px solid #FF9900 !important;
        border-radius: 0 !important;
    }

    /* メインオレンジボタン */
    .primary-btn button {
        background-color: #FF9900 !important;
        color: white !important;
        height: 52px !important;
        font-size: 18px !important;
        box-shadow: 0 4px 0 #CC7A00 !important;
    }

    .recipe-card {
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #EEEEEE !important;
        margin-bottom: 20px !important;
        color: #000000 !important;
    }
    
    h1 {
        font-size: 22px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
        margin-bottom: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ページ切り替え関数 ---
def change_page(page_name):
    st.session_state.page = page_name

# ==========================================
# メインコンテンツ表示
# ==========================================

# 1. 生成画面
if st.session_state.page == "作る":
    st.markdown("<h1>レシピを作る</h1>", unsafe_allow_html=True)
    st.caption("食材を撮ってAIに献立をまかせましょう")

    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("ジャンル", ["一般的な料理", "離乳食(5-6ヶ月)", "離乳食(7-8ヶ月)", "離乳食(9-11ヶ月)", "離乳食(12-18ヶ月)"])
    with c2:
        num_dishes = st.radio("品数", (1, 2, 3), format_func=lambda x: f"{x}品", horizontal=True)

    uploaded_files = st.file_uploader("食材の写真を撮影または選択", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    
    images = []
    if uploaded_files:
        cols = st.columns(4)
        for i, f in enumerate(uploaded_files):
            img = Image.open(f)
            images.append(img)
            with cols[i % 4]: st.image(img, use_column_width=True)
        
        if st.button("① 食材をチェックする", use_container_width=True):
            with st.spinner("画像を解析中..."):
                stream = gemini_handler.identify_ingredients(images)
                st.session_state.ingredients_list = st.write_stream(stream)

    if st.session_state.ingredients_list:
        st.markdown("<br>### 2. 食材リスト（編集可）", unsafe_allow_html=True)
        edited = st.text_area("食材", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("🥕 ちょい足しモード（定番食材をプラス）", value=False)
        
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("② レシピを生成！", use_container_width=True):
            with st.status("Geminiシェフが考案中...", expanded=True) as status:
                placeholder = st.empty()
                stream = gemini_handler.generate_recipe(edited, mode, num_dishes, is_choi)
                with placeholder:
                    result = st.write_stream(stream)
                st.session_state.recipe_result = result
                st.session_state.ingredients_list = edited
                placeholder.empty()
                status.update(label="完成しました！", state="complete")
            change_page("確認")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 2. 確認画面
elif st.session_state.page == "確認":
    st.markdown("<h1>できたレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.recipe_result:
        st.info("「作る」画面からレシピを生成してください。")
    else:
        result_text = st.session_state.recipe_result
        pattern = re.compile(r'##\s*案([A-C|Ａ-Ｃ])[:：]')
        matches = list(pattern.finditer(result_text))
        
        if matches:
            intro = result_text[:matches[0].start()].strip()
            if intro: st.warning(intro)

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
        
            st.markdown("---")
            if st.button("⭐ このレシピをお気に入りに保存", use_container_width=True):
                new_entry = {
                    "date": datetime.datetime.now().strftime("%m/%d %H:%M"),
                    "label": f"レシピ ({datetime.datetime.now().strftime('%m/%d')})",
                    "content": result_text
                }
                st.session_state.saved_recipes.insert(0, new_entry)
                st.success("「保存」画面に追加しました")
        else:
            st.markdown(f"<div class='recipe-card'>{result_text}</div>", unsafe_allow_html=True)

# 3. 保存画面
elif st.session_state.page == "保存":
    st.markdown("<h1>保存済みレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.saved_recipes:
        st.info("保存されたレシピはありません。")
    else:
        for i, item in enumerate(st.session_state.saved_recipes):
            with st.expander(f"📅 {item['date']} - {item['label']}"):
                st.markdown(f"<div class='recipe-card'>{item['content']}</div>", unsafe_allow_html=True)
                if st.button(f"削除", key=f"del_{i}"):
                    st.session_state.saved_recipes.pop(i)
                    st.rerun()

# ==========================================
# 下部ナビゲーション（フッター）
# ==========================================

# 画面下部に配置するために空行を入れる（Streamlitの挙動上、最後に出力されたものが下にくるため）
# ただしCSS position: fixed を使うので、どこに書いてもOKですが、意味的に最後におきます。

st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
fcol1, fcol2, fcol3 = st.columns(3)

with fcol1:
    st.markdown(f'<div class="{"active-btn" if st.session_state.page == "作る" else ""}">', unsafe_allow_html=True)
    if st.button("🧑‍🍳 作る", key="nav_create", use_container_width=True):
        change_page("作る")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with fcol2:
    st.markdown(f'<div class="{"active-btn" if st.session_state.page == "確認" else ""}">', unsafe_allow_html=True)
    if st.button("📖 確認", key="nav_view", use_container_width=True):
        change_page("確認")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with fcol3:
    st.markdown(f'<div class="{"active-btn" if st.session_state.page == "保存" else ""}">', unsafe_allow_html=True)
    if st.button("⭐ 保存", key="nav_save", use_container_width=True):
        change_page("保存")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
