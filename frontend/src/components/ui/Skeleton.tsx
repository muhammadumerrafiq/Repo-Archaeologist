import React from 'react';

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => {
  return (
    <div
      aria-hidden="true"
      className={`animate-pulse bg-bg-2 border border-line/60 rounded-[2px] ${className}`}
    />
  );
};
