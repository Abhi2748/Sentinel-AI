import { 
  Activity, 
  DollarSign, 
  Zap, 
  TrendingUp,
  MessageSquare,
  Clock,
  BarChart3,
  Settings
} from 'lucide-react'

const stats = [
  {
    name: 'Total Requests',
    value: '12,847',
    change: '+12%',
    changeType: 'positive',
    icon: MessageSquare,
  },
  {
    name: 'Cost Savings',
    value: '$2,847',
    change: '+23%',
    changeType: 'positive',
    icon: DollarSign,
  },
  {
    name: 'Cache Hit Rate',
    value: '78.2%',
    change: '+5.1%',
    changeType: 'positive',
    icon: Zap,
  },
  {
    name: 'Avg Response Time',
    value: '1.2s',
    change: '-0.3s',
    changeType: 'positive',
    icon: Clock,
  },
]

const recentActivity = [
  {
    id: 1,
    type: 'request',
    message: 'AI request processed via OpenAI GPT-4',
    time: '2 minutes ago',
    cost: '$0.023',
  },
  {
    id: 2,
    type: 'cache',
    message: 'Cache hit on L2 for similar prompt',
    time: '5 minutes ago',
    cost: '$0.001',
  },
  {
    id: 3,
    type: 'budget',
    message: 'Team budget alert: 85% used',
    time: '10 minutes ago',
    cost: null,
  },
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
        <p className="mt-2 text-secondary-600">
          Overview of your AI routing performance and metrics
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-secondary-900">{stat.value}</p>
                <p className={`text-sm ${
                  stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.change}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-medium text-secondary-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  activity.type === 'request' ? 'bg-blue-500' :
                  activity.type === 'cache' ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
                <div>
                  <p className="text-sm font-medium text-secondary-900">{activity.message}</p>
                  <p className="text-xs text-secondary-500">{activity.time}</p>
                </div>
              </div>
              {activity.cost && (
                <span className="text-sm text-secondary-600">{activity.cost}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <button className="card hover:shadow-lg transition-shadow text-left">
          <div className="flex items-center space-x-3">
            <MessageSquare className="h-6 w-6 text-primary-600" />
            <div>
              <h4 className="font-medium text-secondary-900">New Chat</h4>
              <p className="text-sm text-secondary-600">Start a new AI conversation</p>
            </div>
          </div>
        </button>

        <button className="card hover:shadow-lg transition-shadow text-left">
          <div className="flex items-center space-x-3">
            <BarChart3 className="h-6 w-6 text-primary-600" />
            <div>
              <h4 className="font-medium text-secondary-900">View Analytics</h4>
              <p className="text-sm text-secondary-600">Detailed performance metrics</p>
            </div>
          </div>
        </button>

        <button className="card hover:shadow-lg transition-shadow text-left">
          <div className="flex items-center space-x-3">
            <Settings className="h-6 w-6 text-primary-600" />
            <div>
              <h4 className="font-medium text-secondary-900">Configure</h4>
              <p className="text-sm text-secondary-600">Manage providers and settings</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  )
}