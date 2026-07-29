import { Tabs } from 'expo-router';
import { COLORS } from '@/constants';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerStyle: { backgroundColor: COLORS.card },
        headerTintColor: COLORS.primary,
        headerTitleStyle: { fontWeight: '700' },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textMuted,
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Home', tabBarLabel: 'Home' }} />
      <Tabs.Screen name="practice" options={{ title: 'Practice', tabBarLabel: 'Practice' }} />
      <Tabs.Screen name="grammar" options={{ title: 'Grammar', tabBarLabel: 'Grammar' }} />
      <Tabs.Screen name="assessment" options={{ title: 'Assessment', tabBarLabel: 'Test' }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile', tabBarLabel: 'Profile' }} />
    </Tabs>
  );
}
