'use client';

import React, { useRef, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { UploadCloud } from 'lucide-react';

interface FileUploadProps {
  onUpload?: (file: File) => void;
  onUploadComplete?: (result: any) => void;
  onUploadError?: (error: string) => void;
}

export default function FileUpload({
  onUpload,
  onUploadComplete,
  onUploadError,
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFile = (selectedFile: File) => {
    if (selectedFile.type !== 'application/pdf') {
      onUploadError?.('Only PDF files are allowed.');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      onUploadError?.('File size must be less than 10MB.');
      return;
    }

    setFile(selectedFile);
    onUpload?.(selectedFile);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) handleFile(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) handleFile(droppedFile);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(10);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Upload failed');

      setUploadProgress(100);
      onUploadComplete?.(result);
    } catch (error: any) {
      onUploadError?.(error.message);
    } finally {
      setTimeout(() => setIsUploading(false), 500);
    }
  };

  return (
    <Card className="mt-4 border-dashed border-2 border-muted shadow-sm">
      <CardContent
        className="p-6 text-center cursor-pointer hover:bg-muted/40 transition rounded-xl"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <UploadCloud className="mx-auto mb-2 text-muted-foreground" size={36} />
        <p className="text-sm text-muted-foreground">
          {file ? `Selected: ${file.name}` : 'Click or drag & drop a PDF file here'}
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={handleFileSelect}
          className="hidden"
        />
      </CardContent>

      {file && (
        <div className="p-4 flex items-center justify-between">
          <span className="text-sm text-muted-foreground truncate">{file.name}</span>
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="ml-4"
            variant="default"
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </Button>
        </div>
      )}

      {isUploading && (
        <div className="p-4">
          <Progress value={uploadProgress} />
        </div>
      )}
    </Card>
  );
}
