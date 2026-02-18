import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it.")

genai.configure(api_key=GOOGLE_API_KEY)

def get_recipe_from_image(image, mode):
    """
    Generates a recipe based on the provided image and mode using Gemini 1.5 Flash.

    Args:
        image: PIL Image object.
        mode: String indicating the selected mode (e.g., "一般的な料理", "離乳食(5-6ヶ月)").

    Returns:
        String containing the generated recipe response.
    """
    
    # Model configuration
    model = genai.GenerativeModel('gemini-flash-latest')

    # Constructing the prompt based on the mode
    base_prompt = """
    あなたはプロの料理研究家兼管理栄養士です。
    アップロードされた画像を分析し、そこに写っている食材を特定してください。
    その食材を使った、美味しくて作りやすいレシピを1つ提案してください。
    
    出力フォーマット:
    ## 料理名: [ここに料理名]
    
    ### 材料
    - [食材1]: [分量]
    - [食材2]: [分量]
    ...
    
    ### 手順
    1. [手順1]
    2. [手順2]
    ...
    
    ### ポイント
    [美味しく作るコツや代用食材など]
    """

    if "離乳食" in mode:
        baby_food_stage = mode.replace("離乳食", "").strip("()")
        prompt = f"""
        {base_prompt}
        
        【重要】
        今回は「{baby_food_stage}」向けの離乳食レシピを提案してください。
        
        以下の点に厳重に注意してください:
        1. 食材の大きさ、固さは{baby_food_stage}の赤ちゃんが安全に食べられるものにしてください。
        2. 味付けは月齢に合わせてごく薄味、または素材の味のみにしてください。
        3. アレルギー特定原材料が含まれる場合は注意書きをしてください。
        4. はちみつ、黒糖、刺身などの乳児ボツリヌス症や食中毒のリスクがある食材は絶対に使用しないでください。
        5. 必ず冒頭に以下の警告文を表示してください。
        「⚠️ アレルギーや窒息に注意し、初めての食材は少量から試してください。」
        """
    else:
        # General cooking mode
        prompt = f"""
        {base_prompt}
        
        ターゲット: 忙しい人、家にある食材を使い切りたい人
        手軽に作れる家庭料理を提案してください。
        """

    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"
