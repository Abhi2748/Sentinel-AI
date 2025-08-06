import { 
  BarChart3, 
  TrendingUp, 
  DollarSign, 
  Zap,
  Clock,
  Activity
} from 'lucide-react'

const metrics = [
  {
    name: 'Total Requests',
    value: '12,847',
    change: '+12%',
    icon: Activity,
  },
  {
    name: 'Cost Savings',
    value: '$2,847',
    change: '+23%',
    icon: DollarSign,
  },
  {
    name: 'Cache Hit Rate',
    value: '78.2%',
    change: '+5.1%',
    icon: Zap,
  },
  {
    name: 'Avg Response Time',
    value: '1.2s',
    change: '-0.3s',
    icon: Clock,
  },
]

const providerStats = [
  { name: 'OpenAI', requests: 5847, cost: 1247, success: 98.2 },
  { name: 'Anthropic', requests: 3247, cost: 892, success: 97.8 },
  { name: 'Groq', requests: 3753, cost: 708, success: 99.1 },
]

const timeData = [
  { time: '00:00', requests: 45, cost: 12.3 },
  { time: '04:00', requests: 32, cost: 8.7 },
  { time: '08:00', requests: 89, cost: 24.1 },
  { time: '12:00', requests: 156, cost: 42.8 },
  { time: '16:00', requests: 134, cost: 36.9 },
  { time: '20:00', requests: 78, cost: 21.4 },
]

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Analytics</h1>
        <p className="mt-2 text-secondary-600">
          Detailed performance metrics and insights
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div key={metric.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <metric.icon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">{metric.name}</p>
                <p className="text-2xl font-semibold text-secondary-900">{metric.value}</p>
                <p className="text-sm text-green-600">{metric.change}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Provider Performance */}
      <div className="card">
        <h3 className="text-lg font-medium text-secondary-900 mb-4">Provider Performance</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-secondary-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Provider
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Success Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-secondary-200">
              {providerStats.map((provider) => (
                <tr key={provider.name}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">
                    {provider.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    {provider.requests.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    ${provider.cost.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    {provider.success}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Time Series Chart Placeholder */}
      <div className="card">
        <h3 className="text-lg font-medium text-secondary-900 mb-4">Request Volume Over Time</h3>
        <div className="h-64 bg-secondary-50 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-secondary-400 mx-auto mb-2" />
            <p className="text-secondary-500">Chart component would be implemented here</p>
            <p className="text-sm text-secondary-400">Using Recharts or similar library</p>
          </div>
        </div>
      </div>

      {/* Cache Performance */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="text-lg font-medium text-secondary-900 mb-4">Cache Performance</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-secondary-600">L1 Cache Hit Rate</span>
              <span className="text-sm font-medium text-secondary-900">45.2%</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '45.2%' }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-secondary-600">L2 Cache Hit Rate</span>
              <span className="text-sm font-medium text-secondary-900">78.1%</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78.1%' }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-secondary-600">L3 Cache Hit Rate</span>
              <span className="text-sm font-medium text-secondary-900">92.3%</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '92.3%' }}></div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-secondary-900 mb-4">Cost Breakdown</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-secondary-600">OpenAI</span>
              <span className="text-sm font-medium text-secondary-900">$1,247</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: '44%' }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-secondary-600">Anthropic</span>
              <span className="text-sm font-medium text-secondary-900">$892</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div className="bg-orange-500 h-2 rounded-full" style={{ width: '31%' }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-secondary-600">Groq</span>
              <span className="text-sm font-medium text-secondary-900">$708</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '25%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}