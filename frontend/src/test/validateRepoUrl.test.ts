import { describe, it, expect } from 'vitest';
import { validateRepoUrl } from '../lib/validateRepoUrl';

describe('validateRepoUrl', () => {
  it('accepts valid GitHub repository URLs', () => {
    const valid = [
      'https://github.com/facebook/react',
      'https://github.com/torvalds/linux/',
      'https://github.com/tiangolo/fastapi.git',
      'https://github.com/pallets/click.git/',
      '  https://github.com/vuejs/core  ',
      'facebook/react',
      'github.com/facebook/react',
    ];

    for (const url of valid) {
      const res = validateRepoUrl(url);
      expect(res.valid).toBe(true);
      expect(res.owner).toBeDefined();
      expect(res.repo).toBeDefined();
      expect(res.canonicalUrl).toMatch(/^https:\/\/github\.com\//);
    }
  });

  it('rejects non-https URLs', () => {
    expect(validateRepoUrl('http://github.com/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('git://github.com/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('ssh://github.com/owner/repo').valid).toBe(false);
  });

  it('rejects foreign or spoofed hosts', () => {
    expect(validateRepoUrl('https://gitlab.com/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('https://bitbucket.org/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('https://github.com.evil.com/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('https://evilgithub.com/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('https://192.168.1.1/owner/repo').valid).toBe(false);
  });

  it('rejects userinfo, ports, subpaths, and query params', () => {
    expect(validateRepoUrl('https://user:pass@github.com/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('https://github.com:8080/owner/repo').valid).toBe(false);
    expect(validateRepoUrl('https://github.com/owner/repo/tree/main').valid).toBe(false);
    expect(validateRepoUrl('https://github.com/owner/repo?ref=main').valid).toBe(false);
    expect(validateRepoUrl('https://github.com/owner/repo#readme').valid).toBe(false);
  });

  it('rejects control characters, whitespace, and percent-encoding', () => {
    expect(validateRepoUrl('https://github.com/owner/repo\n').valid).toBe(false);
    expect(validateRepoUrl('https://github.com/owner/ repo').valid).toBe(false);
    expect(validateRepoUrl('https://github.com/owner/%2e%2e/evil').valid).toBe(false);
    expect(validateRepoUrl('').valid).toBe(false);
  });
});
