import React, { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import FileUpload from '@/components/FileUpload';
import ChatInterface from '@/components/ChatInterface';
import { DocumentViewer } from '@/components/DocumentViewer';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, FileSearch } from 'lucide-react';

export default function Home() {
  const [fileUrl, setFileUrl] = useState('');
  type Message = {
    sender: 'user' | 'ai';
    text: string;
    sources?: any[];
  };

  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleFileUpload = (file: File) => {
    const objectUrl = URL.createObjectURL(file);
    setFileUrl(objectUrl);
  };

  const handleSend = async (q: string): Promise<string> => {
    setMessages(prev => [...prev, { sender: 'user', text: q }]);
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        body: JSON.stringify({ question: q }),
        headers: { 'Content-Type': 'application/json' },
      });

      const data = await res.json();

      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: data.answer || 'No answer found.',
          sources: data.sources || [],
        },
      ]);
      return data.answer || 'No answer found.';
    } catch (error) {
      console.error('Failed to fetch answer:', error);
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: 'An error occurred. Please try again.',
        },
      ]);
      return 'An error occurred.';
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <>
      <Head>
        <title>📄 RAG-based Financial Q&A</title>
      </Head>

      <main className="min-h-screen bg-gray-100 py-10 px-4">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* LEFT - Upload & View */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="text-2xl flex items-center gap-2">
                <FileSearch className="w-6 h-6" /> Financial Document Viewer
              </CardTitle>
              <p className="text-sm text-muted-foreground">Upload a PDF document below.</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <FileUpload onUpload={handleFileUpload} />
              {fileUrl && <DocumentViewer fileUrl={fileUrl} />}
            </CardContent>
          </Card>

          {/* RIGHT - Chat */}
          <Card className="flex flex-col h-[90vh]">
            <CardHeader>
              <CardTitle>💬 Ask Your Financial Assistant</CardTitle>
            </CardHeader>

            {/* Chat Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 pb-4">
              <div className="space-y-3">
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`max-w-[80%] px-4 py-3 rounded-lg ${
                      msg.sender === 'user'
                        ? 'bg-blue-100 ml-auto text-right'
                        : 'bg-gray-200 mr-auto'
                    }`}
                  >
                    <div className="whitespace-pre-line">{msg.text}</div>
                    {(msg.sources?.length || 0) > 0 && (
                      <div className="text-xs text-gray-600 mt-2">
                        <div className="font-semibold">Sources:</div>
                        <ul className="list-disc list-inside">
                          {(msg.sources || []).slice(0, 3).map((src, i) => (
                            <li key={i}>
                              Page {src.page} (score: {src.score.toFixed(2)})
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex items-center space-x-2 text-gray-600 text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating answer...</span>
                  </div>
                )}

                <div ref={bottomRef} />
              </div>
            </div>

            {/* Chat Input */}
            <CardContent>
              <ChatInterface onSend={handleSend} />
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  );
}
