'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface Message {
  sender: 'user' | 'bot';
  content: string;
}

interface ChatInterfaceProps {
  onSend: (question: string) => Promise<string>;
}

export default function ChatInterface({ onSend }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const question = input.trim();
    setMessages((prev) => [...prev, { sender: 'user', content: question }]);
    setInput('');
    setLoading(true);

    try {
      const response = await onSend(question);
      setMessages((prev) => [...prev, { sender: 'bot', content: response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', content: '❌ Error fetching response.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    containerRef.current?.scrollTo({
      top: containerRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, loading]);

  return (
    <div className="mt-6">
      <div
        ref={containerRef}
        className="h-64 overflow-y-auto p-4 border rounded-lg bg-muted space-y-4"
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-[80%] p-3 rounded-xl ${
              msg.sender === 'user'
                ? 'ml-auto bg-primary text-white'
                : 'mr-auto bg-white text-gray-800'
            }`}
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start items-center text-sm text-muted-foreground">
            <Loader2 className="animate-spin mr-2 h-4 w-4" />
            Thinking...
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 mt-4">
        <Input
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <Button type="submit" disabled={loading}>
          Send
        </Button>
      </form>
    </div>
  );
}
