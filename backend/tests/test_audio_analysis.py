#!/usr/bin/env python3
"""
Audio analysis script to diagnose transcription issues
"""
import os
import sys
from pathlib import Path
import json

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

def analyze_audio_file(meeting_id: str):
    """Analyze the audio file to understand potential transcription issues"""
    
    audio_path = Path(__file__).parent.parent / f"storage/audio/{meeting_id}_audio.mp3"
    
    if not audio_path.exists():
        print(f"[ERROR] Audio file not found: {audio_path}")
        return False
    
    print(f"[ANALYZE] Analyzing audio file: {audio_path}")
    print(f"[INFO] File size: {audio_path.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        # Try to analyze audio properties
        from pydub import AudioSegment
        
        audio = AudioSegment.from_mp3(str(audio_path))
        
        duration = len(audio) / 1000.0  # seconds
        sample_rate = audio.frame_rate
        channels = audio.channels
        
        print(f"[TIME] Duration: {duration:.2f} seconds")
        print(f"[AUDIO] Sample Rate: {sample_rate} Hz")
        print(f"[AUDIO] Channels: {channels}")
        
        # Check for potential issues
        issues = []
        
        if duration < 1.0:
            issues.append("Audio is very short (< 1 second)")
        elif duration > 600:
            issues.append("Audio is very long (> 10 minutes)")
        
        if sample_rate < 8000:
            issues.append("Sample rate is very low (< 8kHz)")
        elif sample_rate > 48000:
            issues.append("Sample rate is very high (> 48kHz)")
        
        if channels > 2:
            issues.append("Audio has more than 2 channels")
        
        if issues:
            print("\n[WARNING] Potential issues detected:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n[OK] Audio file appears to be in good condition")
        
        return True
        
    except ImportError:
        print("[WARNING] pydub not available, cannot analyze audio properties")
        return False
    except Exception as e:
        print(f"[ERROR] Error analyzing audio: {str(e)}")
        return False

def test_transcription_with_analysis(meeting_id: str):
    """Test transcription with detailed analysis"""
    
    print(f"\n[TEST] Testing transcription for meeting_id: {meeting_id}")
    
    # First analyze the audio
    if not analyze_audio_file(meeting_id):
        return False
    
    # Check existing transcript - update path to go up one level
    transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
    if transcript_path.exists():
        print(f"\n[DOC] Found existing transcript: {transcript_path}")
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            transcript = data.get('transcript', '')
            print(f"[TEXT] Current transcript length: {len(transcript)} characters")
            print(f"[TEXT] Transcript preview: {transcript[:200]}...")
            
            # Check for repetition patterns
            sentences = transcript.split('.')
            unique_sentences = set(s.strip() for s in sentences if s.strip())
            repetition_ratio = len(unique_sentences) / len(sentences) if sentences else 0
            
            print(f"[ANALYSIS] Repetition analysis:")
            print(f"   - Total sentences: {len(sentences)}")
            print(f"   - Unique sentences: {len(unique_sentences)}")
            print(f"   - Repetition ratio: {repetition_ratio:.2f}")
            
            if repetition_ratio < 0.5:
                print("   [WARNING] High repetition detected!")
            
        except Exception as e:
            print(f"[ERROR] Error reading transcript: {str(e)}")
    
    # Test new transcription
    print(f"\n[TEST] Testing improved transcription...")
    try:
        from agents.transcription_agent import transcribe_audio_file
        
        result = transcribe_audio_file(meeting_id)
        
        print("[OK] Transcription completed!")
        print(f"[TEXT] New transcript length: {len(result['transcript'])} characters")
        print(f"[TEXT] New transcript preview: {result['transcript'][:200]}...")
        
        if 'original_length' in result and 'cleaned_length' in result:
            print(f"[CLEAN] Cleaning removed {result['original_length'] - result['cleaned_length']} characters")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Transcription failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with the existing meeting ID
    meeting_id = "bbd45fb8-a2a9-4708-b929-a9acb2fda37e"
    
    print("Audio Analysis and Transcription Test")
    print("=" * 50)
    
    success = test_transcription_with_analysis(meeting_id)
    
    if success:
        print("\nAnalysis completed successfully!")
    else:
        print("\nAnalysis failed. Please check the implementation.") 