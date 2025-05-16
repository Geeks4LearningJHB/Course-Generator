from course_gen.core.globals import (
    os, logging, json, Dict, Set, List, Optional, Union, Lock, re
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
    def export_markdown(course: Dict, filename: Optional[str] = None):
        """Export course structure to Markdown file."""
        if not filename:
            filename = re.sub(r'[ /\-.,]', '_', filename)
            filename = f"{course['title'].strip()}.md"

        try:
            md_content = FileManager._generate_markdown(course)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)
            logger.info(f"Markdown saved to {filename}")
        except Exception as e:
            logger.error(f"Markdown export failed: {str(e)}")
            raise

    @staticmethod
    def _generate_markdown(course: Dict) -> str:
        """Generate Markdown content following template structure without using template strings."""
        md = []
        
        # Course Introduction
        intro = [
            f"# {course.get('title', '')}",
            "",
            "## Course Overview",
            "",
            course.get('ai_enhanced_description', ''),
            "",
            "### Course Objectives",
            "",
            course.get('learning_objectives', ''),
            "",
            "### Prerequisites",
            "",
            course.get('prerequisites', ''),
            "",
            "### Course Structure",
            "",
            course.get('structure_overview', ''),
            "",
            "### Learning Path",
            "",
            course.get('learning_path', ''),
            ""
        ]
        md.append("\n".join(intro))

        # Modules
        for i, module in enumerate(course.get('modules', []), 1):
            # Module Introduction
            module_intro = [
                f"# Module {i}: {module.get('title', '')}",
                "",
                "## Overview",
                "",
                module.get('ai_enhanced_overview', ''),
                "",
                "## Learning Objectives",
                "",
                module.get('learning_objectives', ''),
                "",
                "## Module Outline",
                "",
                module.get('module_outline', ''),
                ""
            ]
            md.append("\n".join(module_intro))

            # Units
            for unit in module.get('units', []):
                if unit.get('type') == 'explanation':
                    explanation = [
                        f"## {unit.get('title', '')}",
                        "",
                        unit['content'].get('explanation', ''),
                        "",
                        "### Key Points",
                        "",
                        unit['content'].get('key_points', ''),
                        "",
                        "### Real-world Application",
                        "",
                        unit['content'].get('real_world_application', ''),
                        "",
                        "### Conceptual Model",
                        "",
                        unit['content'].get('conceptual_model', ''),
                        "",
                        "### Common Misconceptions",
                        "",
                        unit['content'].get('misconceptions', ''),
                        "",
                        "---",
                        ""
                    ]
                    md.append("\n".join(explanation))
                
                elif unit.get('type') == 'example':
                    example = [
                        f"### Example: {unit.get('title', '')}",
                        "",
                        "#### Problem Statement",
                        "",
                        unit['content'].get('problem_statement', ''),
                        "",
                        "#### Solution Approach",
                        "",
                        unit['content'].get('solution_approach', ''),
                        "",
                        f"```{unit['content'].get('language', '')}",
                        unit['content'].get('code', ''),
                        "```",
                        "",
                        "#### Explanation",
                        "",
                        unit['content'].get('explanation', ''),
                        "",
                        "#### Alternative Approaches",
                        "",
                        unit['content'].get('alternative_approaches', ''),
                        "",
                        "#### Practice Variation",
                        "",
                        unit['content'].get('practice_variation', ''),
                        "",
                        "---",
                        ""
                    ]
                    md.append("\n".join(example))
                
                elif unit.get('type') == 'case_study':
                    case_study = [
                        f"## Case Study: {unit.get('title', '')}",
                        "",
                        "### Background",
                        "",
                        unit['content'].get('background', ''),
                        "",
                        "### Challenge",
                        "",
                        unit['content'].get('challenge', ''),
                        "",
                        "### Analysis",
                        "",
                        unit['content'].get('analysis', ''),
                        "",
                        "### Solution",
                        "",
                        unit['content'].get('solution', ''),
                        "",
                        "### Lessons Learned",
                        "",
                        unit['content'].get('lessons_learned', ''),
                        "",
                        "### Discussion Questions",
                        "",
                        unit['content'].get('discussion_questions', ''),
                        "",
                        "---",
                        ""
                    ]
                    md.append("\n".join(case_study))

            # Module Summary
            summary = [
                f"## Module {i} Summary",
                "",
                module.get('summary', ''),
                ""
            ]
            md.append("\n".join(summary))

        # Course Conclusion
        conclusion = [
            "# Course Conclusion",
            "",
            "## Congratulations!",
            "",
            f"You've completed the {course.get('level', '')} course on {course.get('topic', '')}! Let's recap what you've learned:",
            "",
            course.get('key_learnings', ''),
            "",
            "## Next Steps",
            "",
            course.get('next_steps', ''),
            ""
        ]
        md.append("\n".join(conclusion))

        # Resources
        if course.get('resources'):
            resources = ["## Course Resources", ""]
            for resource in course['resources']:
                if resource.get('url'):
                    resources.append(f"- [{resource.get('title', '')}]({resource.get('url', '')})")
                else:
                    resources.append(f"- {resource.get('title', '')}")
            resources.append("")
            md.append("\n".join(resources))

        return "\n".join(md)

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