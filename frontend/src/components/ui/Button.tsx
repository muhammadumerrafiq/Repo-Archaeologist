import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-mono font-medium tracking-wide transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none rounded-[2px]';

  const sizeStyles = {
    sm: 'text-xs px-2.5 py-1 gap-1.5',
    md: 'text-sm px-4 py-2 gap-2',
    lg: 'text-base px-6 py-2.5 gap-2.5',
  };

  const variantStyles = {
    primary: 'bg-cyan text-bg-0 hover:bg-[#68E2F2] active:bg-[#32CADF]',
    secondary: 'bg-bg-2 border border-line text-text-0 hover:border-line-strong hover:bg-bg-1 active:bg-bg-0',
    ghost: 'text-text-1 hover:text-text-0 hover:bg-bg-2',
    danger: 'bg-red/10 border border-red/40 text-red hover:bg-red/20 active:bg-red/30',
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
