import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';

interface LoadingSkeletonProps {
  repoTarget: string;
}

const STAGES = [
  'Connecting to GitHub & validating repository...',
  'Fetching git tree & language distribution...',
  'Inspecting manifest files & entry candidates...',
  'Synthesizing architecture graph & plain-English guide...',
];

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ repoTarget }) => {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 900);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto py-8">
      {/* Progress Status Bar */}
      <div className="bg-bg-1 border border-border rounded p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-cyan animate-spin" />
            <div>
              <span className="font-mono text-xs text-cyan uppercase tracking-wider block">
                Excavation in Progress
              </span>
              <h2 className="font-mono font-bold text-base text-text-0">
                Surveying {repoTarget}
              </h2>
            </div>
          </div>
          <span className="font-mono text-xs text-text-2">
            Stage {stageIndex + 1} of {STAGES.length}
          </span>
        </div>

        {/* Progress Bar Track */}
        <div className="h-1.5 w-full bg-bg-2 rounded-full overflow-hidden">
          <div
            className="h-full bg-cyan transition-all duration-500 ease-out"
            style={{ width: `${((stageIndex + 1) / STAGES.length) * 100}%` }}
          />
        </div>

        <p className="font-mono text-xs text-text-1 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan animate-pulse inline-block" />
          <span>{STAGES[stageIndex]}</span>
        </p>
      </div>

      {/* Skeletons Layout */}
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="bg-bg-1 border border-border rounded p-6 space-y-4">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-8 w-80" />
          <Skeleton className="h-4 w-full max-w-xl" />
          <div className="flex gap-4 pt-4 border-t border-border">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-24" />
          </div>
        </div>

        {/* 2-Column Grid Skeletons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-bg-1 border border-border rounded p-6 space-y-4">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
          <div className="bg-bg-1 border border-border rounded p-6 space-y-4">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </div>

        {/* Explorer Skeleton */}
        <div className="bg-bg-1 border border-border rounded p-6 space-y-3">
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-3/4" />
        </div>
      </div>
    </div>
  );
};
