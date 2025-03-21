import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from diary.models import Diary
from member.models import MemberInfo

User = get_user_model()


class DiaryAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        if not settings.configured:
            settings.configure()


class DiaryTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.email = "test@email.com"
        self.password = "password123"
        self.nickname = "testnickname"

        self.user = User.objects.create_user(
            email=self.email,
            provider="test_provider",
            provider_user_id="test_id",
            password=self.password
        )
        MemberInfo.objects.create(
            social_account=self.user,
            nickname=self.nickname
        )

        self.client.force_authenticate(user=self.user)

        # 기존 데이터 삭제
        Diary.objects.filter(member=self.user).delete()

        self.diary = Diary.objects.create(
            member=self.user,
            diary_title="오늘의 일기 test",
            content="오늘은 날씨가 무척 좋다. 밖에 나가 신나는 노래를 들으며 자전거르 타고싶다."
            "봄이오니까 뻐근했던 몸도 슬슬 풀리는 기분이다. 기분 좋은 팝송 들으며 나들이 가고싶어진다.",
            moods=["기쁨", "설렘"],
        )

        self.diary_url = f"/api/diary/{self.diary.diary_id}/"

        self.today = datetime.date.today().strftime("%Y-%m-%d")
        self.past_date_0 = (
            datetime.date.today() - datetime.timedelta(days=4)
        ).strftime("%Y-%m-%d")
        self.past_date = (
            datetime.date.today() - datetime.timedelta(days=5)
        ).strftime("%Y-%m-%d")
        self.future_date = (
            datetime.date.today() + datetime.timedelta(days=3)
        ).strftime("%Y-%m-%d")

    def test_create_diary(self):
        payload = {
            "diary_title": "새로운 일기 테스트",
            "content": "테스트가 잘 안되서 너무속상한 상태이다. 어려움을 겪고있어서 너무 힘들고 지친다. 왜이걸 해야하는건가으아아아악 머리가 너무아파 요 우우아가가가",
            "moods": ["분노", "좌절"],
            "created_at": self.past_date_0,
        }
        response = self.client.post(
            "/api/diary/create/", data=payload, format="json"
        )
        print("서버응답 :", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("diary_id", response.data["data"])
        self.assertEqual(
            response.data["data"]["diary_title"], payload["diary_title"]
        )
        self.assertEqual(response.data["data"]["content"], payload["content"])
        print("🥳 일기 생성 테스트 통과")

    # 오늘이 아닌 날짜 (과거)에 작성 테스트
    def test_create_diary_past(self):
        payload = {
            "diary_title": "빈 과거 날짜의 일기",
            "content": "과거의 날짜중 일기를 쓰지 않은 날 작성이 가능해야 한다! 제발 되쓰면 ㅎㅎ",
            "moods": ["초조", "희망"],
            "created_at": self.past_date,
        }
        print(
            f"🚀 테스트: 과거 일기 작성 요청 payload: {payload}"
        )  # 추가된 디버깅 로그

        response = self.client.post(
            "/api/diary/create/", data=payload, format="json"
        )

        print(f"🚀 서버 응답: {response.data}")  # 응답 확인

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("diary_id", response.data["data"])
        print("🥳 과거 날짜 일기 생성 테스트 통과")

    # 미래 날짜 일기 작성 실패 테스트
    def test_create_diary_future(self):
        payload = {
            "diary_title": "오늘 이후의 일기",
            "content": "오늘 이후 즉, 미래의 일기는 써지면 안된다. 안될 거 같아서 매우 초조하다 엄청 피곤함..",
            "moods": ["불안", "피곤"],
            "created_at": self.future_date,
        }
        response = self.client.post(
            "/api/diary/create/", data=payload, format="json"
        )
        print("🔹 서버 응답:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "invalid_request")
        print("🥳 미래 날짜 일기 작성 방지 테스트 통과")

    #  중복 일기 실패 테스트
    def test_create_duplicate_diary(self):
        payload = {
            "diary_title": "오늘 일기 또쓰지롱",
            "content": "오늘 날짜로 일기 또쓰는데 과연 될런지 .. 기대가 됩니다.",
            "moods": ["불안", "피곤"],
            "created_at": self.today,
        }

        self.client.post("/api/diary/create/", data=payload, format="json")
        response = self.client.post(
            "/api/diary/create/", data=payload, format="json"
        )
        print("🔹 서버 응답:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "invalid_request")
        print("🥳 중복된 날짜의 일기 생성 방지 테스트 통과")

    def test_get_diary_detail(self):
        diary_id = str(self.diary.diary_id)
        response = self.client.get(self.diary_url)

        print("🔹 요청한 일기 ID:", diary_id)  # 디버깅용
        print("🔹 서버 응답:", response.data)  # 응답 확인

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["diary_id"], diary_id)
        print("🥳 일기 조회 테스트 통과")

    def test_get_diary_list(self):

        Diary.objects.create(
            member=self.user,
            diary_title="추가 일기1",
            content="내용1" * 10,
            moods=["기쁨"],
            created_at=datetime.date.today() - datetime.timedelta(days=1),
        )
        Diary.objects.create(
            member=self.user,
            diary_title="추가 일기2",
            content="내용2" * 10,
            moods=["슬픔"],
            created_at=datetime.date.today() - datetime.timedelta(days=2),
        )

        url = reverse('diary:diary-main')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "일기 날짜 데이터 불러오기 성공.")
        self.assertEqual(len(response.data['data']),3)
        print("🥳 일기 목록 조회 테스트 통과")

    def test_search_diary(self):
        """일기 검색 테스트"""
        payload = {"q": "test"}
        response = self.client.post(
            "/api/diary/search/", data=payload, format="json"
        )

        # 디버깅용
        print("🔹 서버 응답 상태 코드:", response.status_code)
        print("🔹 서버 응답 데이터:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)
        print("🥳 일기 검색 테스트 통과!")

    def test_delete_diary(self):
        diary_exists = Diary.objects.filter(
            diary_id=self.diary.diary_id
        ).exists()

        print(f"✅ 삭제 전 일기 존재 여부: {diary_exists}")

        response = self.client.delete(self.diary_url)

        print(f"🔹 삭제 요청 응답 코드: {response.status_code}")
        print(f"🔹 삭제 요청 응답 데이터: {response.data}")

        # ✅ 삭제 후 다시 체크
        diary_exists_after = Diary.objects.filter(
            diary_id=self.diary.diary_id
        ).exists()
        print(f"✅ 삭제 후 일기 존재 여부: {diary_exists_after}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(diary_exists_after, "일기가 삭제되지 않았습니다.")

        print("🥳 일기 삭제 테스트 통과")
