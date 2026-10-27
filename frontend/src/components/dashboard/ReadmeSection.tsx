import React from 'react';
import { FileText, ExternalLink, AlertCircle } from 'lucide-react';
import type { ReadmeReport } from '../../types/contract';

interface ReadmeSectionProps {
  readme: ReadmeReport;
}

export const ReadmeSection: React.FC<ReadmeSectionProps> = ({ readme }) => {
  return (
    <div className="bg-bg-1 border border-border rounded p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan" />
          <h2 className="font-mono text-sm font-bold text-text-0 uppercase tracking-wider">
            Repository README
          </h2>
        </div>

        {readme.found && readme.html_url && (
          <a
            href={readme.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-text-2 hover:text-cyan flex items-center gap-1 text-xs font-mono transition-colors"
          >
            <span>View raw on GitHub</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>

      {!readme.found ? (
        <div className="p-8 text-center border border-dashed border-border rounded bg-bg-2/30 space-y-2">
          <AlertCircle className="w-6 h-6 text-text-2 mx-auto" />
          <p className="font-mono text-xs text-text-1">No README found in repository.</p>
          <p className="text-[11px] text-text-2">
            This repository does not contain a standard README file (README.md, README.rst, README.txt).
          </p>
        </div>
      ) : (
        <div className="p-4 rounded bg-bg-2 border border-border font-mono text-xs text-text-1 whitespace-pre-wrap max-h-72 overflow-y-auto leading-relaxed select-text">
          {readme.excerpt || 'README file was found but content could not be decoded.'}
        </div>
      )}
    </div>
  );
};
