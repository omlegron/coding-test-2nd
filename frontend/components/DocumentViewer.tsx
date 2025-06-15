import React from 'react';

interface DocumentViewerProps {
  fileUrl: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ fileUrl }) => {
  return (
    <div className="w-full mt-6">
      {fileUrl ? (
        <div className="rounded-lg shadow-lg border border-gray-300 overflow-hidden">
          <div className="bg-gray-100 px-4 py-2 border-b border-gray-300">
            <h2 className="text-lg font-semibold text-gray-700">📄 Document Preview</h2>
          </div>
          <iframe
            src={fileUrl}
            title="Document Viewer"
            className="w-full h-[600px] bg-white"
          />
        </div>
      ) : (
        <div className="text-center text-gray-500 italic">
          <p>No document loaded yet. Please upload a PDF file.</p>
        </div>
      )}
    </div>
  );
};
