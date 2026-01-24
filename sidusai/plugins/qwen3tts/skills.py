from typing import Dict, Any
from datetime import datetime
import os

class TTSDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def generate_voice_skill(context: Dict[str, Any]) -> TTSDataValue:
    print("Starting generate_voice_skill...")

    text = context.get('text', '')
    language = context.get('language', 'english')
    speaker = context.get('speaker', 'ryan')
    max_new_tokens = context.get('max_new_tokens', 512)
    top_p = context.get('top_p', 0.9)
    temperature = context.get('temperature', 0.8)

    try:
        processor = context.get('tts_processor')

        if not processor:
            result = {"success": False, "error": "TTS processor not available"}
            return TTSDataValue(result)

        generation_result = processor.generate_voice(
            text=text,
            language=language,
            speaker=speaker,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            temperature=temperature
        )

        if generation_result.get('success'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_voice_{timestamp}.wav"

            try:
                processor.save_audio(
                    generation_result['audio'],
                    generation_result['sample_rate'],
                    filename
                )

                analysis_result = {
                    "success": True,
                    "filename": filename,
                    "text": text,
                    "language": language,
                    "speaker": speaker,
                    "duration": generation_result['duration'],
                    "db_level": generation_result['db_level'],
                    "sample_rate": generation_result['sample_rate'],
                    "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "standard_generation"
                }

                print(f"✅ Voice generated: {filename}")
                print(f"   Duration: {generation_result['duration']:.2f}s")
                print(f"   DB Level: {generation_result['db_level']:.1f} dBFS")

            except Exception as save_error:
                analysis_result = {
                    "success": False,
                    "error": f"Failed to save audio: {str(save_error)}",
                    "generation_success": True,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Failed to save audio: {save_error}")
        else:
            analysis_result = {
                "success": False,
                "error": generation_result.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Voice generation failed: {generation_result.get('error')}")

        return TTSDataValue(analysis_result)

    except Exception as e:
        print(f"Error in generate_voice_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return TTSDataValue(result)

def generate_voice_clone_skill(context: Dict[str, Any]) -> TTSDataValue:
    print("Starting generate_voice_clone_skill...")

    text = context.get('text', '')
    ref_audio_path = context.get('ref_audio_path', '')
    ref_text = context.get('ref_text')
    language = context.get('language', 'english')
    x_vector_only_mode = context.get('x_vector_only_mode', False)
    max_new_tokens = context.get('max_new_tokens', 512)
    top_p = context.get('top_p', 0.9)
    temperature = context.get('temperature', 0.8)

    try:
        processor = context.get('tts_processor')

        if not processor:
            result = {"success": False, "error": "TTS processor not available"}
            return TTSDataValue(result)

        if not os.path.exists(ref_audio_path):
            result = {"success": False, "error": f"Reference audio not found: {ref_audio_path}"}
            return TTSDataValue(result)

        clone_result = processor.generate_voice_clone(
            text=text,
            ref_audio_path=ref_audio_path,
            ref_text=ref_text,
            language=language,
            x_vector_only_mode=x_vector_only_mode,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            temperature=temperature
        )

        if clone_result.get('success'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode_str = "xvector" if x_vector_only_mode else "icl"
            filename = f"voice_clone_{mode_str}_{timestamp}.wav"

            try:
                processor.save_audio(
                    clone_result['audio'],
                    clone_result['sample_rate'],
                    filename
                )

                analysis_result = {
                    "success": True,
                    "filename": filename,
                    "text": text,
                    "ref_audio": ref_audio_path,
                    "ref_text": ref_text,
                    "language": language,
                    "mode": mode_str,
                    "duration": clone_result['duration'],
                    "db_level": clone_result['db_level'],
                    "sample_rate": clone_result['sample_rate'],
                    "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0,
                    "timestamp": datetime.now().isoformat(),
                    "details": {
                        "original_length": clone_result['original_length'],
                        "processed_length": clone_result['processed_length']
                    }
                }

                print(f"✅ Voice clone generated: {filename}")
                print(f"   Mode: {mode_str}")
                print(f"   Duration: {clone_result['duration']:.2f}s")
                print(f"   DB Level: {clone_result['db_level']:.1f} dBFS")
                print(f"   Reference: {os.path.basename(ref_audio_path)}")

            except Exception as save_error:
                analysis_result = {
                    "success": False,
                    "error": f"Failed to save audio: {str(save_error)}",
                    "clone_success": True,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Failed to save audio: {save_error}")
        else:
            analysis_result = {
                "success": False,
                "error": clone_result.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Voice cloning failed: {clone_result.get('error')}")

        return TTSDataValue(analysis_result)

    except Exception as e:
        print(f"Error in generate_voice_clone_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return TTSDataValue(result)

def process_audio_skill(context: Dict[str, Any]) -> TTSDataValue:
    print("Starting process_audio_skill...")

    audio_path = context.get('audio_path', '')
    target_dbfs = context.get('target_dbfs', -16.0)
    apply_compression = context.get('apply_compression', True)

    try:
        processor = context.get('tts_processor')

        if not processor:
            result = {"success": False, "error": "TTS processor not available"}
            return TTSDataValue(result)

        if not os.path.exists(audio_path):
            result = {"success": False, "error": f"Audio file not found: {audio_path}"}
            return TTSDataValue(result)

        process_result = processor.process_audio_file(
            audio_path=audio_path,
            target_dbfs=target_dbfs,
            apply_compression=apply_compression
        )

        if process_result.get('success'):
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_name}_processed_{timestamp}.wav"

            try:
                processor.save_audio(
                    process_result['audio'],
                    process_result['sample_rate'],
                    filename
                )

                before = process_result['analysis_before']
                after = process_result['analysis_after']
                improvement = process_result['improvement_db']

                analysis_result = {
                    "success": True,
                    "filename": filename,
                    "original_file": audio_path,
                    "target_dbfs": target_dbfs,
                    "apply_compression": apply_compression,
                    "improvement_db": improvement,
                    "analysis": {
                        "before": {
                            "duration": before['duration'],
                            "db_rms": before['db_rms'],
                            "db_peak": before['db_peak'],
                            "clipping_percent": before['clipping_percent']
                        },
                        "after": {
                            "duration": after['duration'],
                            "db_rms": after['db_rms'],
                            "db_peak": after['db_peak'],
                            "clipping_percent": after['clipping_percent']
                        }
                    },
                    "file_size": os.path.getsize(filename) if os.path.exists(filename) else 0,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✅ Audio processed: {filename}")
                print(f"   Original: {before['db_rms']:.1f} dBFS")
                print(f"   Processed: {after['db_rms']:.1f} dBFS")
                print(f"   Improvement: {improvement:.1f} dB")
                print(f"   Clipping: {before['clipping_percent']:.1f}% → {after['clipping_percent']:.1f}%")

            except Exception as save_error:
                analysis_result = {
                    "success": False,
                    "error": f"Failed to save audio: {str(save_error)}",
                    "process_success": True,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ Failed to save audio: {save_error}")
        else:
            analysis_result = {
                "success": False,
                "error": process_result.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Audio processing failed: {process_result.get('error')}")

        return TTSDataValue(analysis_result)

    except Exception as e:
        print(f"Error in process_audio_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return TTSDataValue(result)

def analyze_audio_skill(context: Dict[str, Any]) -> TTSDataValue:
    print("Starting analyze_audio_skill...")

    audio_path = context.get('audio_path', '')

    try:
        processor = context.get('tts_processor')

        if not processor:
            result = {"success": False, "error": "TTS processor not available"}
            return TTSDataValue(result)

        if not os.path.exists(audio_path):
            result = {"success": False, "error": f"Audio file not found: {audio_path}"}
            return TTSDataValue(result)

        analyze_result = processor.analyze_audio_file(audio_path)

        if analyze_result.get('success'):
            analysis = analyze_result['analysis']
            quality = analyze_result['quality']
            recommendations = analyze_result['recommendations']

            analysis_result = {
                "success": True,
                "audio_path": audio_path,
                "quality": quality,
                "analysis": {
                    "duration": analysis['duration'],
                    "sample_rate": analysis['sample_rate'],
                    "samples": analysis['samples'],
                    "db_rms": analysis['db_rms'],
                    "db_peak": analysis['db_peak'],
                    "rms": analysis['rms'],
                    "peak": analysis['peak'],
                    "clipping_percent": analysis['clipping_percent']
                },
                "recommendations": recommendations,
                "file_size": os.path.getsize(audio_path),
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Audio analysis: {audio_path}")
            print(f"   Quality: {quality}")
            print(f"   Duration: {analysis['duration']:.2f}s")
            print(f"   RMS Level: {analysis['db_rms']:.1f} dBFS")
            print(f"   Peak Level: {analysis['db_peak']:.1f} dBFS")
            print(f"   Clipping: {analysis['clipping_percent']:.1f}%")
            print(f"   Sample Rate: {analysis['sample_rate']} Hz")

            if recommendations:
                print(f"   Recommendations:")
                for rec in recommendations:
                    print(f"     • {rec}")

        else:
            analysis_result = {
                "success": False,
                "error": analyze_result.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Audio analysis failed: {analyze_result.get('error')}")

        return TTSDataValue(analysis_result)

    except Exception as e:
        print(f"Error in analyze_audio_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return TTSDataValue(result)
