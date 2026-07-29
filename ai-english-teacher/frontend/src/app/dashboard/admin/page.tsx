'use client';

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-bold text-primary">Admin Dashboard</h1>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Users', value: '12,450', change: '+8%' },
            { label: 'Active Tenants', value: '34', change: '+2' },
            { label: 'AI Calls Today', value: '8,234', change: '+15%' },
            { label: 'System Uptime', value: '99.97%', change: '' },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-xl p-5 border">
              <p className="text-sm text-gray-500">{s.label}</p>
              <p className="text-3xl font-bold">{s.value}</p>
              {s.change && <p className="text-xs text-green-600 mt-1">{s.change}</p>}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl p-6 border">
            <h2 className="font-semibold mb-4">System Health</h2>
            <div className="space-y-3">
              {['API Gateway', 'PostgreSQL', 'Redis', 'Azure OpenAI', 'Azure Speech'].map((svc) => (
                <div key={svc} className="flex items-center justify-between">
                  <span className="text-sm">{svc}</span>
                  <span className="flex items-center gap-2 text-sm text-green-600">
                    <span className="w-2 h-2 bg-green-500 rounded-full" /> Healthy
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border">
            <h2 className="font-semibold mb-4">Tenant Overview</h2>
            <div className="space-y-3">
              {[
                { name: 'Acme Corp', tier: 'Enterprise', users: 450 },
                { name: 'Language School A', tier: 'Pro', users: 120 },
                { name: 'Default', tier: 'Free', users: 890 },
              ].map((t) => (
                <div key={t.name} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="font-medium text-sm">{t.name}</p>
                    <p className="text-xs text-gray-500">{t.tier}</p>
                  </div>
                  <span className="text-sm">{t.users} users</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
