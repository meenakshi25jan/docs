import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import * as Speech from 'expo-speech';
import { api } from '@/lib/api';
import { useVoiceRecord } from '@/hooks/useVoiceRecord';
import { COLORS } from '@/constants';

const GRADES = [5, 6, 7, 8, 9, 10, 11, 12];

interface Lesson {
  id: string;
  title: string;
  rule: string;
}

export default function GrammarScreen() {
  const [grade, setGrade] = useState(8);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [lessonId, setLessonId] = useState('');
  const [teacherText, setTeacherText] = useState('');
  const [feedback, setFeedback] = useState('');
  const [score, setScore] = useState<number | null>(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const { startRecording, stopRecording, isRecording } = useVoiceRecord();

  function speak(text: string) {
    Speech.stop();
    Speech.speak(text, { language: 'en-US', rate: 0.85 });
  }

  async function loadLessons(g: number) {
    setGrade(g);
    try {
      const res = (await api.grammar.lessons(g)) as { lessons: Lesson[] };
      setLessons(res.lessons);
      if (res.lessons[0]) setLessonId(res.lessons[0].id);
    } catch {
      alert('Could not load lessons');
    }
  }

  async function startLesson() {
    if (!lessonId) return;
    setLoading(true);
    try {
      const res = (await api.grammar.intro(grade, lessonId)) as { intro: { response?: string } };
      const msg = res.intro?.response || 'Let us practice grammar together.';
      setTeacherText(msg);
      speak(msg);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start');
    } finally {
      setLoading(false);
    }
  }

  async function practice(spoken: string) {
    if (!spoken.trim() || !lessonId) return;
    setLoading(true);
    try {
      const res = (await api.grammar.practice({
        grade,
        lesson_id: lessonId,
        transcript: spoken.trim(),
      })) as { grammar_score: number; teacher: { response?: string; encouragement?: string } };
      setScore(res.grammar_score);
      const msg = [res.teacher?.response, res.teacher?.encouragement].filter(Boolean).join(' ');
      setFeedback(msg);
      if (msg) speak(msg);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Practice failed');
    } finally {
      setLoading(false);
    }
  }

  async function handleMic() {
    if (isRecording) {
      try {
        setLoading(true);
        const audio = await stopRecording();
        if (audio) {
          const res = (await api.grammar.practice({
            grade,
            lesson_id: lessonId,
            audio_base64: audio.base64,
            audio_mime_type: 'audio/m4a',
            duration_seconds: audio.durationMs / 1000,
          })) as { grammar_score: number; teacher: { response?: string }; transcript?: string };
          if (res.transcript) setInput(res.transcript);
          setScore(res.grammar_score);
          setFeedback(res.teacher?.response || '');
          if (res.teacher?.response) speak(res.teacher.response);
        }
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Voice failed');
      } finally {
        setLoading(false);
      }
      return;
    }
    try {
      await startRecording();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Mic permission needed');
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>📚 Grammar Class</Text>
      <Text style={styles.sub}>Grades 5–12 · Voice teacher</Text>

      <Text style={styles.label}>Grade</Text>
      <FlatList
        horizontal
        data={GRADES}
        keyExtractor={(g) => String(g)}
        renderItem={({ item }) => (
          <Pressable
            style={[styles.chip, grade === item && styles.chipActive]}
            onPress={() => loadLessons(item)}
          >
            <Text style={grade === item ? styles.chipTextActive : styles.chipText}>{item}</Text>
          </Pressable>
        )}
        style={styles.chipRow}
      />

      {lessons.length > 0 && (
        <>
          <Text style={styles.label}>Topic</Text>
          {lessons.map((l) => (
            <Pressable
              key={l.id}
              style={[styles.lesson, lessonId === l.id && styles.lessonActive]}
              onPress={() => setLessonId(l.id)}
            >
              <Text style={styles.lessonTitle}>{l.title}</Text>
              <Text style={styles.lessonRule}>{l.rule}</Text>
            </Pressable>
          ))}
        </>
      )}

      <Pressable style={styles.btnPrimary} onPress={startLesson} disabled={loading}>
        <Text style={styles.btnText}>▶ Start lesson</Text>
      </Pressable>

      {teacherText ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Teacher</Text>
          <Text>{teacherText}</Text>
        </View>
      ) : null}

      <TextInput
        style={styles.input}
        placeholder="Type a sentence..."
        value={input}
        onChangeText={setInput}
      />
      <Pressable style={styles.btnSecondary} onPress={() => practice(input)} disabled={loading}>
        <Text style={styles.btnTextDark}>Send text</Text>
      </Pressable>

      <Pressable
        style={[styles.mic, isRecording && styles.micActive]}
        onPress={handleMic}
        disabled={loading}
      >
        <Text style={styles.micText}>{isRecording ? '🎤 Stop' : '🎤 Speak'}</Text>
      </Pressable>

      {loading && <ActivityIndicator style={{ marginTop: 12 }} color={COLORS.primary} />}

      {feedback ? (
        <View style={[styles.card, styles.feedback]}>
          {score != null && <Text style={styles.score}>Grammar: {Math.round(score)}/100</Text>}
          <Text>{feedback}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: 16, paddingBottom: 40 },
  title: { fontSize: 22, fontWeight: '700', color: COLORS.text },
  sub: { color: COLORS.textMuted, marginBottom: 16 },
  label: { fontWeight: '600', marginBottom: 8, marginTop: 8 },
  chipRow: { marginBottom: 8 },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: COLORS.card, marginRight: 8, borderWidth: 1, borderColor: COLORS.border },
  chipActive: { backgroundColor: COLORS.primary },
  chipText: { color: COLORS.text },
  chipTextActive: { color: '#fff', fontWeight: '700' },
  lesson: { padding: 12, borderRadius: 12, backgroundColor: COLORS.card, marginBottom: 8, borderWidth: 1, borderColor: COLORS.border },
  lessonActive: { borderColor: COLORS.primary, borderWidth: 2 },
  lessonTitle: { fontWeight: '600' },
  lessonRule: { fontSize: 12, color: COLORS.textMuted, marginTop: 4 },
  btnPrimary: { backgroundColor: '#f59e0b', padding: 14, borderRadius: 12, alignItems: 'center', marginTop: 12 },
  btnSecondary: { backgroundColor: COLORS.card, padding: 12, borderRadius: 12, alignItems: 'center', marginTop: 8, borderWidth: 1, borderColor: COLORS.border },
  btnText: { color: '#fff', fontWeight: '700' },
  btnTextDark: { fontWeight: '600' },
  card: { backgroundColor: COLORS.card, padding: 14, borderRadius: 12, marginTop: 12, borderWidth: 1, borderColor: COLORS.border },
  cardTitle: { fontWeight: '700', marginBottom: 6, color: COLORS.primary },
  feedback: { borderColor: '#86efac' },
  score: { fontWeight: '700', color: '#15803d', marginBottom: 6 },
  input: { borderWidth: 1, borderColor: COLORS.border, borderRadius: 12, padding: 12, marginTop: 12, backgroundColor: '#fff' },
  mic: { backgroundColor: '#22c55e', padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 12 },
  micActive: { backgroundColor: '#ef4444' },
  micText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
