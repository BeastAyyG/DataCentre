import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
}

export function Card({ children, className = '', title }: CardProps) {
  return (
    <div className={`panel-surface rounded-[2px] ${className}`}>
      {title && (
        <div className="px-4 py-3 border-b border-obsidian-600/60 bg-obsidian-700/45">
          <h3 className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-200">{title}</h3>
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
