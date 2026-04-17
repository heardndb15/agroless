import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Tractor, TrendingUp, CloudRain, DollarSign, BrainCircuit } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7'];

const Dashboard = () => {
  const [data, setData] = useState({
    total_revenue: 0,
    total_expenses: 0,
    profit: 0,
    roi: 0,
    expense_by_category: {}
  });

  const [aiResponse, setAiResponse] = useState('');
  const [question, setQuestion] = useState('');

  useEffect(() => {
    // В реальном приложении здесь будет запрос к axios:
    // axios.get(`${API_URL}/dashboard`).then(res => setData(res.data));
    
    // Заглушка для демонстрации
    setData({
      total_revenue: 154000,
      total_expenses: 62000,
      profit: 92000,
      roi: 148.4,
      expense_by_category: {
        'Удобрения': 20000,
        'ГСМ': 15000,
        'Семена': 12000,
        'Зарплата': 10000,
        'Ремонт': 5000
      }
    });
  }, []);

  const handleAskAi = async () => {
    if (!question) return;
    setAiResponse('Загрузка...');
    try {
      // Имитация работы с серверным эндпоинтом /api/analytics/ai
      setTimeout(() => {
        setAiResponse('По вашим данным, рентабельность превосходная (ROI > 140%). Рекомендую обратить внимание на расходы на удобрения — они составляют 32% от общих затрат. Прогноз погоды от Open-Meteo на следующую неделю: ожидаются дожди, оптимальное время для посева.');
      }, 1200);
    } catch (e) {
      setAiResponse('Ошибка соединения с ИИ.');
    }
  };

  const pieData = Object.entries(data.expense_by_category).map(([name, value]) => ({ name, value }));

  const harvestData = [
    { name: '2019', yield: 400 },
    { name: '2020', yield: 300 },
    { name: '2021', yield: 550 },
    { name: '2022', yield: 480 },
    { name: '2023', yield: 600 },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-gray-800">
      <header className="flex items-center justify-between pb-6 border-b border-green-200">
        <div className="flex items-center space-x-3 text-green-700">
          <Tractor size={32} />
          <h1 className="text-3xl font-bold">AgroLess</h1>
        </div>
        <div className="text-sm font-medium text-green-800 bg-green-200 px-3 py-1 rounded-full">
          Панель управления фермой
        </div>
      </header>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-lg"><DollarSign /></div>
          <div>
            <div className="text-sm text-gray-500">Выручка сезона</div>
            <div className="text-xl font-bold">{data.total_revenue.toLocaleString()} ₸</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-red-100 text-red-600 rounded-lg"><TrendingUp className="rotate-180" /></div>
          <div>
            <div className="text-sm text-gray-500">Всего расходов</div>
            <div className="text-xl font-bold">{data.total_expenses.toLocaleString()} ₸</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg"><TrendingUp /></div>
          <div>
            <div className="text-sm text-gray-500">Чистая прибыль</div>
            <div className="text-xl font-bold">{data.profit.toLocaleString()} ₸</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-purple-100 text-purple-600 rounded-lg"><CloudRain /></div>
          <div>
            <div className="text-sm text-gray-500">Погода (7 дней)</div>
            <div className="text-lg font-bold text-green-600">Благоприятно</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Charts */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold mb-4">Урожайность (тонны)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={harvestData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="yield" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold mb-4">Структура расходов</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value} ₸`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Assistant */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-indigo-100 bg-gradient-to-br from-indigo-50 to-white">
        <div className="flex items-center space-x-2 mb-4">
          <BrainCircuit className="text-indigo-600" />
          <h2 className="text-lg font-semibold text-indigo-900">ИИ Агроном (Google Gemini)</h2>
        </div>
        <div className="flex space-x-2">
          <input 
            type="text" 
            className="flex-1 p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Спросите: Как мне оптимизировать расходы на удобрения для пшеницы?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAskAi()}
          />
          <button 
            onClick={handleAskAi}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition shadow-sm font-medium"
          >
            Спросить
          </button>
        </div>
        {aiResponse && (
          <div className="mt-4 p-4 bg-indigo-50 text-indigo-900 border border-indigo-100 rounded-lg text-sm leading-relaxed">
            {aiResponse}
          </div>
        )}
      </div>

    </div>
  );
};

export default Dashboard;
