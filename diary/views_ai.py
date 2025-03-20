import google.generativeai as genai

from config import settings

# Google API 키 설정 (본인의 키로 변경 필요)
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)


def get_emotions(content):
    # 감정 분석할 일기
    diary = content

    # 프롬프트 작성
    prompt = f"""
    다음은 사용자가 작성한 일기입니다.
    
    [일기]
    {diary}
    
    위 일기의 감정을 정확히 네가지 고르고, 감정 외에는 절대 출력하지 마세요.  
    다음 감정 목록에서 선택하세요:
    반드시 목록에 있는 감정만 선택하세요.  
    감정만 출력하고, 다른 문장은 절대로 출력하지 마세요.  
    감정은 아래 형식으로 출력하세요.
    
    [감정 목록]
        "기쁨", "슬픔", "분노", "불안", "사랑", "두려움", "외로움", "설렘", "짜증", "행복",
        "후회", "자신감", "좌절", "공포", "흥분", "우울", "희망", "질투", "원망", "감동",
        "미움", "초조", "만족", "실망", "그리움", "죄책감", "억울함", "충격", "안도", "분개",
        "긴장", "환희", "낙담", "피곤", "민망함", "자책", "포기", "열정", "홀가분함", "수치심",
        "신뢰", "짜릿함", "감사", "동정", "황당함", "의심", "희열", "짜증남", "편안함", "짜릿한 기대"
    
    출력 예시:
    기쁨, 상쾌함
    """

    # 모델 불러오기
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 감정 분석 요청
    response = model.generate_content(prompt)

    # 출력 결과 정리
    generated_text = response.text.strip()

    return generated_text
