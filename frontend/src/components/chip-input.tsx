import { useId, useRef, useState, type KeyboardEvent } from 'react';

import { cn } from '@/lib/utils';

interface ChipInputProps {
  value: string[];
  onChange: (next: string[]) => void;
  suggestions?: string[];
  placeholder?: string;
  id?: string;
  describedBy?: string;
}

export const ChipInput = ({
  value,
  onChange,
  suggestions = [],
  placeholder,
  id,
  describedBy,
}: ChipInputProps) => {
  const [draft, setDraft] = useState('');
  const reactId = useId();
  const inputId = id ?? reactId;
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = `${inputId}-suggestions`;

  const commit = (raw: string) => {
    const token = raw.trim().toLowerCase();
    if (!token) return;
    if (value.includes(token)) {
      setDraft('');
      return;
    }
    onChange([...value, token]);
    setDraft('');
  };

  const remove = (token: string) => {
    onChange(value.filter((t) => t !== token));
    inputRef.current?.focus();
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',' || e.key === 'Tab') {
      if (draft.trim()) {
        e.preventDefault();
        commit(draft);
      }
    } else if (e.key === 'Backspace' && !draft && value.length) {
      e.preventDefault();
      onChange(value.slice(0, -1));
    }
  };

  const filteredSuggestions = suggestions
    .filter((s) => !value.includes(s))
    .filter((s) => (draft ? s.includes(draft.toLowerCase()) : true))
    .slice(0, 6);

  return (
    <div>
      <div
        className={cn(
          'flex min-h-10 flex-wrap items-center gap-1.5 rounded border border-input bg-surface px-2 py-1.5 transition-colors focus-within:border-ring focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background hover:border-muted-foreground/40',
        )}
        onClick={() => inputRef.current?.focus()}
      >
        {value.map((token) => (
          <span
            key={token}
            className="inline-flex items-center gap-1 rounded bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent-soft-foreground"
          >
            <span className="font-mono">{token}</span>
            <button
              type="button"
              aria-label={`Quitar ${token}`}
              onClick={(e) => {
                e.stopPropagation();
                remove(token);
              }}
              className="rounded text-accent-soft-foreground/70 hover:text-accent-soft-foreground focus:outline-none"
            >
              ×
            </button>
          </span>
        ))}
        <input
          id={inputId}
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          onBlur={() => draft.trim() && commit(draft)}
          placeholder={value.length === 0 ? placeholder : ''}
          className="min-w-[8rem] flex-1 bg-transparent px-1 py-0.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          aria-controls={listboxId}
          aria-describedby={describedBy}
        />
      </div>
      {filteredSuggestions.length > 0 && (
        <div id={listboxId} className="mt-2 flex flex-wrap gap-1.5">
          <span className="self-center text-2xs uppercase tracking-wider text-muted-foreground">
            Sugerencias
          </span>
          {filteredSuggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => commit(s)}
              className="rounded bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground transition-colors hover:bg-subtle hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              + {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
