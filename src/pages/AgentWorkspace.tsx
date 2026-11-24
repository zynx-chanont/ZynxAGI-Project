import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Send, Plus, Download, Share2, Trash2, Save } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Analysis {
  clarity: number;
  specificity: number;
  structure: number;
  outcome: number;
  improvedPrompt: string;
  tips: string[];
}

export default function AgentWorkspace() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedPrompts, setSavedPrompts] = useState<Array<{ id: string; prompt: string; timestamp: Date }>>([]);
  const [showHistory, setShowHistory] = useState(false);

  const handleSendPrompt = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    setTimeout(() => {
      const mockAnalysis: Analysis = {
        clarity: Math.floor(Math.random() * 40) + 60,
        specificity: Math.floor(Math.random() * 40) + 60,
        structure: Math.floor(Math.random() * 40) + 60,
        outcome: Math.floor(Math.random() * 40) + 60,
        improvedPrompt: `Enhanced version of: "${inputValue}"`,
        tips: [
          'Be more specific about the desired outcome',
          'Include context and constraints',
          'Define the expected format of the response',
          'Add examples if applicable',
        ],
      };

      setAnalysis(mockAnalysis);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: 'Analysis complete! Check the results on the right.',
          timestamp: new Date(),
        },
      ]);
      setIsLoading(false);
    }, 1500);
  };

  const handleSavePrompt = () => {
    if (!inputValue.trim()) return;
    setSavedPrompts((prev) => [
      ...prev,
      { id: Date.now().toString(), prompt: inputValue, timestamp: new Date() },
    ]);
  };

  const handleExport = () => {
    if (!analysis) return;
    const exportData = {
      originalPrompt: messages.find((m) => m.type === 'user')?.content,
      analysis,
      timestamp: new Date().toISOString(),
    };
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `deeja-analysis-${Date.now()}.json`;
    link.click();
  };

  const averageScore = analysis && (analysis.clarity + analysis.specificity + analysis.structure + analysis.outcome) / 4;

  return (
    <div className="home-shell min-h-screen relative overflow-hidden">
      <div className="home-bg-pattern" aria-hidden="true" />

      <div className="relative z-10 min-h-screen flex flex-col">
        <header className="home-header px-4 py-4 sm:px-6 lg:px-8">
          <div className="home-container flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/deeja-favicon.png" alt="Deeja Logo" className="w-10 h-10 object-contain" />
              <div>
                <h1 className="home-title">Deeja Agent Workspace</h1>
                <p className="home-subtitle">Skill + Prompt Analyzer</p>
              </div>
            </div>

            <Button onClick={() => setShowHistory(!showHistory)} variant="outline" className="home-btn-secondary">
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
          </div>
        </header>

        <main className="flex-1 px-4 py-4 sm:px-6 sm:py-6 lg:px-8 lg:py-8">
          <div className="home-container home-grid">
            <section className="home-panel flex flex-col min-h-[420px]">
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center">
                    <img src="/deeja-favicon.png" alt="Deeja Character" className="w-36 h-36 sm:w-44 sm:h-44 object-contain mb-5" />
                    <h2 className="home-heading">Welcome to Deeja Agent Workspace</h2>
                    <p className="home-copy max-w-md">Paste your prompt for skill-style analysis, score breakdown, and improvement suggestions.</p>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs sm:max-w-sm px-4 py-3 rounded-xl ${msg.type === 'user' ? 'home-bubble-user' : 'home-bubble-ai'}`}>
                        <p className="text-sm">{msg.content}</p>
                        <p className="text-xs opacity-60 mt-1">{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                      </div>
                    </div>
                  ))
                )}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="home-bubble-ai px-4 py-3 rounded-xl">
                      <div className="flex gap-2">
                        <div className="w-2 h-2 rounded-full bg-neutral-400 animate-pulse" />
                        <div className="w-2 h-2 rounded-full bg-neutral-400 animate-pulse delay-100" />
                        <div className="w-2 h-2 rounded-full bg-neutral-400 animate-pulse delay-200" />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="border-t border-[var(--home-border)] p-4 sm:p-6 bg-[var(--home-surface-muted)]">
                <div className="flex gap-3">
                  <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendPrompt()}
                    placeholder="Paste your prompt here..."
                    className="home-input"
                  />
                  <Button onClick={handleSendPrompt} disabled={isLoading || !inputValue.trim()} className="home-btn-primary">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </section>

            {analysis && (
              <aside className="flex flex-col gap-4">
                <Card className="home-card p-5 sm:p-6">
                  <h3 className="text-lg font-semibold text-[var(--home-text)] mb-4">Analysis Results</h3>
                  <div className="home-score-box mb-6">
                    <p className="text-sm text-[var(--home-text-muted)] mb-1">Overall Score</p>
                    <p className="text-4xl font-semibold text-[var(--home-text)]">{Math.round(averageScore || 0)}/100</p>
                  </div>
                  <div className="space-y-3">
                    {[{ label: 'Clarity', value: analysis.clarity }, { label: 'Specificity', value: analysis.specificity }, { label: 'Structure', value: analysis.structure }, { label: 'Outcome', value: analysis.outcome }].map((item) => (
                      <div key={item.label}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-[var(--home-text-muted)]">{item.label}</span>
                          <span className="text-sm font-semibold text-[var(--home-text)]">{item.value}%</span>
                        </div>
                        <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                          <div className="h-full bg-neutral-700 transition-all duration-500" style={{ width: `${item.value}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card className="home-card p-5 sm:p-6">
                  <h4 className="text-sm font-semibold text-[var(--home-text)] mb-3">Improved Prompt</h4>
                  <p className="text-sm text-[var(--home-text-muted)] bg-[var(--home-surface-muted)] p-3 rounded-lg border border-[var(--home-border)]">{analysis.improvedPrompt}</p>
                </Card>

                <Card className="home-card p-5 sm:p-6">
                  <h4 className="text-sm font-semibold text-[var(--home-text)] mb-3">Suggestions</h4>
                  <ul className="space-y-2">
                    {analysis.tips.map((tip, idx) => (
                      <li key={idx} className="text-sm text-[var(--home-text-muted)] flex gap-2">
                        <span className="text-neutral-700 font-bold">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </Card>

                <div className="grid grid-cols-3 gap-2">
                  <Button onClick={handleSavePrompt} variant="outline" className="home-btn-secondary"><Save className="w-4 h-4 mr-2" />Save</Button>
                  <Button onClick={handleExport} variant="outline" className="home-btn-secondary"><Download className="w-4 h-4 mr-2" />Export</Button>
                  <Button variant="outline" className="home-btn-secondary"><Share2 className="w-4 h-4 mr-2" />Share</Button>
                </div>
              </aside>
            )}
          </div>
        </main>
      </div>

      {showHistory && (
        <div className="fixed right-0 top-0 h-screen w-full sm:w-80 bg-[var(--home-surface)]/95 backdrop-blur border-l border-[var(--home-border)] p-6 z-20">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-[var(--home-text)]">Saved Prompts</h3>
            <button onClick={() => setShowHistory(false)} className="text-[var(--home-text-muted)] hover:text-[var(--home-text)] transition-colors">✕</button>
          </div>

          <div className="space-y-2 max-h-[calc(100vh-120px)] overflow-y-auto">
            {savedPrompts.length === 0 ? (
              <p className="text-[var(--home-text-muted)] text-sm text-center py-8">No saved prompts yet</p>
            ) : (
              savedPrompts.map((item) => (
                <div key={item.id} className="p-3 rounded-lg bg-[var(--home-surface-muted)] border border-[var(--home-border)] group">
                  <p className="text-sm text-[var(--home-text-muted)] line-clamp-2">{item.prompt}</p>
                  <p className="text-xs text-neutral-500 mt-2">{item.timestamp.toLocaleDateString()}</p>
                  <button
                    onClick={() => setSavedPrompts((prev) => prev.filter((p) => p.id !== item.id))}
                    className="mt-2 w-full p-1 rounded text-xs text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="w-3 h-3 mx-auto" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
