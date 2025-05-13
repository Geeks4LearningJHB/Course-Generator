from course_gen.core.globals import (
    Dict, List, Union, dataclass, field
)

@dataclass
class ScrapedContent:
    """Structured content scraped from the web."""
    title: str = ""
    text: str = ""
    code: List[str] = field(default_factory=list)
    url: str = ""
    topic: str = ""
    level: str = "intermediate"

    def to_dict(self) -> Dict:
        """Convert to dictionary (for JSON, MongoDB, etc.)"""
        return {
            "topic": self.topic,
            "title": self.title,
            "content": self.text,
            "code_examples": self.code,
            "url": self.url,
            "level": self.level
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ScrapedContent":
        """Rebuild from dictionary (for reading saved files)"""
        return cls(
            title=data.get("title", ""),
            text=data.get("content", ""),
            code=data.get("code_examples", []),
            url=data.get("url", ""),
            topic=data.get("topic", ""),
            level=data.get("level", "intermediate")
        )

    def is_valid(self) -> bool:
        """Check content validity"""
        return bool(self.text.strip())


@dataclass
class SourceConfig:
    """Site-specific configuration for scraping."""
    base_url: str
    topics: Dict[str, Dict[str, Union[str, int]]]
    content_selectors: List[str] = field(default_factory=list)
    code_selectors: List[str] = field(default_factory=list)
    avoid_urls: List[str] = field(default_factory=list)
