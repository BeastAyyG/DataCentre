import React from 'react';

type ButtonVariant = 'primary' | 'accept' | 'reject' | 'ghost';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: 'sm' | 'md' | 'lg';
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-gradient-to-r from-cyber-purple to-cyber-500 hover:from-cyber-600 hover:to-cyber-purple text-white border border-cyber-400/30',
  accept: 'bg-healthy/85 hover:bg-healthy text-white border border-healthy/50',
  reject: 'bg-cyber-attack/85 hover:bg-cyber-attack text-white border border-cyber-attack/60',
  ghost: 'bg-transparent hover:bg-obsidian-700/80 text-slate-300 border border-obsidian-600',
};

const sizeClasses: Record<string, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-[2px]',
  md: 'px-4 py-2 text-sm rounded-[2px]',
  lg: 'px-6 py-3 text-base rounded-[2px]',
};

export function Button({ variant = 'primary', size = 'md', className = '', children, ...props }: ButtonProps) {
  return (
    <button
      className={`font-medium transition disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size!]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
