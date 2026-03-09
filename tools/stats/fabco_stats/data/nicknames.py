"""Player nickname normalization.

Handles mapping of player aliases to canonical names.
"""

import json
from pathlib import Path
from typing import Dict, Optional

# Default path for nicknames file
DEFAULT_NICKNAMES_PATH = Path(__file__).parent.parent.parent / "data" / "nicknames.json"


def load_nicknames(path: Optional[Path] = None) -> Dict[str, list]:
    """Load nickname mappings from JSON file.

    Args:
        path: Path to nicknames.json. Defaults to data/nicknames.json.

    Returns:
        Dict mapping canonical names to lists of aliases.

    File format:
        {
            "CanonicalName": ["alias1", "Alias2", "ALIAS3"],
            ...
        }
    """
    if path is None:
        path = DEFAULT_NICKNAMES_PATH

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_nicknames(mappings: Dict[str, list], path: Optional[Path] = None) -> None:
    """Save nickname mappings to JSON file.

    Args:
        mappings: Dict mapping canonical names to lists of aliases.
        path: Path to save to. Defaults to data/nicknames.json.
    """
    if path is None:
        path = DEFAULT_NICKNAMES_PATH

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)


def build_reverse_mapping(mappings: Dict[str, list]) -> Dict[str, str]:
    """Build a reverse mapping from aliases to canonical names.

    Args:
        mappings: Dict mapping canonical names to lists of aliases.

    Returns:
        Dict mapping lowercase aliases to canonical names.
    """
    reverse = {}
    for canonical, aliases in mappings.items():
        # Map the canonical name to itself
        reverse[canonical.lower()] = canonical
        # Map all aliases to the canonical name
        for alias in aliases:
            reverse[alias.lower()] = canonical
    return reverse


def normalize_player_name(
    name: str,
    mappings: Optional[Dict[str, list]] = None,
    reverse_map: Optional[Dict[str, str]] = None,
) -> str:
    """Normalize a player name to its canonical form.

    Args:
        name: Player name to normalize.
        mappings: Dict mapping canonical names to aliases.
        reverse_map: Pre-built reverse mapping (for efficiency).

    Returns:
        Canonical player name, or original name if no mapping found.
    """
    if reverse_map is None:
        if mappings is None:
            mappings = load_nicknames()
        reverse_map = build_reverse_mapping(mappings)

    name = name.strip()

    # Lookup by lowercase
    normalized = reverse_map.get(name.lower())
    if normalized:
        return normalized

    # Handle "Nickname - Hero" pattern (e.g., "PlayerName - Dorinthea")
    if " - " in name:
        base_name = name.split(" - ")[0].strip()
        normalized = reverse_map.get(base_name.lower())
        if normalized:
            return normalized
        # Return just the base name if no mapping found
        return base_name

    # No mapping found, return original
    return name


class NicknameNormalizer:
    """Helper class for efficient nickname normalization."""

    def __init__(self, path: Optional[Path] = None):
        """Initialize the normalizer.

        Args:
            path: Path to nicknames.json file.
        """
        self.mappings = load_nicknames(path)
        self.reverse_map = build_reverse_mapping(self.mappings)

    def normalize(self, name: str) -> str:
        """Normalize a player name.

        Args:
            name: Player name to normalize.

        Returns:
            Canonical player name.
        """
        return normalize_player_name(name, reverse_map=self.reverse_map)

    def add_mapping(self, canonical: str, alias: str) -> None:
        """Add a new alias mapping.

        Args:
            canonical: Canonical player name.
            alias: Alias to add.
        """
        if canonical not in self.mappings:
            self.mappings[canonical] = []
        if alias.lower() not in [a.lower() for a in self.mappings[canonical]]:
            self.mappings[canonical].append(alias)
            self.reverse_map[alias.lower()] = canonical

    def save(self, path: Optional[Path] = None) -> None:
        """Save current mappings to file.

        Args:
            path: Path to save to. Defaults to original path.
        """
        save_nicknames(self.mappings, path)
