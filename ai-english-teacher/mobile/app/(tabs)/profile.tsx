import { useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '@/lib/auth';
import { API_URL, COLORS } from '@/constants';

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace('/login');
  }

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Profile</Text>
        <Text style={styles.label}>Name</Text>
        <Text style={styles.value}>{user?.first_name} {user?.last_name}</Text>
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user?.email}</Text>
        <Text style={styles.label}>Role</Text>
        <Text style={styles.value}>{user?.role || 'student'}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>API Server</Text>
        <Text style={styles.apiUrl}>{API_URL}</Text>
      </View>

      <Pressable style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={styles.logoutText}>Log out</Text>
      </Pressable>

      <Text style={styles.version}>AI English Teacher v1.0.0</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background, padding: 16 },
  card: { backgroundColor: COLORS.card, borderRadius: 12, padding: 16, borderWidth: 1, borderColor: COLORS.border, marginBottom: 16 },
  title: { fontSize: 20, fontWeight: '700', color: COLORS.text, marginBottom: 16 },
  label: { fontSize: 12, color: COLORS.textMuted, marginTop: 8 },
  value: { fontSize: 16, color: COLORS.text, fontWeight: '500' },
  apiUrl: { fontSize: 12, color: COLORS.textMuted, marginTop: 4 },
  logoutBtn: { backgroundColor: COLORS.error, borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 8 },
  logoutText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  version: { textAlign: 'center', color: COLORS.textMuted, fontSize: 12, marginTop: 24 },
});
