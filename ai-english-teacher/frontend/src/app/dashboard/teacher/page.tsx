'use client';

export default function TeacherDashboard() {
  const learners = [
    { name: 'Jane Doe', cefr: 'B2', ielts: 6.5, progress: 78, status: 'on_track' },
    { name: 'John Smith', cefr: 'B1', ielts: 5.5, progress: 62, status: 'needs_attention' },
    { name: 'Maria Garcia', cefr: 'C1', ielts: 7.5, progress: 88, status: 'on_track' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-bold text-primary">Teacher Dashboard</h1>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Class Size', value: '24' },
            { label: 'Active Learners', value: '18' },
            { label: 'Avg IELTS', value: '6.2' },
            { label: 'Assessments This Week', value: '42' },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-xl p-5 border">
              <p className="text-sm text-gray-500">{s.label}</p>
              <p className="text-3xl font-bold">{s.value}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="font-semibold">Learner Overview</h2>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">Name</th>
                <th className="px-6 py-3 text-left">CEFR</th>
                <th className="px-6 py-3 text-left">IELTS</th>
                <th className="px-6 py-3 text-left">Progress</th>
                <th className="px-6 py-3 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {learners.map((l) => (
                <tr key={l.name} className="border-t">
                  <td className="px-6 py-3 font-medium">{l.name}</td>
                  <td className="px-6 py-3">{l.cefr}</td>
                  <td className="px-6 py-3">{l.ielts}</td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-100 rounded-full">
                        <div className="h-2 bg-primary rounded-full" style={{ width: `${l.progress}%` }} />
                      </div>
                      <span>{l.progress}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      l.status === 'on_track' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {l.status === 'on_track' ? 'On Track' : 'Needs Attention'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
