#!/usr/bin/env python3
"""
Test different Whisper API parameters to find optimal configuration
"""
import openai
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def test_whisper_parameters(audio_file_path: str, test_name: str, **params):
    """Test Whisper API with different parameters"""
    
    print(f"\n🧪 Testing: {test_name}")
    print(f"📋 Parameters: {params}")
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                **params
            )
        
        # Clean up repetitive content
        cleaned_transcript = clean_transcript(transcript_response)
        
        # Analyze results
        original_length = len(transcript_response)
        cleaned_length = len(cleaned_transcript)
        reduction = original_length - cleaned_length
        
        print(f"✅ Success!")
        print(f"📝 Original length: {original_length} chars")
        print(f"📝 Cleaned length: {cleaned_length} chars")
        print(f"🧹 Reduction: {reduction} chars ({reduction/original_length*100:.1f}%)")
        print(f"📄 Preview: {cleaned_transcript[:150]}...")
        
        return {
            "test_name": test_name,
            "parameters": params,
            "original_length": original_length,
            "cleaned_length": cleaned_length,
            "reduction": reduction,
            "transcript": cleaned_transcript
        }
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return None

def clean_transcript(transcript: str) -> str:
    """Clean repetitive content from transcript"""
    if not transcript:
        return transcript
    
    sentences = transcript.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    cleaned_sentences = []
    for i, sentence in enumerate(sentences):
        if i == 0 or sentence != sentences[i-1]:
            cleaned_sentences.append(sentence)
    
    cleaned_transcript = '. '.join(cleaned_sentences)
    if cleaned_transcript and not cleaned_transcript.endswith('.'):
        cleaned_transcript += '.'
    
    return cleaned_transcript

def main():
    """Test various Whisper configurations"""
    
    meeting_id = "3173c1ca-5e13-454e-9b20-706fab4d53f1"
    audio_file_path = Path(f"storage/audio/{meeting_id}_audio.mp3")
    
    if not audio_file_path.exists():
        print(f"❌ Audio file not found: {audio_file_path}")
        return
    
    print("🔍 Testing Whisper API Parameters")
    print("=" * 50)
    print(f"🎵 Audio file: {audio_file_path}")
    
    # Test configurations
    test_configs = [
        {
            "name": "Default settings",
            "params": {}
        },
        {
            "name": "English language specified",
            "params": {"language": "en"}
        },
        {
            "name": "Low temperature (more deterministic)",
            "params": {"language": "en", "temperature": 0.0}
        },
        {
            "name": "With prompt",
            "params": {
                "language": "en", 
                "temperature": 0.0,
                "prompt": "This is a clear recording. Please transcribe accurately without repetition."
            }
        },
        {
            "name": "Meeting context prompt",
            "params": {
                "language": "en", 
                "temperature": 0.0,
                "prompt": "This is a meeting recording. Transcribe the conversation clearly and accurately."
            }
        },
        {
            "name": "Music/song context prompt",
            "params": {
                "language": "en", 
                "temperature": 0.0,
                "prompt": "This is a song or music recording. Transcribe the lyrics accurately."
            }
        }
    ]
    
    results = []
    
    for config in test_configs:
        result = test_whisper_parameters(
            str(audio_file_path),
            config["name"],
            **config["params"]
        )
        
        if result:
            results.append(result)
    
    # Find best result
    if results:
        best_result = min(results, key=lambda x: x["reduction"] / x["original_length"])
        
        print(f"\n🏆 Best configuration: {best_result['test_name']}")
        print(f"📊 Reduction rate: {best_result['reduction']/best_result['original_length']*100:.1f}%")
        print(f"📝 Final transcript: {best_result['transcript']}")
        
        # Save best result
        output_path = Path(f"storage/transcripts/{meeting_id}_optimized.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "meeting_id": meeting_id,
                "test_name": best_result["test_name"],
                "parameters": best_result["parameters"],
                "created_at": datetime.utcnow().isoformat(),
                "transcript": best_result["transcript"],
                "original_length": best_result["original_length"],
                "cleaned_length": best_result["cleaned_length"],
                "reduction": best_result["reduction"]
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved optimized transcript to: {output_path}")
    
    else:
        print("❌ No successful tests completed")

if __name__ == "__main__":
    main() 