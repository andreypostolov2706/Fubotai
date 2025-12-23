"""
Тестовый скрипт для проверки fal.ai API
"""
import asyncio
import os
import sys

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# API ключ
FAL_API_KEY = "666580cb-bf91-48ea-952b-9c31126cb76d:ca3d5943c73ec5f411ec0774dd638461"


async def test_text_to_image():
    """Тест генерации изображения (Text-to-Image)"""
    print("=" * 50)
    print("Тест: Text-to-Image (Nano Banana)")
    print("=" * 50)
    
    from api.fal_client import FalClient
    
    client = FalClient(FAL_API_KEY)
    
    result = await client.generate_image(
        endpoint="fal-ai/nano-banana",
        prompt="A cute cat astronaut floating in space, digital art style",
        aspect_ratio="1:1",
        output_format="png",
    )
    
    if result.success:
        print(f"✅ Успех!")
        print(f"   URL: {result.image_url}")
        print(f"   Время: {result.generation_time:.2f} сек")
        print(f"   Request ID: {result.request_id}")
    else:
        print(f"❌ Ошибка: {result.error}")
    
    return result


async def test_text_to_image_pro():
    """Тест генерации изображения Pro версии"""
    print("\n" + "=" * 50)
    print("Тест: Text-to-Image (Nano Banana Pro)")
    print("=" * 50)
    
    from api.fal_client import FalClient
    
    client = FalClient(FAL_API_KEY)
    
    result = await client.generate_image(
        endpoint="fal-ai/nano-banana-pro",
        prompt="A majestic mountain landscape at sunset, photorealistic, 4K quality",
        aspect_ratio="16:9",
        output_format="png",
        resolution="1K",
    )
    
    if result.success:
        print(f"✅ Успех!")
        print(f"   URL: {result.image_url}")
        print(f"   Время: {result.generation_time:.2f} сек")
        print(f"   Request ID: {result.request_id}")
    else:
        print(f"❌ Ошибка: {result.error}")
    
    return result


async def test_with_negative_prompt():
    """Тест с негативным промптом"""
    print("\n" + "=" * 50)
    print("Тест: С негативным промптом")
    print("=" * 50)
    
    from api.fal_client import FalClient
    
    client = FalClient(FAL_API_KEY)
    
    result = await client.generate_image(
        endpoint="fal-ai/nano-banana",
        prompt="Beautiful woman portrait, professional photo",
        negative_prompt="blurry, low quality, text, watermark, deformed",
        aspect_ratio="3:4",
        output_format="png",
    )
    
    if result.success:
        print(f"✅ Успех!")
        print(f"   URL: {result.image_url}")
        print(f"   Время: {result.generation_time:.2f} сек")
    else:
        print(f"❌ Ошибка: {result.error}")
    
    return result


async def main():
    print("\n🍌 Тестирование Nano Banano API\n")
    
    # Проверяем установлен ли fal-client
    try:
        import fal_client
        print(f"✅ fal-client установлен")
    except ImportError:
        print("❌ fal-client не установлен!")
        print("   Выполните: pip install fal-client")
        return
    
    # Тест 1: Базовая генерация
    result1 = await test_text_to_image()
    
    # Тест 2: Pro версия
    result2 = await test_text_to_image_pro()
    
    # Тест 3: С негативным промптом
    result3 = await test_with_negative_prompt()
    
    # Итоги
    print("\n" + "=" * 50)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    tests = [
        ("Nano Banana", result1),
        ("Nano Banana Pro", result2),
        ("С негативным промптом", result3),
    ]
    
    for name, result in tests:
        status = "✅" if result.success else "❌"
        print(f"{status} {name}")
    
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
