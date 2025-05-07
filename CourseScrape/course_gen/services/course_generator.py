from course_gen.core.globals import (
    logger, json, re, Dict, List, os, defaultdict
)

from .content_enhancer import AIContentEnhancer

class CourseGenerator:
    """Advanced AI-powered course generator with dynamic content and MongoDB storage"""
    def __init__(self, knowledge_file: str = "knowledge_base.json", db_manager=None):
        self.knowledge_file = knowledge_file
        self.knowledge = []
        self.ai_enhancer = AIContentEnhancer()
        self.db_manager = db_manager  # MongoDB database manager
        self.load_knowledge()

        # Course templates with placeholders for AI-enhanced content
        self.templates = {
            'module': {
                'introduction': (
                    "Welcome to this {level} course on {topic}!\n\n"
                    "In this module, we'll cover:\n"
                    "- Core concepts of {topic}\n"
                    "- Practical examples\n"
                    "- Hands-on exercises\n\n"
                    "By the end, you'll be able to:\n"
                    "- Explain key {topic} concepts\n"
                    "- Write basic {topic} code\n"
                    "- Solve simple problems using {topic}"
                ),
                'section': {
                    'explanation': (
                        "### {title}\n\n"
                        "{ai_enhanced_explanation}\n\n"
                        "**Key Concepts:**\n"
                        "{key_points}\n\n"
                        "**Real-world Analogy:**\n"
                        "{analogy}"
                    ),
                    'example': (
                        "#### Example: {title}\n\n"
                        "```{language}\n{code}\n```\n\n"
                        "**How It Works:**\n"
                        "{ai_enhanced_explanation}\n\n"
                        "**Try It Yourself:**\n"
                        "{suggestion}"
                    ),
                    'exercise': (
                        "#### Exercise: {title}\n\n"
                        "**Objective:** {objective}\n\n"
                        "**Requirements:**\n"
                        "{requirements}\n\n"
                        "**Steps to Solve:**\n"
                        "{steps}\n\n"
                        "**Hints:**\n"
                        "{hints}"
                    )
                },
                'summary': (
                    "### Summary\n\n"
                    "Congratulations on completing this {level} module on {topic}!\n\n"
                    "**Key Achievements:**\n"
                    "- Learned core {topic} concepts\n"
                    "- Practiced with real examples\n"
                    "- Completed hands-on exercises\n\n"
                    "**Next Steps:**\n"
                    "- Try building a small project\n"
                    "- Explore more advanced topics\n"
                    "- Join community discussions"
                )
            }
        }
        level_map = {
            "beginner": 1,
            "intermediate": 2, 
            "advanced": 3
        }

    def load_knowledge(self):
        """Load knowledge base from file"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
                logger.info(f"Loaded {len(self.knowledge)} knowledge items")
            else:
                logger.warning("No knowledge base found. Please scrape content first.")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            self.knowledge = []  # Initialize as empty list to avoid errors

    def generate_course(self, topic: str, level: str = "beginner", save_to_db: bool = False) -> Dict:
        """Generate a complete AI-enhanced course

        Args:
            topic: Course topic
            level: Course difficulty level
            save_to_db: Whether to save the course to MongoDB

        Returns:
            Dict: Generated course data or error message
        """
        # Ensure we have a knowledge base to work with
        if not self.knowledge:
            logger.warning("No knowledge items found - generating a minimal course structure")
            # Create a minimal course structure
            course = self._create_minimal_course(topic, level)
            return course

        relevant_content = [item for item in self.knowledge
                          if item['topic'].lower() == topic.lower()
                          and item['level'].lower() == level.lower()]

        if not relevant_content:
            # If no exact match found, try just matching topic
            relevant_content = [item for item in self.knowledge if item['topic'].lower() == topic.lower()]

        if not relevant_content:
            # Still no match, use first few items from knowledge base as fallback
            logger.warning(f"No content available for {topic}. Using generic content.")
            if self.knowledge:
                relevant_content = self.knowledge[:3]  # Use first 3 items
            else:
                return self._create_minimal_course(topic, level)

        course = {
            "title": f"{topic.title()} - {level.title()} Course",
            "description": f"Comprehensive {level} course on {topic} with AI Course Generator content",
            "topic": topic,
            "level": level,
            "modules": [],
            "resources": []
        }

        try:
            # Organize content into logical modules
            modules = self._organize_content(relevant_content)

            for i, module_content in enumerate(modules, 1):
                try:
                    module = self._create_module(module_content, i, topic, level)
                    module["order"] = i  # Add explicit order for database
                    course["modules"].append(module)
                    if "resources" in module:
                        course["resources"].extend(module["resources"])
                except Exception as module_error:
                    logger.error(f"Error creating module {i}: {str(module_error)}")
                    # Add a minimal module as fallback
                    course["modules"].append(self._create_minimal_module(i, topic, level))
        except Exception as e:
            logger.error(f"Error organizing content: {str(e)}")
            # Add a minimal module as fallback
            course["modules"].append(self._create_minimal_module(1, topic, level))

        # Save to database if requested
        if save_to_db and self.db_manager:
            try:
                course_id = self._save_course_to_db(course)
                course["_id"] = course_id
            except Exception as db_error:
                logger.error(f"Error saving to database: {str(db_error)}")

        return course

    def _create_minimal_course(self, topic: str, level: str) -> Dict:
        """Create a minimal course when knowledge base is empty or has errors"""
        course = {
            "title": f"{topic.title()} - {level.title()} Course",
            "description": f"Introduction to {topic} for {level} learners",
            "topic": topic,
            "level": level,
            "modules": [self._create_minimal_module(1, topic, level)],
            "resources": []
        }
        return course

    def _create_minimal_module(self, module_num: int, topic: str, level: str) -> Dict:
        """Create a minimal module when errors occur"""
        module = {
            "title": f"Module {module_num}: Introduction to {topic.title()}",
            "introduction": self.templates['module']['introduction'].format(topic=topic, level=level),
            "summary": self.templates['module']['summary'].format(topic=topic, level=level),
            "sections": [],
            "resources": [],
            "units": []
        }

        # Create a single basic section
        section = {
            "title": f"Getting Started with {topic.title()}",
            "content": {
                "explanation": f"This section introduces the basic concepts of {topic}. You'll learn the fundamental principles and how to start working with {topic}.",
                "examples": [f"Example code and demonstrations for {topic} will be shown here."],
                "exercise": f"Practice exercises for {topic} will be provided here."
            },
            "resources": [],
            "order": 1
        }

        module["sections"].append(section)

        # Create a basic unit for database
        unit = {
            "title": f"Introduction to {topic.title()}",
            "type": "explanation",
            "content": {"text": section["content"]["explanation"]},
            "resources": [],
            "order": 1
        }

        module["units"].append(unit)

        return module

    def _organize_content(self, content: List[Dict]) -> List[List[Dict]]:
        """Organize content into logical learning modules with error handling"""
        try:
            # If we have very little content, just put it all in one module
            if len(content) <= 3:
                return [content]

            # Enhanced organization with topic clustering
            from collections import defaultdict

            # Group by subtopics using title keywords
            topic_groups = defaultdict(list)

            for item in content:
                # Extract key topic words from title
                title_words = set(re.findall(r'\b\w{4,}\b', item['title'].lower()))

                # Find best group or create new one
                best_group = None
                max_overlap = 0

                for group_name, group_items in topic_groups.items():
                    group_words = set(re.findall(r'\b\w{4,}\b', group_name.lower()))
                    overlap = len(title_words.intersection(group_words))

                    if overlap > max_overlap and len(group_items) < 4:  # Limit group size
                        max_overlap = overlap
                        best_group = group_name

                if best_group and max_overlap > 0:
                    topic_groups[best_group].append(item)
                else:
                    topic_groups[item['title']].append(item)

            # Merge small groups if needed
            result = []
            temp_group = []

            for group_items in topic_groups.values():
                if len(temp_group) + len(group_items) <= 4:
                    temp_group.extend(group_items)
                else:
                    if temp_group:
                        result.append(temp_group)
                    temp_group = group_items

            if temp_group:
                result.append(temp_group)

            return result
        except Exception as e:
            logger.error(f"Error organizing content: {str(e)}")
            # Fallback: return content as a single module
            return [content] if content else [[]]

    def _create_module(self, content: List[Dict], module_num: int, topic: str, level: str) -> Dict:
        """Create an AI-enhanced learning module with improved error handling"""
        # Ensure we have content to work with
        if not content:
            return self._create_minimal_module(module_num, topic, level)

        try:
            # Determine a better module title
            common_words = self._find_common_words([item["title"] for item in content]) if content else []
            module_title = f"Module {module_num}: {' '.join(common_words).title()}" if common_words else f"Module {module_num}: {content[0]['title'] if content else 'Introduction'}"

            module = {
                "title": module_title,
                "sections": [],
                "resources": [],
                "units": []  # For database structure
            }

            # Module introduction
            module["introduction"] = self.templates['module']['introduction'].format(
                topic=topic,
                level=level
            )

            # Add sections for each content item
            for i, item in enumerate(content, 1):
                try:
                    section = self._create_section(item, topic, i)
                    module["sections"].append(section)
                    if "resources" in section:
                        module["resources"].extend(section["resources"])

                    # Create units (for database)
                    if "content" in section:
                        module["units"].extend(self._create_units_from_section(section))
                except Exception as section_error:
                    logger.error(f"Error creating section {i}: {str(section_error)}")
                    # Add a minimal section as fallback
                    minimal_section = {
                        "title": f"Section {i}: {item.get('title', 'Content')}",
                        "content": {
                            "explanation": f"Content for {item.get('title', 'this section')}.",
                            "examples": [],
                            "exercise": "Practice exercises will be provided here."
                        },
                        "resources": [{"title": item.get("title", "Resource"), "url": item.get("url", "")}],
                        "order": i
                    }
                    module["sections"].append(minimal_section)
                    module["resources"].extend(minimal_section["resources"])
                    module["units"].extend(self._create_units_from_section(minimal_section))

            # Module summary
            module["summary"] = self.templates['module']['summary'].format(
                topic=topic,
                level=level
            )

            return module
        except Exception as e:
            logger.error(f"Error creating module: {str(e)}")
            return self._create_minimal_module(module_num, topic, level)

    def _create_section(self, item: Dict, topic: str, order: int) -> Dict:
        """Create a section with proper error handling"""
        try:
            section = {
                "title": item.get("title", f"Section {order}"),
                "content": self._enhance_section(item, topic),
                "resources": [{"title": item.get("title", "Resource"), "url": item.get("url", "")}],
                "order": order
            }
            return section
        except Exception as e:
            logger.error(f"Error in _create_section: {str(e)}")
            # Return minimal section
            return {
                "title": item.get("title", f"Section {order}"),
                "content": {
                    "explanation": f"Content about {item.get('title', 'this topic')}.",
                    "examples": [],
                    "exercise": "Practice exercises will be provided here."
                },
                "resources": [{"title": item.get("title", "Resource"), "url": item.get("url", "")}],
                "order": order
            }

    def _find_common_words(self, titles: List[str]) -> List[str]:
        """Find common significant words across titles"""
        if not titles:
            return []

        # Extract words and count frequencies
        word_freq = defaultdict(int)
        stop_words = {'and', 'the', 'in', 'on', 'of', 'for', 'with', 'a', 'to', 'from', 'by'}

        for title in titles:
            words = re.findall(r'\b\w{3,}\b', title.lower())
            for word in words:
                if word not in stop_words:
                    word_freq[word] += 1

        # Find words that appear in at least half of titles
        threshold = max(1, len(titles) // 2)
        common = [word for word, freq in word_freq.items() if freq >= threshold]

        return common[:3]  # Return top 3 common words

    def _create_units_from_section(self, section: Dict) -> List[Dict]:
        """Create database units from a section"""
        units = []

        # Explanation unit
        units.append({
            "title": section["title"],
            "type": "explanation",
            "content": {"text": section["content"]["explanation"]},
            "resources": section["resources"],
            "order": 1
        })

        # Example units
        for i, example in enumerate(section["content"]["examples"], 2):
            units.append({
                "title": f"{section['title']} - Example {i-1}",
                "type": "example",
                "content": {"text": example},
                "resources": [],
                "order": i
            })

        # Exercise unit
        units.append({
            "title": f"{section['title']} - Exercise",
            "type": "exercise",
            "content": {"text": section["content"]["exercise"]},
            "resources": [],
            "order": len(section["content"]["examples"]) + 2
        })

        return units

    def _enhance_section(self, content: Dict, topic: str) -> Dict:
        """Enhance a content section with AI-generated material"""
        try:
            # Generate AI-enhanced explanations
            ai_explanation = self.ai_enhancer.enhance_content(
                f"Explain {content['title']} in {content['level']} terms: {content['content']}",
                'explanation'
            )

            # Generate key points
            key_points = self.ai_enhancer.enhance_content(
                f"Extract 3 key points about {content['title']} from: {content['content']}",
                'explanation'
            )

            # Generate analogy
            analogy = self.ai_enhancer.enhance_content(
                f"Create a real-world analogy for {content['title']}",
                'explanation'
            )

            # Prepare examples
            examples = []
            for i, code in enumerate(content.get("code_examples", [])[:2], 1):
                example_exp = self.ai_enhancer.enhance_content(
                    f"Explain this {topic} code example: {code}",
                    'example'
                )
                suggestion = self.ai_enhancer.enhance_content(
                    f"Suggest a modification for this {topic} code: {code}",
                    'example'
                )

                examples.append({
                    "title": f"Example {i}",
                    "code": code,
                    "explanation": example_exp,
                    "suggestion": suggestion,
                    "language": topic.lower() if topic.lower() in ["python", "javascript"] else "python"
                })

            # Generate exercise
            exercise = {
                "title": f"Practice {content['title']}",
                "objective": self.ai_enhancer.enhance_content(
                    f"Create a learning objective for practicing {content['title']}",
                    'exercise'
                ),
                "requirements": self.ai_enhancer.enhance_content(
                    f"List requirements for an exercise about {content['title']}",
                    'exercise'
                ),
                "steps": self.ai_enhancer.enhance_content(
                    f"Provide steps to solve an exercise about {content['title']}",
                    'exercise'
                ),
                "hints": self.ai_enhancer.enhance_content(
                    f"Give helpful hints for solving an exercise about {content['title']}",
                    'exercise'
                )
            }

            return {
                "explanation": self.templates['module']['section']['explanation'].format(
                    title=content["title"],
                    ai_enhanced_explanation=ai_explanation,
                    key_points=key_points,
                    analogy=analogy
                ),
                "examples": [
                    self.templates['module']['section']['example'].format(
                        title=ex["title"],
                        code=ex["code"],
                        language=ex["language"],
                        ai_enhanced_explanation=ex["explanation"],
                        suggestion=ex["suggestion"]
                    ) for ex in examples
                ],
                "exercise": self.templates['module']['section']['exercise'].format(
                    title=exercise["title"],
                    objective=exercise["objective"],
                    requirements=exercise["requirements"],
                    steps=exercise["steps"],
                    hints=exercise["hints"]
                )
            }
        except ValueError as e:
            # Handle the "too many values to unpack" error
            logger.error(f"Error in _enhance_section: {str(e)}")
            # Return a simplified section with placeholder content
            return {
                "explanation": f"## {content.get('title', 'Topic')}\n\nThis section covers important concepts related to {content.get('title', 'this topic')}.",
                "examples": [f"### Example\n\nExample code for {content.get('title', 'this topic')} would be shown here."],
                "exercise": f"### Exercise\n\nPractice what you've learned about {content.get('title', 'this topic')} with this exercise."
            }
        except Exception as e:
            logger.error(f"Error in _enhance_section: {str(e)}")
            # Return a simplified section with placeholder content
            return {
                "explanation": f"## {content.get('title', 'Topic')}\n\nThis section covers important concepts related to {content.get('title', 'this topic')}.",
                "examples": [f"### Example\n\nExample code for {content.get('title', 'this topic')} would be shown here."],
                "exercise": f"### Exercise\n\nPractice what you've learned about {content.get('title', 'this topic')} with this exercise."
            }

    def _save_course_to_db(self, course: Dict) -> str:
        """Save course, modules and units to MongoDB"""
        if not self.db_manager:
            logger.warning("No database manager available, course not saved")
            return None

        try:
            course_data = {
                "title": course["title"],
                "description": course["description"],
                "topic_id": course.get("topic_id", 1),  # placeholder or resolve actual topic_id
                "difficulty_id": self.level_map.get(self.level.lower(), 1),  # placeholder or resolve actual difficulty
                "completion_time": course.get("completion_time", 40),
                "modules": []
            }

            for i, module in enumerate(course.get("modules", []), start=1):
                module_data = {
                    "module_id": i,
                    "module_order": module.get("order", i),
                    "title": module["title"],
                    "description": module.get("introduction", ""),  # using 'introduction' as description
                    "units": []
                }

                for j, unit in enumerate(module.get("units", []), start=1):
                    unit_data = {
                        "unit_id": j,
                        "unit_order": unit.get("order", j),
                        "title": unit["title"],
                        "description": unit.get("summary", ""),
                        "type": unit.get("type", "explanation"),
                        "body": unit.get("content", "")
                    }
                    module_data["units"].append(unit_data)

                course_data["modules"].append(module_data)

            course_id = self.db_manager.store_course(course_data)
            logger.info(f"Saved course with ID {course_id} to database")
            return course_id

        except Exception as e:
            logger.error(f"Error saving course to database: {str(e)}")
            return None

    def export_markdown(self, course: Dict, filename: str = None) -> str:
        """Export course to beautifully formatted Markdown"""
        if not filename:
            filename = f"{course['title'].replace(' ', '_')}.md"

        md = f"# {course['title']}\n\n"
        md += f"*{course['description']}*\n\n"

        for i, module in enumerate(course["modules"], 1):
            md += f"## {module['title']}\n\n"
            md += f"{module['introduction']}\n\n"

            for section in module["sections"]:
                md += f"### {section['title']}\n\n"
                md += f"{section['content']['explanation']}\n\n"

                if section['content']['examples']:
                    md += "### Examples\n\n"
                    for example in section['content']['examples']:
                        md += f"{example}\n\n"

                md += f"### Exercise\n\n"
                md += f"{section['content']['exercise']}\n\n"
                md += "---\n\n"

            md += f"{module['summary']}\n\n"

        md += "## Course Resources\n\n"
        for resource in course["resources"]:
            if resource["url"]:
                md += f"- [{resource['title']}]({resource['url']})\n"
            else:
                md += f"- {resource['title']}\n"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)

        logger.info(f"Course saved to {filename}")
        return md

    def get_course_from_db(self, course_id: str) -> Dict:
        """Retrieve a course from the database

        Args:
            course_id: MongoDB ID of the course

        Returns:
            Dict: Complete course data
        """
        if not self.db_manager:
            logger.warning("No database manager available")
            return None

        try:
            return self.db_manager.get_full_course(course_id)
        except Exception as e:
            logger.error(f"Error retrieving course: {str(e)}")
            return None

    def list_courses_from_db(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """List courses from the database with pagination"""
        if not self.db_manager:
            logger.warning("No database manager available")
            return []

        try:
            return self.db_manager.list_courses(limit, offset)
        except Exception as e:
            logger.error(f"Error listing courses: {str(e)}")
            return []

    def search_courses_in_db(self, query: str) -> List[Dict]:
        """Search for courses in the database"""
        if not self.db_manager:
            logger.warning("No database manager available")
            return []

        try:
            return self.db_manager.search_courses(query)
        except Exception as e:
            logger.error(f"Error searching courses: {str(e)}")
            return []