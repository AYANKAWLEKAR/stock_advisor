import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount)
}

export function formatPercentage(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date)
}

export function parseStockSymbols(input: string): string[] {
  // Extract stock symbols from various formats
  const patterns = [
    /\[([^\]]+)\]/g, // [AAPL, MSFT, GOOGL]
    /([A-Z]{1,5})/g, // AAPL MSFT GOOGL
  ];
  
  const symbols = new Set<string>();
  
  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(input)) !== null) {
      if (match[1]) {
        // Extract from brackets
        const bracketSymbols = match[1].split(',').map(s => s.trim().toUpperCase());
        bracketSymbols.forEach(symbol => {
          if (symbol.length <= 5 && /^[A-Z]+$/.test(symbol)) {
            symbols.add(symbol);
          }
        });
      } else if (match[0]) {
        // Direct symbol match
        const symbol = match[0].toUpperCase();
        if (symbol.length <= 5 && /^[A-Z]+$/.test(symbol)) {
          symbols.add(symbol);
        }
      }
    }
  });
  
  return Array.from(symbols);
}
