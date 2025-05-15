from course_gen.core.globals import (
    os, logging, json, Dict, Set, List, Optional, Union, Lock
)

logger = logging.getLogger(__name__)

class FileManager:
    """Centralized file operations manager with thread safety."""
    
    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Singleton pattern to ensure thread-safe access."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def save_to_knowledge_base(new_data: List[Dict], file_path: str = "knowledge_base.json") -> None:
        """Append new data to a JSON knowledge base file."""
        with FileManager._lock:
            try:
                existing_data = []
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f) if os.path.getsize(file_path) > 0 else []
                
                combined_data = existing_data + new_data
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(combined_data, f, indent=4, ensure_ascii=False)
                logger.info(f"Saved {len(new_data)} items to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save knowledge: {str(e)}")
                raise

    @staticmethod
    def load_knowledge(file_path: str = "knowledge_base.json") -> List[Dict]:
        """Load JSON data from file with validation."""
        with FileManager._lock:
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        if os.path.getsize(file_path) > 0:
                            data = json.load(f)
                            logger.info(f"Loaded {len(data)} items from {file_path}")
                            return data
                logger.warning(f"No valid data found at {file_path}")
                return []
            except Exception as e:
                logger.error(f"Load failed: {str(e)}")
                return []

    @staticmethod
    def export_markdown(course: Dict, filename: Optional[str] = None) -> str:
        """Export course structure to Markdown file."""
        if not filename:
            filename = f"{course['title'].strip().replace(' ', '_')}.md"

        try:
            md_content = FileManager._generate_markdown(course)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)
            logger.info(f"Markdown saved to {filename}")
            return md_content
        except Exception as e:
            logger.error(f"Markdown export failed: {str(e)}")
            raise

    @staticmethod
    def _generate_markdown(course: Dict) -> str:
        """Generate Markdown content from course dict."""
        md = f"# {course['title']}\n\n"
        md += f"*{course['description']}*\n\n"

        for i, module in enumerate(course["modules"], 1):
            md += f"## Module {i}: {module['title']}\n\n"
            md += f"{module['introduction']}\n\n"

            for section in module["sections"]:
                md += f"### {section['title']}\n\n"
                md += f"{section['content']['explanation']}\n\n"

                if section['content']['examples']:
                    md += "#### Examples\n\n"
                    for example in section['content']['examples']:
                        md += f"- {example}\n\n"

                md += f"#### Exercise\n"
                md += f"{section['content']['exercise']}\n\n"
                md += "---\n\n"

            md += f"### Module {i} Summary\n"
            md += f"{module['summary']}\n\n"

        md += "## Course Resources\n\n"
        for resource in course["resources"]:
            md += f"- [{resource['title']}]({resource['url']})\n" if resource["url"] else f"- {resource['title']}\n"

        return md

    @staticmethod
    def save_json(data: Union[Dict, List, Set], file_path: Union[str, os.PathLike], indent: int = 2) -> None:
        """Validate file_path before saving."""
        if not isinstance(file_path, (str, os.PathLike)):
            raise TypeError(f"file_path must be string or PathLike, got {type(file_path)}")

        if isinstance(data, Set):
            data = list(data)  # Convert sets to lists

        with FileManager._lock:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=indent, ensure_ascii=False)
                logger.info(f"Saved {len(data)} items to {file_path}")
            except Exception as e:
                logger.error(f"JSON save failed: {str(e)}", exc_info=True)
                raise

    @staticmethod
    def load_json(file_path: str) -> Union[Dict, List]:
        """Generic JSON loader with validation."""
        with FileManager._lock:
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        if os.path.getsize(file_path) > 0:
                            return json.load(f)
                logger.warning(f"Empty/missing file: {file_path}")
                return {} if file_path.endswith(".json") else []
            except Exception as e:
                logger.error(f"JSON load failed: {str(e)}")
                raise