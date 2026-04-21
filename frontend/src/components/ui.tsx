import {
  forwardRef,
  type ButtonHTMLAttributes,
  type InputHTMLAttributes,
  type LabelHTMLAttributes,
  type ReactNode,
  type TextareaHTMLAttributes,
} from 'react';

import { cn } from '@/lib/utils';

const focusRing =
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background';

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: 'primary' | 'ghost' | 'danger' | 'outline' | 'subtle';
    size?: 'sm' | 'md';
  }
>(({ className, variant = 'primary', size = 'md', ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      'inline-flex items-center justify-center gap-1.5 rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
      focusRing,
      size === 'md' && 'h-10 px-4 text-sm',
      size === 'sm' && 'h-8 px-3 text-xs',
      variant === 'primary' &&
        'bg-accent text-accent-foreground hover:bg-accent/90 active:bg-accent/85',
      variant === 'ghost' &&
        'bg-transparent text-foreground hover:bg-muted',
      variant === 'outline' &&
        'border border-border bg-transparent text-foreground hover:bg-muted',
      variant === 'subtle' &&
        'bg-muted text-foreground hover:bg-subtle',
      variant === 'danger' &&
        'bg-destructive text-destructive-foreground hover:bg-destructive/90',
      className,
    )}
    {...props}
  />
));
Button.displayName = 'Button';

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'block h-10 w-full rounded border border-input bg-surface px-3 text-sm text-foreground placeholder:text-muted-foreground transition-colors hover:border-muted-foreground/40 disabled:opacity-50',
        focusRing,
        'focus-visible:border-ring',
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = 'Input';

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      'block w-full rounded border border-input bg-surface px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground transition-colors hover:border-muted-foreground/40 disabled:opacity-50',
      focusRing,
      'focus-visible:border-ring',
      className,
    )}
    {...props}
  />
));
Textarea.displayName = 'Textarea';

export const Label = ({
  className,
  children,
  ...rest
}: LabelHTMLAttributes<HTMLLabelElement> & { children: ReactNode }) => (
  <label
    className={cn(
      'mb-1.5 block text-2xs font-semibold uppercase tracking-wider text-muted-foreground',
      className,
    )}
    {...rest}
  >
    {children}
  </label>
);

export const Surface = ({
  children,
  className,
  as: Tag = 'div',
}: {
  children: ReactNode;
  className?: string;
  as?: 'div' | 'section' | 'article';
}) => (
  <Tag
    className={cn(
      'rounded-lg border border-border bg-surface text-surface-foreground',
      className,
    )}
  >
    {children}
  </Tag>
);

export const FormError = ({ message }: { message?: string }) =>
  message ? (
    <p role="alert" className="mt-1.5 text-xs text-destructive-soft-foreground">
      {message}
    </p>
  ) : null;

export const Alert = ({
  kind = 'error',
  children,
  className,
}: {
  kind?: 'error' | 'success' | 'info';
  children: ReactNode;
  className?: string;
}) => (
  <div
    role="alert"
    className={cn(
      'rounded border px-4 py-3 text-sm',
      kind === 'error' &&
        'border-destructive/30 bg-destructive-soft text-destructive-soft-foreground',
      kind === 'success' &&
        'border-success/30 bg-success-soft text-success-soft-foreground',
      kind === 'info' && 'border-border bg-info-soft text-info-soft-foreground',
      className,
    )}
  >
    {children}
  </div>
);

export const Spinner = ({ className }: { className?: string }) => (
  <span
    role="status"
    aria-live="polite"
    className={cn(
      'inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent opacity-70',
      className,
    )}
  >
    <span className="sr-only">Cargando</span>
  </span>
);

export const Badge = ({
  children,
  tone = 'neutral',
  className,
}: {
  children: ReactNode;
  tone?: 'neutral' | 'accent' | 'success' | 'destructive';
  className?: string;
}) => (
  <span
    className={cn(
      'inline-flex items-center rounded px-1.5 py-0.5 text-2xs font-medium tracking-wide',
      tone === 'neutral' && 'bg-muted text-muted-foreground',
      tone === 'accent' && 'bg-accent-soft text-accent-soft-foreground',
      tone === 'success' && 'bg-success-soft text-success-soft-foreground',
      tone === 'destructive' && 'bg-destructive-soft text-destructive-soft-foreground',
      className,
    )}
  >
    {children}
  </span>
);

export const SectionHeader = ({
  eyebrow,
  title,
  meta,
  children,
}: {
  eyebrow?: string;
  title: string;
  meta?: ReactNode;
  children?: ReactNode;
}) => (
  <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-2">
    <div>
      {eyebrow && (
        <p className="mb-1 text-2xs font-semibold uppercase tracking-wider text-muted-foreground">
          {eyebrow}
        </p>
      )}
      <h2 className="font-display text-2xl font-medium text-foreground">{title}</h2>
      {children && (
        <p className="mt-1 max-w-prose text-sm text-muted-foreground">{children}</p>
      )}
    </div>
    {meta && <div className="text-sm text-muted-foreground">{meta}</div>}
  </header>
);

export const SkipLink = () => (
  <a
    href="#contenido"
    className={cn(
      'sr-only focus-visible:not-sr-only focus-visible:fixed focus-visible:left-4 focus-visible:top-4 focus-visible:z-50 focus-visible:rounded focus-visible:bg-accent focus-visible:px-3 focus-visible:py-2 focus-visible:text-sm focus-visible:font-medium focus-visible:text-accent-foreground',
    )}
  >
    Saltar al contenido
  </a>
);
