import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, RotateCcw, ArrowLeft, ShieldAlert } from 'lucide-react';
import type { ErrorCode } from '../../types/contract';
import { Button } from '../ui/Button';

interface ErrorViewProps {
  code: ErrorCode;
  message: string;
  retryAfter?: number | null;
  onRetry?: () => void;
}

export const ErrorView: React.FC<ErrorViewProps> = ({
  code,
  message,
  retryAfter,
  onRetry,
}) => {
  const getErrorTitle = (errCode: ErrorCode): string => {
    switch (errCode) {
      case 'INVALID_URL':
        return 'Invalid Repository Target';
      case 'UNSUPPORTED_HOST':
        return 'Unsupported Git Host';
      case 'NOT_FOUND':
        return 'Repository Not Found';
      case 'PRIVATE_OR_FORBIDDEN':
        return 'Access Prohibited (Private Repository)';
      case 'RATE_LIMITED':
        return 'GitHub API Rate Limit Exceeded';
      case 'TIMEOUT':
        return 'Survey Request Timed Out';
      default:
        return 'Analysis Engine Error';
    }
  };

  const getErrorDescription = (errCode: ErrorCode, msg: string): string => {
    switch (errCode) {
      case 'INVALID_URL':
        return 'The provided repository target format is invalid. Please supply an owner/repo slug (e.g. facebook/react) or full public GitHub URL.';
      case 'UNSUPPORTED_HOST':
        return 'Only public repositories hosted on github.com are currently supported by the deterministic analysis engine.';
      case 'NOT_FOUND':
        return 'GitHub returned HTTP 404. Verify the owner and repository name are spelled correctly, or that the repository was not deleted.';
      case 'PRIVATE_OR_FORBIDDEN':
        return 'Repo Archaeologist only surveys public open-source codebases. Private or restricted repositories cannot be accessed.';
      case 'RATE_LIMITED':
        return retryAfter
          ? `The GitHub API rate limit has been reached. Analysis can resume after ${Math.ceil(
              retryAfter / 60
            )} minutes.`
          : 'The GitHub API rate limit has been reached. Please configure a read-only GITHUB_TOKEN in backend/.env for 5,000 requests/hr.';
      case 'TIMEOUT':
        return 'The repository survey timed out while downloading metadata or git trees. The repository may be exceptionally large or upstream latency is elevated.';
      default:
        return msg || 'An unexpected upstream error occurred while communicating with the GitHub API.';
    }
  };

  return (
    <div className="max-w-2xl mx-auto my-12 p-8 bg-bg-1 border border-rust/40 rounded space-y-6 shadow-xl">
      <div className="flex items-start gap-4">
        <div className="p-3 rounded bg-rust/10 border border-rust/30 text-rust">
          <ShieldAlert className="w-8 h-8" />
        </div>

        <div className="space-y-1 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-rust bg-rust/10 px-1.5 py-0.2 rounded border border-rust/30">
              {code}
            </span>
            <span className="text-xs font-mono text-text-2">Excavation Halted</span>
          </div>
          <h2 className="text-xl font-mono font-bold text-text-0">
            {getErrorTitle(code)}
          </h2>
        </div>
      </div>

      <div className="p-4 rounded bg-bg-2 border border-border text-xs md:text-sm font-sans text-text-1 leading-relaxed">
        {getErrorDescription(code, message)}
      </div>

      {code === 'RATE_LIMITED' && retryAfter && (
        <div className="flex items-center gap-2 text-xs font-mono text-amber p-3 rounded bg-amber/5 border border-amber/20">
          <Clock className="w-4 h-4 text-amber" />
          <span>Retry available in approximately {Math.ceil(retryAfter / 60)} minute(s).</span>
        </div>
      )}

      <div className="pt-4 border-t border-border flex items-center justify-between gap-4 flex-wrap">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs font-mono text-text-1 hover:text-cyan transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Target Locator</span>
        </Link>

        {onRetry && (
          <Button
            type="button"
            variant="primary"
            onClick={onRetry}
            className="flex items-center gap-2 text-xs"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry Excavation</span>
          </Button>
        )}
      </div>
    </div>
  );
};
