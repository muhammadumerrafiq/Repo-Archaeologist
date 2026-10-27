import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProvenanceStamp } from '../components/ui/ProvenanceStamp';

describe('ProvenanceStamp', () => {
  it('renders CONFIRMED stamp with solid cyan outline and filled dot', () => {
    render(<ProvenanceStamp confidence="confirmed" />);
    const stamp = screen.getByRole('status');
    expect(stamp).toHaveTextContent(/confirmed/i);
    expect(stamp.className).toContain('border-cyan');
    expect(stamp.className).not.toContain('border-dashed');
  });

  it('renders HEURISTIC stamp with dashed violet outline and hollow dot', () => {
    render(<ProvenanceStamp confidence="heuristic" />);
    const stamp = screen.getByRole('status');
    expect(stamp).toHaveTextContent(/heuristic/i);
    expect(stamp.className).toContain('border-dashed');
    expect(stamp.className).toContain('border-violet');
  });
});
