"""
Design Taste Module
Inspired by taste-skill (24K star) — anti-SLOP framework.

Combats the "AI aesthetic" problem:
- Generic rounded corners
- Predictable gradient backgrounds
- Overused color schemes
- Cookie-cutter layouts
- Lack of visual personality
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from omniforge.config import DesignConfig

logger = logging.getLogger(__name__)


@dataclass
class TasteRule:
    """A design taste rule for quality evaluation."""
    name: str
    description: str
    severity: str  # critical, warning, suggestion
    check_fn: str  # Reference to check function


class AntiSlopDetector:
    """Detects AI-generated design cliches and SLOP patterns."""

    # Common AI design cliches (SLOP = Synthetic Lack of Personality)
    SLOP_PATTERNS = {
        "gradient_hero": {
            "patterns": [
                r'linear-gradient\(.*?(blue|purple|indigo).*?(pink|cyan).*?\)',
                r'bg-gradient-to-r\s+from-(blue|purple|indigo)',
            ],
            "severity": "warning",
            "suggestion": "Use solid colors, textures, or meaningful imagery instead of generic gradients",
        },
        "parallax_overuse": {
            "patterns": [r'parallax', r'scroll-behavior.*?smooth'],
            "severity": "suggestion",
            "suggestion": "Parallax is overused; consider simpler, more deliberate motion",
        },
        "generic_rounded": {
            "patterns": [r'border-radius:\s*(12|16|20|24)px', r'rounded-(xl|2xl|3xl)'],
            "severity": "suggestion",
            "suggestion": "Use varied border radii or intentional geometric shapes",
        },
        "neon_glow": {
            "patterns": [r'box-shadow.*?(0 0 \d+px.*?rgba|glow|neon)'],
            "severity": "warning",
            "suggestion": "Subtle shadows create more sophisticated depth than neon glows",
        },
        "placeholder_pattern": {
            "patterns": [r'lorem ipsum', r'Lorem ipsum', r'TODO:', r'Placeholder'],
            "severity": "critical",
            "suggestion": "Use real content; placeholder text reduces design credibility",
        },
        "monospace_everything": {
            "patterns": [r'font-family.*?monospace(?!.*code|.*terminal)'],
            "severity": "suggestion",
            "suggestion": "Monospace is for code, not body text; use readable fonts",
        },
        "center_align_all": {
            "patterns": [r'text-align:\s*center'],
            "severity": "suggestion",
            "suggestion": "Vary alignment based on content type; not everything should be centered",
        },
        "stock_icons": {
            "patterns": [r'fa-\w+', r'<i class="fa', r'@fortawesome', r'heroicons'],
            "severity": "suggestion",
            "suggestion": "Custom icons convey more brand personality than generic icon libraries",
        },
    }

    # Design quality heuristics
    QUALITY_CHECKS = [
        "color_contrast",
        "typography_hierarchy",
        "spacing_consistency",
        "responsive_breakpoints",
        "accessibility_landmarks",
    ]

    def detect(self, content: str) -> List[Dict[str, Any]]:
        """Detect SLOP patterns in content."""
        issues = []

        for pattern_name, pattern_info in self.SLOP_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    issues.append({
                        "type": "slop",
                        "pattern": pattern_name,
                        "matches": len(matches),
                        "severity": pattern_info["severity"],
                        "suggestion": pattern_info["suggestion"],
                    })
                    break  # One match per pattern type is enough

        return issues

    def score(self, content: str) -> float:
        """Score design quality from 0-100."""
        issues = self.detect(content)
        if not issues:
            return 100.0

        # Deduct points based on severity
        deductions = 0
        for issue in issues:
            if issue["severity"] == "critical":
                deductions += 20
            elif issue["severity"] == "warning":
                deductions += 10
            else:
                deductions += 5

        return max(0, 100 - deductions)


class DesignTaste:
    """
    Design taste evaluation and enhancement system.

    Features:
    1. Anti-SLOP detection (catches AI cliches)
    2. Design quality scoring
    3. Automatic design rule application
    4. Multi-design-system support (Material, Minimal, Brutalist)
    5. Accessibility validation
    """

    def __init__(self, config: DesignConfig):
        self.config = config
        self._detector = AntiSlopDetector()
        self._design_systems = self._load_design_systems()

    def _load_design_systems(self) -> Dict[str, Dict[str, Any]]:
        """Load design system definitions."""
        return {
            "material": {
                "colors": {
                    "primary": "#6200EE",
                    "secondary": "#03DAC6",
                    "surface": "#FFFFFF",
                    "background": "#FAFAFA",
                    "error": "#B00020",
                },
                "typography": {
                    "heading": "system-ui, -apple-system, sans-serif",
                    "body": "system-ui, -apple-system, sans-serif",
                    "code": "'Fira Code', 'Cascadia Code', monospace",
                },
                "spacing": {"unit": 8},
                "elevation": [1, 2, 4, 8, 12, 24],
                "border_radius": [4, 8, 12, 16],
            },
            "minimal": {
                "colors": {
                    "primary": "#1A1A1A",
                    "secondary": "#666666",
                    "surface": "#FFFFFF",
                    "background": "#F5F5F5",
                },
                "typography": {
                    "heading": "'Inter', -apple-system, sans-serif",
                    "body": "'Inter', -apple-system, sans-serif",
                },
                "spacing": {"unit": 4},
                "elevation": [0],
                "border_radius": [0, 2, 4],
            },
            "brutalist": {
                "colors": {
                    "primary": "#000000",
                    "secondary": "#FF0000",
                    "surface": "#FFFFFF",
                    "background": "#F0F0F0",
                },
                "typography": {
                    "heading": "'Courier New', monospace",
                    "body": "'Courier New', monospace",
                },
                "spacing": {"unit": 16},
                "elevation": [4, 8],
                "border_radius": [0, 0, 0],
            },
        }

    def evaluate(self, content: str, content_type: str = "ui") -> Dict[str, Any]:
        """Evaluate content against design taste rules."""
        if not self.config.enabled:
            return {"score": 100, "issues": []}

        issues = []

        if self.config.anti_slop:
            slop_issues = self._detector.detect(content)
            issues.extend(slop_issues)

        # Content-type specific checks
        if content_type in ("ui", "html", "css", "frontend"):
            issues.extend(self._check_ui_quality(content))
        elif content_type in ("code", "python", "javascript"):
            issues.extend(self._check_code_aesthetics(content))
        elif content_type in ("copy", "text", "marketing"):
            issues.extend(self._check_copy_quality(content))

        score = self._calculate_score(issues)

        return {
            "score": round(score, 1),
            "issues": issues,
            "issue_count": len(issues),
            "critical_count": sum(1 for i in issues if i["severity"] == "critical"),
            "overall": self._get_score_label(score),
        }

    def apply(self, content: str, design_system: Optional[str] = None) -> str:
        """Apply design taste rules to improve content."""
        ds_name = design_system or self.config.design_system
        ds = self._design_systems.get(ds_name, self._design_systems["material"])

        # Apply design system values
        if "css" in content.lower() or "style" in content.lower():
            content = self._inject_design_tokens(content, ds)

        # Remove SLOP patterns
        content = self._remove_slop_patterns(content)

        return content

    def _inject_design_tokens(self, content: str, ds: Dict[str, Any]) -> str:
        """Inject design tokens into content."""
        # Replace generic color values with design system colors
        content = re.sub(
            r'#333333|#333|#444444|#444',
            ds["colors"]["primary"],
            content
        )
        return content

    def _remove_slop_patterns(self, content: str) -> str:
        """Remove detected SLOP patterns."""
        # Remove placeholder text
        content = re.sub(
            r'(?i)lorem ipsum dolor sit amet.*?\n',
            '[Content needed — replace with real copy]\n',
            content
        )
        return content

    def _check_ui_quality(self, content: str) -> List[Dict[str, Any]]:
        """Check UI-specific quality issues."""
        issues = []

        # Check for color contrast
        if not re.search(r'#[0-9A-Fa-f]{6}', content):
            issues.append({
                "type": "ui",
                "pattern": "no_explicit_colors",
                "severity": "warning",
                "suggestion": "Define explicit color palette instead of relying on defaults",
            })

        # Check for responsive design
        if not re.search(r'@media|responsive|breakpoint|sm:|md:|lg:|xl:', content, re.IGNORECASE):
            issues.append({
                "type": "ui",
                "pattern": "no_responsive",
                "severity": "warning",
                "suggestion": "Add responsive breakpoints for mobile and tablet",
            })

        return issues

    def _check_code_aesthetics(self, content: str) -> List[Dict[str, Any]]:
        """Check code-level aesthetic quality."""
        issues = []

        # Check for magic numbers
        if re.findall(r'\b\d{4,}\b', content):
            issues.append({
                "type": "code",
                "pattern": "magic_numbers",
                "severity": "suggestion",
                "suggestion": "Extract magic numbers into named constants",
            })

        return issues

    def _check_copy_quality(self, content: str) -> List[Dict[str, Any]]:
        """Check copy/text quality."""
        issues = []

        # Check for passive voice
        passive_patterns = [
            r'\b(is|are|was|were|been|being)\s+\w+ed\b',
        ]
        for pattern in passive_patterns:
            if re.findall(pattern, content):
                issues.append({
                    "type": "copy",
                    "pattern": "passive_voice",
                    "severity": "suggestion",
                    "suggestion": "Use active voice for more engaging copy",
                })
                break

        return issues

    def _calculate_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate overall design quality score."""
        if not issues:
            return 100.0

        deductions = 0
        for issue in issues:
            multiplier = len(str(issue.get("matches", 1)))
            if issue["severity"] == "critical":
                deductions += 15 * multiplier
            elif issue["severity"] == "warning":
                deductions += 8 * multiplier
            else:
                deductions += 3 * multiplier

        return max(0, 100 - deductions)

    def _get_score_label(self, score: float) -> str:
        """Get human-readable score label."""
        if score >= 95:
            return "Exceptional"
        elif score >= 85:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Significant Issues"

    def get_design_tokens(self, system: Optional[str] = None) -> Dict[str, Any]:
        """Get design tokens for a specific design system."""
        return self._design_systems.get(
            system or self.config.design_system,
            self._design_systems["material"]
        )