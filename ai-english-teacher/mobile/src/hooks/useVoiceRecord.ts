import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { useCallback, useState } from 'react';

export function useVoiceRecord() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const startRecording = useCallback(async () => {
    const permission = await Audio.requestPermissionsAsync();
    if (!permission.granted) {
      throw new Error('Microphone permission is required for voice practice.');
    }
    await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
    const { recording: rec } = await Audio.Recording.createAsync(
      Audio.RecordingOptionsPresets.HIGH_QUALITY,
    );
    setRecording(rec);
    setIsRecording(true);
  }, []);

  const stopRecording = useCallback(async (): Promise<{ base64: string; durationMs: number } | null> => {
    if (!recording) return null;
    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    setRecording(null);
    if (!uri) return null;

    const status = await recording.getStatusAsync();
    const durationMs = status.durationMillis || 0;
    const base64 = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    return { base64, durationMs };
  }, [recording]);

  return { startRecording, stopRecording, isRecording };
}
