// Utility functions for text and date formatting.

export function formatDate(dateString: string): string {
  // Format ISO date string to readable format.
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatNumber(num: number, decimals: number = 2): string {
  // Format number with specified decimal places.
  return num.toFixed(decimals);
}

export function truncateText(text: string, maxLength: number): string {
  // Truncate text to specified length.
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function formatRelevanceScore(score: number): string {
  // Format relevance score as percentage.
  return (score * 100).toFixed(1) + '%';
}

export function capitalizeWords(text: string): string {
  // Capitalize first letter of each word.
  return text.replace(/\b\w/g, char => char.toUpperCase());
}
