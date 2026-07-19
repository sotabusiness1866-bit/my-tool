import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Moon, Sun, Copy, Check, ThumbsUp, ThumbsDown } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isError?: boolean;
  messageId?: string;
  rating?: 'like' | 'dislike' | null;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "こんにちは！私はAIアシスタントです。何かお手伝いできることはありますか？",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const stored = localStorage.getItem('theme');
    if (stored) return stored === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const userIdRef = useRef(crypto.randomUUID());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const handleCopy = async (id: number, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId((current) => (current === id ? null : current)), 1500);
    } catch (error) {
      console.error('Failed to copy message to clipboard:', error);
    }
  };

  const handleFeedback = async (id: number, messageId: string | undefined, rating: 'like' | 'dislike') => {
    if (!messageId) return;

    const previousRating = messages.find((m) => m.id === id)?.rating ?? null;
    const nextRating = previousRating === rating ? null : rating;

    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, rating: nextRating } : m)));

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message_id: messageId,
          rating: nextRating,
          user: userIdRef.current,
        }),
      });

      if (!response.ok) {
        throw new Error(`Feedback API responded with status ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to send feedback to Dify API:', error);
      setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, rating: previousRating } : m)));
    }
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.text,
          conversation_id: conversationId,
          user: userIdRef.current,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat API responded with status ${response.status}`);
      }

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      const aiMessage: Message = {
        id: Date.now() + 1,
        text: data.answer ?? '応答を取得できませんでした。',
        isUser: false,
        timestamp: new Date(),
        messageId: typeof data.message_id === 'string' ? data.message_id : undefined,
        rating: null,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to send message to Dify API:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: 'メッセージの送信に失敗しました。しばらくしてから再度お試しください。',
        isUser: false,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950 flex flex-col transition-colors duration-200">
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/60 dark:border-slate-700/60 px-4 py-4 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-slate-800 dark:text-slate-100">AI Chat</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Always here to help</p>
          </div>
          <button
            onClick={() => setIsDarkMode((prev) => !prev)}
            aria-label={isDarkMode ? 'ライトモードに切り替え' : 'ダークモードに切り替え'}
            className="flex-shrink-0 w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 flex items-center justify-center hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-200"
          >
            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Messages Container */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center shadow-md ${
                  message.isUser
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-500'
                    : 'bg-gradient-to-br from-emerald-400 to-teal-500'
                }`}
              >
                {message.isUser ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[75%] sm:max-w-[70%] ${
                  message.isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'
                }`}
              >
                <div
                  className={`px-4 py-3 rounded-2xl shadow-sm ${
                    message.isUser
                      ? 'bg-gradient-to-br from-blue-500 to-indigo-500 text-white rounded-tr-md'
                      : message.isError
                      ? 'bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 rounded-tl-md border border-red-200 dark:border-red-900'
                      : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-tl-md border border-slate-100 dark:border-slate-700'
                  }`}
                >
                  <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">
                    {message.text}
                  </p>
                </div>
                <div className="flex items-center gap-2 mt-1 px-1">
                  <span className="text-[10px] text-slate-400 dark:text-slate-500">
                    {message.timestamp.toLocaleTimeString('ja-JP', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                  {!message.isUser && !message.isError && (
                    <>
                      <button
                        onClick={() => handleCopy(message.id, message.text)}
                        aria-label="回答をコピー"
                        className="text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150"
                      >
                        {copiedId === message.id ? (
                          <Check className="w-3 h-3" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                      {message.messageId && (
                        <>
                          <button
                            onClick={() => handleFeedback(message.id, message.messageId, 'like')}
                            aria-label="役に立った"
                            className={`transition-colors duration-150 ${
                              message.rating === 'like'
                                ? 'text-emerald-500'
                                : 'text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300'
                            }`}
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => handleFeedback(message.id, message.messageId, 'dislike')}
                            aria-label="役に立たなかった"
                            className={`transition-colors duration-150 ${
                              message.rating === 'dislike'
                                ? 'text-red-500'
                                : 'text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300'
                            }`}
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center shadow-md bg-gradient-to-br from-emerald-400 to-teal-500">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white dark:bg-slate-800 px-4 py-3 rounded-2xl rounded-tl-md shadow-sm border border-slate-100 dark:border-slate-700">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200/60 dark:border-slate-700/60 px-4 py-4 shadow-lg shadow-slate-200/50 dark:shadow-slate-950/50">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="メッセージを入力..."
                rows={1}
                className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800 border-2 border-transparent focus:border-emerald-400 dark:focus:border-emerald-500 focus:bg-white dark:focus:bg-slate-800 focus:outline-none resize-none text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 transition-all duration-200 text-sm sm:text-base"
                style={{ minHeight: '48px', maxHeight: '120px' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={inputValue.trim() === '' || isTyping}
              className="flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-[10px] text-slate-400 dark:text-slate-500 text-center mt-2">
            送信ボタンをクリックしてメッセージを送信
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
