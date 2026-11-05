import React, { useRef, useState } from 'react';
import { UploadCloud, FileSpreadsheet, Loader2 } from 'lucide-react';
import { api } from '../../api/client';
import { DatasetProfile } from '../../types';

interface DatasetUploaderProps {
  sessionId?: string;
  onUploaded: (fileName: string, storedPath: string, profile: DatasetProfile) => void;
}

export const DatasetUploader: React.FC<DatasetUploaderProps> = ({ sessionId, onUploaded }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const res = await api.uploadDataset(file, sessionId);
      onUploaded(res.file_name, res.stored_path, res.profile);
    } catch (err: any) {
      setError(err.message || 'Dataset upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx,.xls,.json,.parquet,.sqlite,.sqlite3,.db"
        className="hidden"
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFile(e.target.files[0]);
          }
        }}
      />

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
          isDragging
            ? 'border-google-blue bg-google-blue-subtle/40 dark:bg-google-blue-darkSubtle/30'
            : 'border-google-border dark:border-google-dark-border hover:border-google-blue/70 bg-google-secondary dark:bg-google-dark-secondary'
        }`}
      >
        {isUploading ? (
          <div className="flex flex-col items-center gap-2 text-google-muted dark:text-google-dark-muted">
            <Loader2 size={32} className="animate-spin text-google-blue" />
            <p className="text-xs font-medium">Profiling schema & introspecting columns...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 text-center">
            <div className="w-10 h-10 rounded-full bg-google-surface dark:bg-google-dark-surface flex items-center justify-center text-google-blue">
              <UploadCloud size={20} />
            </div>
            <div>
              <p className="text-sm font-medium text-google-text dark:text-google-dark-text">
                Drop your dataset here, or <span className="text-google-blue hover:underline">browse</span>
              </p>
              <p className="text-xs text-google-muted dark:text-google-dark-muted mt-1">
                Supports CSV, Excel (XLSX, XLS), JSON, Parquet, and SQLite databases
              </p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 text-xs text-google-red text-center font-medium">
          {error}
        </div>
      )}
    </div>
  );
};

