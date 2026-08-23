"""
VoiceStudio Client Examples
أمثلة على استخدام العميل
"""

import requests
import soundfile as sf
import asyncio
import websockets
import json
from pathlib import Path


class VoiceStudioClient:
    """عميل VoiceStudio - VoiceStudio Client"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http", "ws")

    def transcribe_file(self, audio_path: str, language: str = "ar") -> dict:
        """
        تحويل ملف صوتي إلى نص
        Convert audio file to text
        """
        with open(audio_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.server_url}/transcribe",
                files=files,
                params={"language": language}
            )
        return response.json()

    def text_to_speech(self, text: str, language: str = "ar", output_path: str = "output.wav"):
        """
        تحويل النص إلى صوت
        Convert text to speech
        """
        response = requests.post(
            f"{self.server_url}/synthesize",
            params={"text": text, "language": language}
        )

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Audio saved to {output_path}")
        return output_path

    def full_conversation(self, audio_path: str, language: str = "ar") -> dict:
        """
        محادثة كاملة
        Full conversation flow
        """
        with open(audio_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.server_url}/conversation",
                files=files,
                params={"language": language}
            )
        return response.json()

    def get_supported_languages(self) -> dict:
        """الحصول على اللغات المدعومة - Get supported languages"""
        response = requests.get(f"{self.server_url}/languages")
        return response.json()

    async def websocket_conversation(self, audio_data):
        """
        محادثة عبر WebSocket (فورية)
        Real-time WebSocket conversation
        """
        uri = f"{self.ws_url}/ws/conversation"
        async with websockets.connect(uri) as websocket:
            # إرسال الصوت
            await websocket.send(audio_data.tobytes())

            # استقبال النتيجة
            response = await websocket.recv()
            print("Bot response:", json.loads(response))

            # استقبال الصوت
            audio_response = await websocket.recv()
            return audio_response


# أمثلة على الاستخدام - Usage Examples

def example_1_transcribe():
    """مثال 1: تحويل صوت إلى نص"""
    print("📝 Example 1: Transcribe Audio")
    client = VoiceStudioClient()

    # تأكد من وجود ملف صوتي
    if Path("test_audio.wav").exists():
        result = client.transcribe_file("test_audio.wav", language="ar")
        print(f"Text: {result['text']}")
        print(f"Confidence: {result['confidence']:.2%}")
    else:
        print("⚠️ No test_audio.wav found")


def example_2_tts():
    """مثال 2: تحويل نص إلى صوت"""
    print("\n🔊 Example 2: Text-to-Speech")
    client = VoiceStudioClient()

    texts = [
        "السلام عليكم ورحمة الله وبركاته",
        "مرحبا بك في VoiceStudio",
        "أنا مساعدك الصوتي الذكي",
    ]

    for i, text in enumerate(texts, 1):
        output = client.text_to_speech(text, language="ar", output_path=f"output_{i}.wav")
        print(f"✅ Generated: {output}")


def example_3_conversation():
    """مثال 3: محادثة كاملة"""
    print("\n💬 Example 3: Full Conversation")
    client = VoiceStudioClient()

    if Path("test_audio.wav").exists():
        result = client.full_conversation("test_audio.wav", language="ar")
        print(f"User said: {result['user_input']}")
        print(f"Intent: {result['intent']}")
        print(f"Bot response: {result['bot_response']}")
    else:
        print("⚠️ No test_audio.wav found")


def example_4_languages():
    """مثال 4: الحصول على اللغات المدعومة"""
    print("\n🌍 Example 4: Supported Languages")
    client = VoiceStudioClient()
    languages = client.get_supported_languages()
    for lang in languages["supported"]:
        print(f"  • {lang['name']} ({lang['code']})")


def example_5_batch_tts():
    """مثال 5: تحويل عدة نصوص"""
    print("\n📚 Example 5: Batch Processing")
    client = VoiceStudioClient()

    texts_ar = [
        "كيف حالك اليوم؟",
        "الطقس جميل جداً",
        "شكراً لك على مساعدتك"
    ]

    for i, text in enumerate(texts_ar, 1):
        try:
            client.text_to_speech(text, language="ar", output_path=f"batch_{i}.wav")
            print(f"✅ Batch {i}: {text}")
        except Exception as e:
            print(f"❌ Batch {i} failed: {e}")


async def example_6_websocket():
    """مثال 6: WebSocket المحادثة الفورية"""
    print("\n⚡ Example 6: WebSocket Real-time")
    client = VoiceStudioClient()

    # تجهيز بيانات صوتية (مثال)
    if Path("test_audio.wav").exists():
        audio_data, sr = sf.read("test_audio.wav")
        result = await client.websocket_conversation(audio_data)
        print("✅ Real-time response received")
    else:
        print("⚠️ No test_audio.wav found")


def main():
    """تشغيل الأمثلة - Run examples"""
    print("🎤 VoiceStudio Client Examples\n")
    print("=" * 50)

    # تأكد من أن الخادم يعمل
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ Server is not running on http://localhost:8000")
            return
    except:
        print("❌ Cannot connect to server. Make sure it's running:")
        print("   python api_server.py")
        return

    # تشغيل الأمثلة
    example_1_transcribe()
    example_2_tts()
    example_3_conversation()
    example_4_languages()
    example_5_batch_tts()

    # WebSocket example (async)
    # asyncio.run(example_6_websocket())

    print("\n" + "=" * 50)
    print("✅ All examples completed!")


if __name__ == "__main__":
    main()
