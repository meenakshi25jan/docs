import { useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api } from '@/lib/api';
import { COLORS } from '@/constants';

export default function AssessmentScreen() {
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [answers, setAnswers] = useState({
    grammar: 'She has been working here for five years.',
    vocabulary: 'The implementation of sustainable practices is crucial for environmental preservation.',
    writing: 'Technology has significantly transformed modern education by providing access to vast resources.',
  });
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  async function startAssessment() {
    setLoading(true);
    try {
      const res = (await api.assessments.create({ assessment_type: 'full' })) as { id: string };
      setAssessmentId(res.id);
      setResults(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start assessment');
    } finally {
      setLoading(false);
    }
  }

  async function submitAssessment() {
    if (!assessmentId) return;
    setLoading(true);
    try {
      const res = await api.assessments.submit(assessmentId, [
        { skill: 'grammar', question_id: 'g1', response: answers.grammar },
        { skill: 'vocabulary', question_id: 'v1', response: answers.vocabulary },
        { skill: 'writing', question_id: 'w1', response: answers.writing },
      ]);
      setResults(res as Record<string, unknown>);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Submit failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {!assessmentId ? (
        <View style={styles.card}>
          <Text style={styles.title}>Placement Assessment</Text>
          <Text style={styles.desc}>
            Test your grammar, vocabulary, and writing. Get CEFR, IELTS, and PTE estimates.
          </Text>
          <Pressable style={styles.btn} onPress={startAssessment} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Start Assessment</Text>}
          </Pressable>
        </View>
      ) : !results ? (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Grammar</Text>
          <Text style={styles.prompt}>Correct: &quot;She have been working here for five year.&quot;</Text>
          <TextInput
            style={styles.textarea}
            multiline
            value={answers.grammar}
            onChangeText={(v) => setAnswers({ ...answers, grammar: v })}
          />

          <Text style={styles.sectionTitle}>Vocabulary</Text>
          <Text style={styles.prompt}>Use &quot;nevertheless&quot; in a sentence:</Text>
          <TextInput
            style={styles.textarea}
            multiline
            value={answers.vocabulary}
            onChangeText={(v) => setAnswers({ ...answers, vocabulary: v })}
          />

          <Text style={styles.sectionTitle}>Writing</Text>
          <Text style={styles.prompt}>Write about how technology changed education (2–3 sentences):</Text>
          <TextInput
            style={[styles.textarea, { height: 100 }]}
            multiline
            value={answers.writing}
            onChangeText={(v) => setAnswers({ ...answers, writing: v })}
          />

          <Pressable style={styles.btn} onPress={submitAssessment} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Submit</Text>}
          </Pressable>
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.title}>Your Results</Text>
          <Text style={styles.resultLine}>CEFR: {(results as { cefr_estimate?: string }).cefr_estimate || '—'}</Text>
          <Text style={styles.resultLine}>IELTS: {(results as { ielts_estimate?: number }).ielts_estimate ?? '—'}</Text>
          <Text style={styles.resultLine}>PTE: {(results as { pte_estimate?: number }).pte_estimate ?? '—'}</Text>
          <Pressable style={[styles.btn, { marginTop: 16 }]} onPress={() => { setAssessmentId(null); setResults(null); }}>
            <Text style={styles.btnText}>Take again</Text>
          </Pressable>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: 16 },
  card: { backgroundColor: COLORS.card, borderRadius: 12, padding: 16, borderWidth: 1, borderColor: COLORS.border },
  title: { fontSize: 20, fontWeight: '700', color: COLORS.text, marginBottom: 8 },
  desc: { fontSize: 14, color: COLORS.textMuted, marginBottom: 20, lineHeight: 20 },
  sectionTitle: { fontSize: 16, fontWeight: '600', marginTop: 12, marginBottom: 6, color: COLORS.text },
  prompt: { fontSize: 13, color: COLORS.textMuted, marginBottom: 8 },
  textarea: { borderWidth: 1, borderColor: COLORS.border, borderRadius: 10, padding: 12, minHeight: 80, fontSize: 15, textAlignVertical: 'top' },
  btn: { backgroundColor: COLORS.primary, borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 20 },
  btnText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  resultLine: { fontSize: 18, marginBottom: 8, color: COLORS.text },
});
