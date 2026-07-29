import * as Speech from 'expo-speech';
import { useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { api } from '@/lib/api';
import { useVoiceRecord } from '@/hooks/useVoiceRecord';
import { COLORS, SCENARIOS } from '@/constants';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  corrections?: Array<{ text?: string; correction?: string }>;
  voiceScore?: number;
}

interface VoiceReport {
  fluency: number;
  pronunciation: number;
  overall_score: number;
}

export default function PracticeScreen() {
  const [scenario, setScenario] = useState('job_interview');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [lastVoiceReport, setLastVoiceReport] = useState<VoiceReport | null>(null);
  const { startRecording, stopRecording, isRecording } = useVoiceRecord();

  function speak(text: string) {
    Speech.stop();
    Speech.speak(text, { language: 'en-US', rate: 0.95 });
  }

  async function startConversation() {
    setLoading(true);
    try {
      const res = (await api.conversations.start({ scenario })) as {
        id: string;
        initial_message: { content: string };
      };
      setConversationId(res.id);
      const msg: Message = { id: '0', role: 'assistant', content: res.initial_message.content };
      setMessages([msg]);
      if (autoSpeak) speak(res.initial_message.content);
      setStarted(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start conversation');
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(text?: string, voiceScore?: number) {
    const userMsg = (text ?? input).trim();
    if (!userMsg || !conversationId) return;
    setInput('');
    setLoading(true);
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), role: 'user', content: userMsg, voiceScore },
    ]);
    try {
      const res = (await api.conversations.sendMessage(conversationId, userMsg)) as {
        assistant_message: { content: string; metadata?: { grammar_corrections?: Message['corrections'] } };
      };
      const assistant: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.assistant_message.content,
        corrections: res.assistant_message.metadata?.grammar_corrections,
      };
      setMessages((prev) => [...prev, assistant]);
      if (autoSpeak) speak(assistant.content);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }

  async function handleMicPress() {
    if (isRecording) {
      try {
        setLoading(true);
        const audio = await stopRecording();
        if (!audio) return;

        const report = (await api.voice.analyze({
          audio_base64: audio.base64,
          audio_mime_type: 'audio/m4a',
          duration_seconds: audio.durationMs / 1000,
          conversation_id: conversationId || undefined,
        })) as VoiceReport & { transcript: string };

        setLastVoiceReport({
          fluency: report.fluency,
          pronunciation: report.pronunciation,
          overall_score: report.overall_score,
        });
        await sendMessage(report.transcript, report.overall_score);
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Voice analysis failed');
      } finally {
        setLoading(false);
      }
      return;
    }

    try {
      await startRecording();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Could not start recording');
    }
  }

  if (!started) {
    return (
      <View style={styles.container}>
        <Text style={styles.heading}>Choose a scenario</Text>
        <Text style={styles.hint}>Practice with text or tap the mic to speak</Text>
        <View style={styles.scenarioGrid}>
          {SCENARIOS.map((s) => (
            <Pressable
              key={s.id}
              style={[styles.scenarioCard, scenario === s.id && styles.scenarioSelected]}
              onPress={() => setScenario(s.id)}
            >
              <Text style={[styles.scenarioText, scenario === s.id && styles.scenarioTextSelected]}>{s.label}</Text>
            </Pressable>
          ))}
        </View>
        <Pressable style={styles.startBtn} onPress={startConversation} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.startBtnText}>Start conversation</Text>}
        </Pressable>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={styles.chatContainer} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={90}>
      <Pressable style={styles.speakToggle} onPress={() => setAutoSpeak(!autoSpeak)}>
        <Text style={styles.speakToggleText}>{autoSpeak ? '🔊 Auto-speak ON' : '🔇 Auto-speak OFF'}</Text>
      </Pressable>

      {lastVoiceReport && (
        <View style={styles.voiceReport}>
          <Text style={styles.voiceReportText}>
            Voice: {lastVoiceReport.overall_score}/100 · Fluency {lastVoiceReport.fluency} · Pronunciation {lastVoiceReport.pronunciation}
          </Text>
        </View>
      )}

      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messageList}
        renderItem={({ item }) => (
          <View style={[styles.bubble, item.role === 'user' ? styles.userBubble : styles.assistantBubble]}>
            <Text style={[styles.bubbleText, item.role === 'user' && styles.userBubbleText]}>{item.content}</Text>
            {item.voiceScore != null && (
              <Text style={styles.voiceBadge}>🎤 Score: {item.voiceScore}</Text>
            )}
            {item.corrections && item.corrections.length > 0 && (
              <View style={styles.corrections}>
                {item.corrections.map((c, i) => (
                  <Text key={i} style={styles.correctionText}>
                    ✏️ {c.text} → {c.correction}
                  </Text>
                ))}
              </View>
            )}
            {item.role === 'assistant' && (
              <Pressable onPress={() => speak(item.content)}>
                <Text style={styles.replay}>▶ Replay</Text>
              </Pressable>
            )}
          </View>
        )}
      />

      <View style={styles.inputRow}>
        <Pressable
          style={[styles.micBtn, isRecording && styles.micBtnActive]}
          onPress={handleMicPress}
          disabled={loading && !isRecording}
        >
          <Text style={styles.micBtnText}>{isRecording ? '⏹' : '🎤'}</Text>
        </Pressable>
        <TextInput
          style={styles.input}
          placeholder="Type your message..."
          value={input}
          onChangeText={setInput}
          multiline
        />
        <Pressable style={styles.sendBtn} onPress={() => sendMessage()} disabled={loading}>
          {loading && !isRecording ? <ActivityIndicator color="#fff" size="small" /> : <Text style={styles.sendBtnText}>Send</Text>}
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background, padding: 16 },
  heading: { fontSize: 20, fontWeight: '700', color: COLORS.text, marginBottom: 4 },
  hint: { fontSize: 14, color: COLORS.textMuted, marginBottom: 20 },
  scenarioGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 24 },
  scenarioCard: { width: '47%', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: COLORS.border, backgroundColor: COLORS.card },
  scenarioSelected: { borderColor: COLORS.primary, backgroundColor: '#eff6ff' },
  scenarioText: { fontSize: 14, fontWeight: '500', color: COLORS.text },
  scenarioTextSelected: { color: COLORS.primary },
  startBtn: { backgroundColor: COLORS.primary, borderRadius: 12, padding: 16, alignItems: 'center' },
  startBtnText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  chatContainer: { flex: 1, backgroundColor: COLORS.background },
  speakToggle: { padding: 10, alignItems: 'center' },
  speakToggleText: { fontSize: 13, color: COLORS.textMuted },
  voiceReport: { marginHorizontal: 16, marginBottom: 8, backgroundColor: '#ecfdf5', borderRadius: 8, padding: 10, borderWidth: 1, borderColor: '#a7f3d0' },
  voiceReportText: { fontSize: 12, color: '#065f46', textAlign: 'center' },
  messageList: { padding: 16, paddingBottom: 8 },
  bubble: { maxWidth: '85%', borderRadius: 16, padding: 12, marginBottom: 10 },
  userBubble: { alignSelf: 'flex-end', backgroundColor: COLORS.primary },
  assistantBubble: { alignSelf: 'flex-start', backgroundColor: COLORS.card, borderWidth: 1, borderColor: COLORS.border },
  bubbleText: { fontSize: 15, color: COLORS.text, lineHeight: 22 },
  userBubbleText: { color: '#fff' },
  voiceBadge: { fontSize: 11, color: '#dbeafe', marginTop: 4 },
  corrections: { marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: COLORS.border },
  correctionText: { fontSize: 12, color: COLORS.textMuted, marginBottom: 4 },
  replay: { fontSize: 12, color: COLORS.primary, marginTop: 6 },
  inputRow: { flexDirection: 'row', padding: 12, gap: 8, borderTopWidth: 1, borderTopColor: COLORS.border, backgroundColor: COLORS.card, alignItems: 'center' },
  micBtn: { width: 44, height: 44, borderRadius: 22, borderWidth: 1, borderColor: COLORS.border, alignItems: 'center', justifyContent: 'center', backgroundColor: COLORS.card },
  micBtnActive: { backgroundColor: '#fee2e2', borderColor: '#ef4444' },
  micBtnText: { fontSize: 18 },
  input: { flex: 1, borderWidth: 1, borderColor: COLORS.border, borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10, maxHeight: 100, fontSize: 15 },
  sendBtn: { backgroundColor: COLORS.primary, borderRadius: 20, paddingHorizontal: 20, paddingVertical: 12, justifyContent: 'center' },
  sendBtnText: { color: '#fff', fontWeight: '600' },
});
