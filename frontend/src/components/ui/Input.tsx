import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  prefixAffordance?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  prefixAffordance,
  error,
  className = '',
  id,
  ...props
}) => {
  return (
    <div className="w-full">
      <div
        className={`flex items-center bg-bg-2 border transition-colors rounded-[2px] ${
          error ? 'border-red' : 'border-line focus-within:border-cyan'
        }`}
      >
        {prefixAffordance && (
          <span className="pl-3.5 pr-1 font-mono text-xs text-text-2 select-none">
            {prefixAffordance}
          </span>
        )}
        <input
          id={id}
          className={`w-full bg-transparent px-3 py-2.5 font-mono text-sm text-text-0 placeholder:text-text-2 focus:outline-none ${className}`}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1.5 font-mono text-xs text-red flex items-center gap-1.5" role="alert">
          <span className="w-1 h-1 rounded-full bg-red inline-block" />
          {error}
        </p>
      )}
    </div>
  );
};
