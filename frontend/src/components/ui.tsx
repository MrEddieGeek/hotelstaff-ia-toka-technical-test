import { forwardRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode } from 'react';

import { cn } from '@/lib/utils';

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' | 'danger' }
>(({ className, variant = 'primary', ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      'inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 disabled:opacity-50',
      variant === 'primary' && 'bg-slate-900 text-white hover:bg-slate-800',
      variant === 'ghost' && 'bg-transparent text-slate-900 hover:bg-slate-100',
      variant === 'danger' && 'bg-red-600 text-white hover:bg-red-500',
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
        'flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus-visible:border-slate-900 focus-visible:outline-none disabled:opacity-50',
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = 'Input';

export const Label = ({ children, htmlFor }: { children: ReactNode; htmlFor?: string }) => (
  <label htmlFor={htmlFor} className="mb-1 block text-sm font-medium text-slate-700">
    {children}
  </label>
);

export const Card = ({ children, className }: { children: ReactNode; className?: string }) => (
  <div className={cn('rounded-lg border border-slate-200 bg-white p-6 shadow-sm', className)}>
    {children}
  </div>
);

export const FormError = ({ message }: { message?: string }) =>
  message ? <p className="mt-1 text-sm text-red-600">{message}</p> : null;

export const Alert = ({
  kind = 'error',
  children,
}: {
  kind?: 'error' | 'success' | 'info';
  children: ReactNode;
}) => (
  <div
    role="alert"
    className={cn(
      'rounded-md border px-4 py-3 text-sm',
      kind === 'error' && 'border-red-200 bg-red-50 text-red-800',
      kind === 'success' && 'border-green-200 bg-green-50 text-green-800',
      kind === 'info' && 'border-slate-200 bg-slate-50 text-slate-800',
    )}
  >
    {children}
  </div>
);

export const Spinner = () => (
  <span
    aria-label="cargando"
    className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900"
  />
);
