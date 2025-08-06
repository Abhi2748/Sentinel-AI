import { useState } from 'react'
import { 
  Settings as SettingsIcon, 
  Key, 
  Database, 
  Shield,
  Save,
  Trash2
} from 'lucide-react'

interface ProviderConfig {
  id: string
  name: string
  type: 'openai' | 'anthropic' | 'groq'
  apiKey: string
  model: string
  isActive: boolean
}

const mockProviders: ProviderConfig[] = [
  {
    id: '1',
    name: 'OpenAI Production',
    type: 'openai',
    apiKey: 'sk-...',
    model: 'gpt-4',
    isActive: true,
  },
  {
    id: '2',
    name: 'Anthropic Claude',
    type: 'anthropic',
    apiKey: 'sk-ant-...',
    model: 'claude-3-sonnet',
    isActive: true,
  },
  {
    id: '3',
    name: 'Groq Fast',
    type: 'groq',
    apiKey: 'gsk_...',
    model: 'llama-3-8b',
    isActive: false,
  },
]

export default function Settings() {
  const [providers, setProviders] = useState<ProviderConfig[]>(mockProviders)
  const [activeTab, setActiveTab] = useState('providers')

  const tabs = [
    { id: 'providers', name: 'Providers', icon: Key },
    { id: 'budget', name: 'Budget', icon: Database },
    { id: 'security', name: 'Security', icon: Shield },
  ]

  const handleToggleProvider = (id: string) => {
    setProviders(prev => 
      prev.map(p => 
        p.id === id ? { ...p, isActive: !p.isActive } : p
      )
    )
  }

  const handleDeleteProvider = (id: string) => {
    setProviders(prev => prev.filter(p => p.id !== id))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Settings</h1>
        <p className="mt-2 text-secondary-600">
          Configure your Sentinel-AI instance
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-secondary-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'providers' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-medium text-secondary-900">AI Providers</h2>
            <button className="btn-primary">
              <Key className="h-4 w-4 mr-2" />
              Add Provider
            </button>
          </div>

          <div className="space-y-4">
            {providers.map((provider) => (
              <div key={provider.id} className="card">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${
                      provider.isActive ? 'bg-green-500' : 'bg-secondary-300'
                    }`} />
                    <div>
                      <h3 className="font-medium text-secondary-900">{provider.name}</h3>
                      <p className="text-sm text-secondary-500">
                        {provider.type} • {provider.model}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleProvider(provider.id)}
                      className={`px-3 py-1 rounded text-sm font-medium ${
                        provider.isActive
                          ? 'bg-green-100 text-green-800'
                          : 'bg-secondary-100 text-secondary-800'
                      }`}
                    >
                      {provider.isActive ? 'Active' : 'Inactive'}
                    </button>
                    <button className="p-2 text-secondary-400 hover:text-secondary-600">
                      <SettingsIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteProvider(provider.id)}
                      className="p-2 text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'budget' && (
        <div className="space-y-6">
          <h2 className="text-lg font-medium text-secondary-900">Budget Configuration</h2>
          
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="card">
              <h3 className="font-medium text-secondary-900 mb-4">User Budget</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Daily Limit
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="0.00"
                    defaultValue="10.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Monthly Limit
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="0.00"
                    defaultValue="100.00"
                  />
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="font-medium text-secondary-900 mb-4">Team Budget</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Daily Limit
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="0.00"
                    defaultValue="50.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Monthly Limit
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="0.00"
                    defaultValue="500.00"
                  />
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="font-medium text-secondary-900 mb-4">Company Budget</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Daily Limit
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="0.00"
                    defaultValue="200.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Monthly Limit
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="0.00"
                    defaultValue="2000.00"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button className="btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Budget Settings
            </button>
          </div>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-6">
          <h2 className="text-lg font-medium text-secondary-900">Security Settings</h2>
          
          <div className="card">
            <h3 className="font-medium text-secondary-900 mb-4">Authentication</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-secondary-900">JWT Token Expiry</p>
                  <p className="text-sm text-secondary-500">Token expiration time</p>
                </div>
                <select className="input-field w-32">
                  <option>1 hour</option>
                  <option>24 hours</option>
                  <option>7 days</option>
                  <option>30 days</option>
                </select>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-secondary-900">Rate Limiting</p>
                  <p className="text-sm text-secondary-500">Requests per minute per user</p>
                </div>
                <input
                  type="number"
                  className="input-field w-32"
                  defaultValue="60"
                />
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="font-medium text-secondary-900 mb-4">Data Protection</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-secondary-900">PII Redaction</p>
                  <p className="text-sm text-secondary-500">Automatically redact personal data</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-secondary-900">Audit Logging</p>
                  <p className="text-sm text-secondary-500">Log all requests for compliance</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}