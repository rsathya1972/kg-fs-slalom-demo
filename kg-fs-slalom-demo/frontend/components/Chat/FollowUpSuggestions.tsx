/**
 * Clickable follow-up question chips for the chat interface.
 */

interface FollowUpSuggestionsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

export default function FollowUpSuggestions({
  suggestions,
  onSelect,
}: FollowUpSuggestionsProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onSelect(suggestion)}
          className="text-xs px-3 py-1.5 rounded-full border border-[#00A3AD] text-[#00A3AD] hover:bg-[#00A3AD] hover:text-white transition-colors text-left"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
