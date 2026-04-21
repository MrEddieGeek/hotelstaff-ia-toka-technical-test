import { useEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui';
import { cn } from '@/lib/utils';

interface ConfirmButtonProps {
  onConfirm: () => void;
  label: string;
  confirmLabel?: string;
  cancelLabel?: string;
  disabled?: boolean;
  className?: string;
}

export const ConfirmButton = ({
  onConfirm,
  label,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  disabled = false,
  className,
}: ConfirmButtonProps) => {
  const [armed, setArmed] = useState(false);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    if (!armed) return;
    timer.current = window.setTimeout(() => setArmed(false), 4000);
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [armed]);

  if (!armed) {
    return (
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => setArmed(true)}
        disabled={disabled}
        className={cn('text-destructive-soft-foreground hover:bg-destructive-soft', className)}
      >
        {label}
      </Button>
    );
  }

  return (
    <span className={cn('inline-flex items-center gap-1.5', className)}>
      <Button
        type="button"
        variant="danger"
        size="sm"
        onClick={() => {
          setArmed(false);
          onConfirm();
        }}
        disabled={disabled}
      >
        {confirmLabel}
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => setArmed(false)}
      >
        {cancelLabel}
      </Button>
    </span>
  );
};
