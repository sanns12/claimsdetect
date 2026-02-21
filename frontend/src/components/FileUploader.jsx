import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud } from 'react-icons/fi';

export default function FileUploader({ onDrop }) {
  const onDropCallback = useCallback((acceptedFiles) => {
    onDrop(acceptedFiles);
  }, [onDrop]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onDropCallback,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    maxSize: 10485760, // 10MB
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive 
          ? 'border-blue-500 bg-blue-500/5' 
          : 'border-gray-700 hover:border-blue-500/50'
      }`}
    >
      <input {...getInputProps()} />
      <FiUploadCloud className="mx-auto text-4xl text-gray-400 mb-4" />
      {isDragActive ? (
        <p className="text-blue-500">Drop files here...</p>
      ) : (
        <>
          <p className="text-gray-400">
            Drag & drop files here, or click to select
          </p>
          <p className="text-xs text-gray-500 mt-2">
            PDF, JPG, PNG, TXT (Max 10MB each)
          </p>
        </>
      )}
    </div>
  );
}