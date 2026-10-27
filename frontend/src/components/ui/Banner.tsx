import React from 'react';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

interface BannerProps {
  type?: 'warning' | 'error' | 'info';
  code?: string;
  message: string;
  className?: string;
}

export const Banner: React.FC<BannerProps> = ({
  type = 'warning',
  code,
  message,
  className = '',
}) => {
  const styles = {
    warning: {
      container: 'bg-amber/5 border-amber/30 text-amber',
      icon: AlertTriangle,
    },
    error: {
      container: 'bg-red/5 border-red/30 text-red',
      icon: AlertCircle,
    },
    info: {
      container: 'bg-cyan/5 border-cyan/30 text-cyan',
      icon: Info,
    },
  };

  const { container, icon: Icon } = styles[type];

  return (
    <div
      role="alert"
      className={`flex items-start gap-3 p-3 border rounded-[2px] font-mono text-xs ${container} ${className}`}
    >
      <Icon className="w-4 h-4 shrink-0 mt-0.5" />
      <div className="flex-1">
        {code && (
          <span className="font-semibold uppercase tracking-wider mr-2 bg-black/30 px-1 py-0.5 rounded-[2px]">
            [{code}]
          </span>
        )}
        <span className="text-text-0">{message}</span>
      </div>
    </div>
  );
};
