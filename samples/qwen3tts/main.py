import os
import sys
import torch
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.qwen3tts import create_qwen_tts_agent

def test_qwen_tts_plugin():
    print("=" * 60)
    print("QWENTTS PLUGIN TEST")
    print("=" * 60)

    try:
        print("\n1. Creating QwenTTS agent...")
        agent = create_qwen_tts_agent(
            device="cuda" if torch.cuda.is_available() else "cpu",
            dtype=torch.float32
        )
        print(f"✅ Agent created: {agent.name}")
        print(f"   Available skills: {list(agent.tts_skills.keys())}")

        print("\n2. Standard voice generation test:")
        print("-" * 40)

        test_text = "Hello Alice and Bob. This is a test of the QwenTTS speech synthesis system."
        result = agent.generate_voice(
            text=test_text,
            language="english",
            speaker="ryan",
            max_new_tokens=512
        )

        if result.get('success'):
            print(f"✅ Success: {result.get('filename')}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
            print(f"   Volume level: {result.get('db_level', 0):.1f} dBFS")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

        print("\n3. Preparing reference audio for cloning:")
        print("-" * 40)

        ref_audio_path = "test_reference.wav"
        ref_text = "Alice and Bob are working together on a cryptography project. They need to exchange secure messages without Eve intercepting their communication."

        if not os.path.exists(ref_audio_path):
            print("Creating reference audio...")
            ref_result = agent.generate_voice(
                text=ref_text,
                language="english",
                speaker="ryan",
                max_new_tokens=768
            )

            if ref_result.get('success'):
                import shutil
                ref_filename = ref_result.get('filename')
                if ref_filename and os.path.exists(ref_filename):
                    shutil.move(ref_filename, ref_audio_path)
                    print(f"✅ Reference created: {ref_audio_path}")

                    with open("reference_text.txt", "w", encoding="utf-8") as f:
                        f.write(ref_text)
                else:
                    print("⚠️ Failed to create reference")
                    return
            else:
                print(f"❌ Reference creation error: {ref_result.get('error')}")
                return
        else:
            print(f"✅ Reference already exists: {ref_audio_path}")

        print("\n4. Voice cloning test (ICL mode):")
        print("-" * 40)

        test_texts = [
            "Hello Alice, this is Bob. I've successfully cloned your voice using this system.",
            "Bob, can you hear me clearly? The voice cloning technology is working perfectly.",
            "Alice and Bob are testing speech synthesis with different intonations and emotions."
        ]

        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}: '{text}'")

            result = agent.generate_voice_clone(
                text=text,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text,
                language="english",
                x_vector_only_mode=False,
                max_new_tokens=512
            )

            if result.get('success'):
                print(f"  ✅ Success: {result.get('filename')}")
                print(f"     Duration: {result.get('duration', 0):.2f}s")
                print(f"     Mode: {result.get('mode', 'unknown')}")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")

        print("\n5. Voice cloning test (x-vector mode):")
        print("-" * 40)

        test_text = "Alice, please confirm if you can recognize my cloned voice. This is Bob speaking."

        result = agent.generate_voice_clone(
            text=test_text,
            ref_audio_path=ref_audio_path,
            language="english",
            x_vector_only_mode=True,
            max_new_tokens=512
        )

        if result.get('success'):
            print(f"✅ Success: {result.get('filename')}")
            print(f"   Mode: {result.get('mode', 'unknown')}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

        print("\n6. Audio processing test:")
        print("-" * 40)

        audio_files = [f for f in os.listdir('.') if f.endswith('.wav')]
        if audio_files:
            test_file = audio_files[0]
            print(f"Processing file: {test_file}")

            result = agent.process_audio(
                audio_path=test_file,
                target_dbfs=-14.0,
                apply_compression=True
            )

            if result.get('success'):
                print(f"✅ Success: {result.get('filename')}")
                analysis = result.get('analysis', {})
                before = analysis.get('before', {})
                after = analysis.get('after', {})

                print(f"   Volume improvement: {result.get('improvement_db', 0):.1f} dB")
                print(f"   Before: {before.get('db_rms', 0):.1f} dBFS")
                print(f"   After: {after.get('db_rms', 0):.1f} dBFS")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")

        print("\n7. Audio analysis test:")
        print("-" * 40)

        if audio_files:
            test_file = audio_files[0]
            print(f"Analyzing file: {test_file}")

            result = agent.analyze_audio(audio_path=test_file)

            if result.get('success'):
                print(f"✅ Analysis completed")
                analysis = result.get('analysis', {})
                quality = result.get('quality', 'UNKNOWN')

                print(f"   Quality: {quality}")
                print(f"   Duration: {analysis.get('duration', 0):.2f}s")
                print(f"   Volume level: {analysis.get('db_rms', 0):.1f} dBFS")
                print(f"   Sample rate: {analysis.get('sample_rate', 0)} Hz")

                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"   Recommendations:")
                    for rec in recommendations[:3]:
                        print(f"     • {rec}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")

        print("\n8. Complex cloning test:")
        print("-" * 40)

        result = agent.test_voice_cloning(
            ref_audio_path=ref_audio_path,
            ref_text=ref_text,
            test_texts=[
                "Alice said to Bob: The encryption key is safe with me.",
                "Bob replied: Perfect, now we can communicate securely without Eve listening.",
                "Both Alice and Bob confirmed that the voice cloning system works exceptionally well."
            ]
        )

        if result.get('success'):
            summary = result.get('summary', {})
            print(f"✅ Test completed:")
            print(f"   Total tests: {result.get('test_count', 0)}")
            print(f"   Successful: {summary.get('successful', 0)}")
            print(f"   Failed: {summary.get('failed', 0)}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

        print("\n9. Created files analysis:")
        print("-" * 40)

        wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]

        if wav_files:
            print(f"Files found: {len(wav_files)}")
            print("\n" + "=" * 75)
            print(f"{'File':30} {'Size (MB)':12} {'Modified':20}")
            print("=" * 75)

            for f in sorted(wav_files):
                size_mb = os.path.getsize(f) / (1024 * 1024)
                mtime = os.path.getmtime(f)
                from datetime import datetime
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

                print(f"{f:30} {size_mb:11.2f} MB  {mtime_str:20}")

            print("=" * 75)
        else:
            print("⚠️ No files found")

        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qwen_tts_plugin()
