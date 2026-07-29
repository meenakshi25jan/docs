import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '@/lib/api';
import { COLORS } from '@/constants';

interface DashboardData {
  learner: { current_cefr: string; ielts_estimate: number; pte_estimate: number };
  skill_scores: Record<string, number>;
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
    </View>
  );
}

function SkillBar({ label, score }: { label: string; score: number }) {
  return (
    <View style={styles.skillRow}>
      <Text style={styles.skillLabel}>{label}</Text>
      <View style={styles.skillTrack}>
        <View style={[styles.skillFill, { width: `${Math.min(score, 100)}%` }]} />
      </View>
      <Text style={styles.skillScore}>{score}</Text>
    </View>
  );
}

export default function HomeScreen() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const res = (await api.dashboard.student()) as DashboardData;
      setData(res);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const scores = data?.skill_scores || {
    grammar: 0, vocabulary: 0, writing: 0, reading: 0, listening: 0, speaking: 0,
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
    >
      {loading && !data ? (
        <ActivityIndicator style={{ marginTop: 40 }} color={COLORS.primary} />
      ) : (
        <>
          <View style={styles.statsRow}>
            <StatCard label="CEFR" value={data?.learner.current_cefr || '—'} color={COLORS.primary} />
            <StatCard label="IELTS" value={data?.learner.ielts_estimate?.toFixed(1) || '—'} color="#7c3aed" />
            <StatCard label="PTE" value={data?.learner.pte_estimate?.toString() || '—'} color="#0891b2" />
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Skill scores</Text>
            {Object.entries(scores).map(([skill, score]) => (
              <SkillBar key={skill} label={skill.charAt(0).toUpperCase() + skill.slice(1)} score={score} />
            ))}
          </View>

          <View style={styles.actions}>
            <Pressable style={styles.actionBtn} onPress={() => router.push('/(tabs)/practice')}>
              <Text style={styles.actionBtnText}>Start AI Practice</Text>
            </Pressable>
            <Pressable style={[styles.actionBtn, styles.actionBtnOutline]} onPress={() => router.push('/(tabs)/assessment')}>
              <Text style={[styles.actionBtnText, styles.actionBtnTextOutline]}>Take Assessment</Text>
            </Pressable>
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background, padding: 16 },
  statsRow: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  statCard: { flex: 1, backgroundColor: COLORS.card, borderRadius: 12, padding: 14, borderWidth: 1, borderColor: COLORS.border },
  statLabel: { fontSize: 12, color: COLORS.textMuted, marginBottom: 4 },
  statValue: { fontSize: 22, fontWeight: '700' },
  card: { backgroundColor: COLORS.card, borderRadius: 12, padding: 16, borderWidth: 1, borderColor: COLORS.border, marginBottom: 16 },
  cardTitle: { fontSize: 16, fontWeight: '600', marginBottom: 12, color: COLORS.text },
  skillRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 10, gap: 8 },
  skillLabel: { width: 80, fontSize: 13, color: COLORS.textMuted, textTransform: 'capitalize' },
  skillTrack: { flex: 1, height: 8, backgroundColor: COLORS.border, borderRadius: 4, overflow: 'hidden' },
  skillFill: { height: 8, backgroundColor: COLORS.primary, borderRadius: 4 },
  skillScore: { width: 28, fontSize: 13, fontWeight: '600', textAlign: 'right' },
  actions: { gap: 12, marginBottom: 32 },
  actionBtn: { backgroundColor: COLORS.primary, borderRadius: 12, padding: 16, alignItems: 'center' },
  actionBtnOutline: { backgroundColor: COLORS.card, borderWidth: 2, borderColor: COLORS.primary },
  actionBtnText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  actionBtnTextOutline: { color: COLORS.primary },
});
