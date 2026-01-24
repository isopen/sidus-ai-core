import torch
import numpy as np
import soundfile as sf
from scipy import signal
from typing import Optional, Dict, Any, Tuple

class AudioProcessor:
    @staticmethod
    def normalize_audio(audio: np.ndarray, target_dbfs: float = -20.0) -> np.ndarray:
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        audio = audio - np.mean(audio)

        rms = np.sqrt(np.mean(audio**2))

        if rms > 0:
            target_linear = 10 ** (target_dbfs / 20.0)
            gain = target_linear / rms

            audio = audio * min(gain, 10.0)

            threshold = 0.95
            audio = np.where(
                audio > threshold, 
                threshold + (audio - threshold) * 0.3,
                np.where(
                    audio < -threshold, 
                    -threshold + (audio + threshold) * 0.3, 
                    audio
                )
            )

        return audio

    @staticmethod
    def apply_compression(audio: np.ndarray, threshold: float = -15.0, 
                         ratio: float = 3.0, attack: float = 0.01, 
                         release: float = 0.1, sr: int = 24000) -> np.ndarray:
        attack_samples = int(attack * sr)
        release_samples = int(release * sr)

        amplitude = np.abs(audio)
        envelope = np.zeros_like(amplitude)

        for i in range(1, len(amplitude)):
            if amplitude[i] > envelope[i-1]:
                envelope[i] = envelope[i-1] + (amplitude[i] - envelope[i-1]) / attack_samples
            else:
                envelope[i] = envelope[i-1] + (amplitude[i] - envelope[i-1]) / release_samples

        envelope_db = 20 * np.log10(envelope + 1e-10)

        gain_reduction = np.zeros_like(envelope_db)
        mask = envelope_db > threshold
        gain_reduction[mask] = (envelope_db[mask] - threshold) * (1 - 1/ratio)

        gain_linear = 10 ** (-gain_reduction / 20)
        compressed = audio * gain_linear

        return AudioProcessor.normalize_audio(compressed, target_dbfs=-16.0)

    @staticmethod
    def process_audio_for_tts(audio: np.ndarray, sr: int = 24000, 
                             target_sr: int = 24000) -> Tuple[np.ndarray, int]:
        if sr != target_sr:
            audio = signal.resample_poly(audio, target_sr, sr)
            sr = target_sr

        audio = AudioProcessor.normalize_audio(audio, target_dbfs=-18.0)
        audio = AudioProcessor.apply_compression(audio, threshold=-20.0, ratio=2.5, sr=sr)
        audio = AudioProcessor.normalize_audio(audio, target_dbfs=-16.0)

        return audio, sr

    @staticmethod
    def analyze_audio(audio: np.ndarray, sr: int) -> Dict[str, Any]:
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        db_rms = 20 * np.log10(rms + 1e-10)
        db_peak = 20 * np.log10(peak + 1e-10)
        duration = len(audio) / sr
        clipping = np.sum(np.abs(audio) > 0.999) / len(audio) * 100

        return {
            'duration': duration,
            'db_rms': db_rms,
            'db_peak': db_peak,
            'clipping_percent': clipping,
            'rms': rms,
            'peak': peak,
            'sample_rate': sr,
            'samples': len(audio)
        }

class QwenTTSProcessor:
    def __init__(self, device: str = "cpu", dtype: torch.dtype = torch.float32):
        self.device = device
        self.dtype = dtype
        self.base_model = None
        self.custom_model = None
        self.audio_processor = AudioProcessor()

        print(f"QwenTTSProcessor initialized (device={device})")

    def load_base_model(self) -> bool:
        try:
            from qwen_tts import Qwen3TTSModel

            self.base_model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
                dtype=self.dtype,
                device_map=self.device
            )
            print("✅ Base model loaded")
            return True
        except Exception as e:
            print(f"❌ Error loading base model: {e}")
            return False

    def load_custom_model(self) -> bool:
        try:
            from qwen_tts import Qwen3TTSModel

            self.custom_model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
                dtype=self.dtype,
                device_map=self.device
            )
            print("✅ CustomVoice model loaded")
            return True
        except Exception as e:
            print(f"❌ Error loading CustomVoice model: {e}")
            return False

    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        try:
            audio, sr = sf.read(audio_path)
            print(f"✅ Audio loaded: {audio_path} ({len(audio)} samples, {sr} Hz)")
            return audio, sr
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            raise

    def save_audio(self, audio: np.ndarray, sr: int, filename: str) -> str:
        try:
            sf.write(filename, audio, sr)
            print(f"✅ Audio saved: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            raise

    def generate_voice(self, 
                      text: str,
                      language: str = "english",
                      speaker: str = "ryan",
                      max_new_tokens: int = 512,
                      top_p: float = 0.9,
                      temperature: float = 0.8) -> Dict[str, Any]:

        if not self.custom_model:
            if not self.load_custom_model():
                return {"success": False, "error": "Failed to load CustomVoice model"}

        try:
            print(f"Generating voice: '{text[:50]}...'")

            wavs, sr = self.custom_model.generate_custom_voice(
                text=text,
                language=language,
                speaker=speaker,
                max_new_tokens=max_new_tokens
            )

            audio = wavs[0] if isinstance(wavs, list) else wavs

            audio_processed, sr = self.audio_processor.process_audio_for_tts(audio, sr=sr)

            analysis = self.audio_processor.analyze_audio(audio_processed, sr)

            return {
                "success": True,
                "audio": audio_processed,
                "sample_rate": sr,
                "duration": analysis['duration'],
                "db_level": analysis['db_rms'],
                "original_length": len(audio),
                "processed_length": len(audio_processed)
            }

        except Exception as e:
            print(f"❌ Error generating voice: {e}")
            return {"success": False, "error": str(e)}

    def generate_voice_clone(self,
                            text: str,
                            ref_audio_path: str,
                            ref_text: Optional[str] = None,
                            language: str = "english",
                            x_vector_only_mode: bool = False,
                            max_new_tokens: int = 512,
                            top_p: float = 0.9,
                            temperature: float = 0.8) -> Dict[str, Any]:

        if not self.base_model:
            if not self.load_base_model():
                return {"success": False, "error": "Failed to load base model"}

        try:
            ref_audio, ref_sr = self.load_audio(ref_audio_path)

            ref_audio_processed, ref_sr = self.audio_processor.process_audio_for_tts(ref_audio, sr=ref_sr)

            print(f"Cloning voice: '{text[:50]}...'")

            ref_audio_tuple = (ref_audio_processed, ref_sr)

            wavs, sr = self.base_model.generate_voice_clone(
                text=text,
                language=language,
                ref_audio=ref_audio_tuple,
                ref_text=ref_text,
                x_vector_only_mode=x_vector_only_mode,
                max_new_tokens=max_new_tokens,
                top_p=top_p,
                temperature=temperature
            )

            audio = wavs[0] if isinstance(wavs, list) else wavs

            audio_processed, sr = self.audio_processor.process_audio_for_tts(audio, sr=sr)

            analysis = self.audio_processor.analyze_audio(audio_processed, sr)

            return {
                "success": True,
                "audio": audio_processed,
                "sample_rate": sr,
                "duration": analysis['duration'],
                "db_level": analysis['db_rms'],
                "ref_audio": ref_audio_path,
                "mode": "x_vector_only" if x_vector_only_mode else "icl",
                "original_length": len(audio),
                "processed_length": len(audio_processed)
            }

        except Exception as e:
            print(f"❌ Error cloning voice: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def process_audio_file(self,
                          audio_path: str,
                          target_dbfs: float = -16.0,
                          apply_compression: bool = True) -> Dict[str, Any]:

        try:
            audio, sr = self.load_audio(audio_path)

            audio_normalized = self.audio_processor.normalize_audio(audio, target_dbfs=target_dbfs)

            if apply_compression:
                audio_processed = self.audio_processor.apply_compression(
                    audio_normalized, 
                    threshold=-20.0, 
                    ratio=2.5, 
                    sr=sr
                )
            else:
                audio_processed = audio_normalized

            audio_final = self.audio_processor.normalize_audio(audio_processed, target_dbfs=target_dbfs)

            analysis_before = self.audio_processor.analyze_audio(audio, sr)
            analysis_after = self.audio_processor.analyze_audio(audio_final, sr)

            return {
                "success": True,
                "audio": audio_final,
                "sample_rate": sr,
                "analysis_before": analysis_before,
                "analysis_after": analysis_after,
                "improvement_db": analysis_after['db_rms'] - analysis_before['db_rms']
            }

        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            return {"success": False, "error": str(e)}

    def analyze_audio_file(self, audio_path: str) -> Dict[str, Any]:

        try:
            audio, sr = self.load_audio(audio_path)
            analysis = self.audio_processor.analyze_audio(audio, sr)

            return {
                "success": True,
                "audio_path": audio_path,
                "analysis": analysis,
                "quality": "GOOD" if analysis['db_rms'] > -25 and analysis['clipping_percent'] < 1 else "POOR",
                "recommendations": self._get_audio_recommendations(analysis)
            }

        except Exception as e:
            print(f"❌ Error analyzing audio: {e}")
            return {"success": False, "error": str(e)}

    def _get_audio_recommendations(self, analysis: Dict[str, Any]) -> list:
        recommendations = []

        if analysis['db_rms'] < -25:
            recommendations.append(f"Audio too quiet ({analysis['db_rms']:.1f} dBFS). Apply normalization to -16 dBFS.")

        if analysis['clipping_percent'] > 1:
            recommendations.append(f"Clipping detected ({analysis['clipping_percent']:.1f}%). Reduce volume.")

        if analysis['peak'] > 0.9:
            recommendations.append(f"High peak level ({analysis['peak']:.2f}). Apply compression.")

        if not recommendations:
            recommendations.append("Audio quality is good. No additional processing required.")

        return recommendations
