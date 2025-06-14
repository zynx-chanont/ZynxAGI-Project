import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { Activity, Cpu, Zap, Brain, Globe, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react';

const ZynxAGIDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [healthScore, setHealthScore] = useState(95);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  // WebSocket connection for real-time data
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket('ws://localhost:8001/ws/metrics');
        
        wsRef.current.onopen = () => {
          setIsConnected(true);
          console.log('🚀 Connected to Zynx AGI Monitor');
        };
        
        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          setMetrics(data);
          
          // Update history (keep last 50 points)
          setHistory(prev => {
            const newHistory = [...prev, {
              time: new Date(data.timestamp).toLocaleTimeString(),
              inference_time: data.inference_time_ms,
              gpu_util: data.gpu_utilization,
              cultural_score: data.cultural_accuracy_score * 100,
              tokens_per_sec: data.tokens_per_second
            }].slice(-50);
            return newHistory;
          });
          
          // Update health score
          setHealthScore(85 + Math.random() * 15); // Mock calculation
        };
        
        wsRef.current.onclose = () => {
          setIsConnected(false);
          setTimeout(connectWebSocket, 3000); // Reconnect after 3s
        };
        
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        // Fallback to mock data
        generateMockData();
      }
    };

    // Generate mock data if WebSocket fails
    const generateMockData = () => {
      const mockMetrics = {
        timestamp: new Date().toISOString(),
        cpu_percent: 45 + Math.random() * 20,
        memory_percent: 60 + Math.random() * 15,
        gpu_utilization: 75 + Math.random() * 20,
        gpu_memory_used: 70 + Math.random() * 15,
        gpu_temperature: 65 + Math.random() * 10,
        inference_time_ms: 450 + Math.random() * 100,
        tokens_per_second: 50 + Math.random() * 15,
        queue_depth: Math.floor(Math.random() * 8),
        response_quality_score: 0.85 + Math.random() * 0.13,
        cultural_accuracy_score: 0.90 + Math.random() * 0.08,
        emotional_intelligence_score: 0.87 + Math.random() * 0.10,
        thai_language_proficiency: 0.92 + Math.random() * 0.07,
        success_rate: 0.95 + Math.random() * 0.04,
        uptime_seconds: 86400 + Math.random() * 3600
      };
      
      setMetrics(mockMetrics);
      setHistory(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        inference_time: mockMetrics.inference_time_ms,
        gpu_util: mockMetrics.gpu_utilization,
        cultural_score: mockMetrics.cultural_accuracy_score * 100,
        tokens_per_sec: mockMetrics.tokens_per_second
      }].slice(-50));
    };

    connectWebSocket();
    
    // Mock data interval as fallback
    const mockInterval = setInterval(generateMockData, 5000);

    return () => {
      if (wsRef.current) wsRef.current.close();
      clearInterval(mockInterval);
    };
  }, []);

  const MetricCard = ({ title, value, unit, icon: Icon, status = 'normal', trend }) => {
    const statusColors = {
      normal: 'bg-green-50 border-green-200 text-green-800',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      critical: 'bg-red-50 border-red-200 text-red-800'
    };

    return (
      <div className={`p-4 rounded-lg border-2 ${statusColors[status]} transition-all duration-300`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className="w-5 h-5" />
            <span className="font-medium text-sm">{title}</span>
          </div>
          {trend && (
            <TrendingUp className={`w-4 h-4 ${trend > 0 ? 'text-green-600' : 'text-red-600'} ${trend > 0 ? '' : 'transform rotate-180'}`} />
          )}
        </div>
        <div className="mt-2">
          <span className="text-2xl font-bold">{value}</span>
          <span className="text-sm ml-1">{unit}</span>
        </div>
      </div>
    );
  };

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (!metrics) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-16 h-16 mx-auto mb-4 animate-pulse text-blue-400" />
          <h2 className="text-xl font-semibold mb-2">กำลังเชื่อมต่อ Zynx AGI Engine...</h2>
          <p className="text-gray-400">Initializing Arc Reactor monitoring systems</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
              Zynx AGI Engine Monitor
            </h1>
            <p className="text-gray-400 mt-1">Real-time Arc Reactor performance tracking</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${isConnected ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-400">{healthScore.toFixed(1)}%</div>
              <div className="text-sm text-gray-400">Health Score</div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Inference Time"
          value={metrics.inference_time_ms?.toFixed(0)}
          unit="ms"
          icon={Clock}
          status={metrics.inference_time_ms > 600 ? 'warning' : 'normal'}
        />
        <MetricCard
          title="GPU Utilization"
          value={metrics.gpu_utilization?.toFixed(1)}
          unit="%"
          icon={Zap}
          status={metrics.gpu_utilization > 90 ? 'critical' : metrics.gpu_utilization > 80 ? 'warning' : 'normal'}
        />
        <MetricCard
          title="Cultural Accuracy"
          value={(metrics.cultural_accuracy_score * 100)?.toFixed(1)}
          unit="%"
          icon={Globe}
          status={metrics.cultural_accuracy_score < 0.85 ? 'warning' : 'normal'}
        />
        <MetricCard
          title="Tokens/Second"
          value={metrics.tokens_per_second?.toFixed(0)}
          unit="tok/s"
          icon={Brain}
          status='normal'
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Performance Timeline */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-400" />
            Inference Performance
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#E5E7EB' }}
              />
              <Line type="monotone" dataKey="inference_time" stroke="#3B82F6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* GPU Utilization */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-yellow-400" />
            GPU Utilization
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#E5E7EB' }}
              />
              <Area type="monotone" dataKey="gpu_util" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Quality Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Cultural Intelligence */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-green-400" />
            Deeja Cultural Intelligence
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Cultural Accuracy</span>
                <span>{(metrics.cultural_accuracy_score * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-400 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${metrics.cultural_accuracy_score * 100}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Emotional Intelligence</span>
                <span>{(metrics.emotional_intelligence_score * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-400 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${metrics.emotional_intelligence_score * 100}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Thai Language Proficiency</span>
                <span>{(metrics.thai_language_proficiency * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-purple-400 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${metrics.thai_language_proficiency * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
            System Health
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span>Success Rate</span>
              <span className="text-green-400">{(metrics.success_rate * 100).toFixed(2)}%</span>
            </div>
            <div className="flex justify-between">
              <span>Queue Depth</span>
              <span className={metrics.queue_depth > 5 ? 'text-yellow-400' : 'text-green-400'}>
                {metrics.queue_depth} requests
              </span>
            </div>
            <div className="flex justify-between">
              <span>Memory Usage</span>
              <span className={metrics.memory_percent > 80 ? 'text-yellow-400' : 'text-green-400'}>
                {metrics.memory_percent?.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Uptime</span>
              <span className="text-blue-400">{formatUptime(metrics.uptime_seconds)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2 text-purple-400" />
          AI-Powered Optimization Recommendations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {metrics.inference_time_ms > 600 && (
            <div className="bg-yellow-900 bg-opacity-50 border border-yellow-600 rounded-lg p-4">
              <AlertTriangle className="w-5 h-5 text-yellow-400 mb-2" />
              <h4 className="font-medium text-yellow-400">High Latency Detected</h4>
              <p className="text-sm text-yellow-300 mt-1">Consider model quantization or GPU scaling</p>
            </div>
          )}
          {metrics.gpu_utilization > 90 && (
            <div className="bg-red-900 bg-opacity-50 border border-red-600 rounded-lg p-4">
              <AlertTriangle className="w-5 h-5 text-red-400 mb-2" />
              <h4 className="font-medium text-red-400">GPU Bottleneck</h4>
              <p className="text-sm text-red-300 mt-1">Scale horizontal GPU infrastructure</p>
            </div>
          )}
          <div className="bg-green-900 bg-opacity-50 border border-green-600 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-green-400 mb-2" />
            <h4 className="font-medium text-green-400">Optimal Performance</h4>
            <p className="text-sm text-green-300 mt-1">Zynx AGI Engine running smoothly</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ZynxAGIDashboard;