
'''Ways to impprove:
    1. Caching to avoid regenerating similar content
    2. Content enhancement validation.
    3. Batch content generation.
'''
from course_gen.core.globals import (
    logger, re, Dict, List, defaultdict, Optional, uuid, datetime, np
)

from .content_enhancer import AIContentEnhancer
from .database_manager import DatabaseManager
from course_gen.utils.file_manager import FileManager
from course_gen.core import (COURSE_TEMPLATE, LEVEL_MAP)

class CourseGenerator:
    """Advanced AI-powered course generator with dynamic content and MongoDB storage"""
    def __init__(self, knowledge_file: str = "knowledge_base.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = FileManager.load_knowledge(knowledge_file)
        self.ai_enhancer = AIContentEnhancer()
        self.db_manager = DatabaseManager()
        
        # Course difficulty levels mapping with progressive learning paths
        self.level_map = LEVEL_MAP
        
        # Load course templates
        self.templates = COURSE_TEMPLATE

    def generate_course(self, topic: str, level: str = "beginner", 
                         modules_count: int = 5,
                         instructor_notes: Optional[str] = None,
                         syllabus_outline: Optional[List[str]] = None,
                         save_to_db: bool = False) -> Dict:
        """Generate a comprehensive long-form course

        Args:
            topic: Course topic
            level: Course difficulty level (beginner, intermediate, advanced, expert)
            modules_count: Target number of modules to generate
            instructor_notes: Optional instructor notes to guide content generation
            syllabus_outline: Optional list of topics to include in syllabus
            save_to_db: Whether to save the course to MongoDB

        Returns:
            Dict: Generated course data or error message
        """
        start_time = datetime.now()
        logger.info(f"Starting course generation for {topic} ({level}) at {start_time}")
        
        # Validate level
        if level not in self.level_map:
            logger.warning(f"Invalid level '{level}'. Defaulting to 'beginner'")
            level = "beginner"
        
        # Ensure we have a knowledge base to work with
        if not self.knowledge:
            logger.warning("No knowledge items found - generating a synthetic course")
            course = self._create_synthetic_course(topic, level, modules_count,  
                                                 instructor_notes, syllabus_outline)
            return course

        # Find relevant content in knowledge base
        relevant_content = self._find_relevant_content(topic, level)
        
        if not relevant_content:
            logger.warning(f"No content available for {topic}. Generating synthetic content.")
            course = self._create_synthetic_course(topic, level, modules_count, 
                                                 instructor_notes, syllabus_outline)
            return course

        # Initialize course structure
        course = self._initialize_course_structure(topic, level, relevant_content, 
                                                  instructor_notes, syllabus_outline)

        try:
            # Generate course introduction with AI enhancement
            course["introduction"] = self._generate_course_introduction(topic, level, relevant_content, 
                                                                      syllabus_outline)
            
            # Organize content into logical modules
            organized_modules = self._organize_content(relevant_content, modules_count)
            
            # Create modules
            for i, module_content in enumerate(organized_modules, 1):
                try:
                    logger.info(f"Generating module {i} of {len(organized_modules)}")
                    module = self._create_module(module_content, i, topic, level)
                    module["order"] = i
                    course["modules"].append(module)
                    if "resources" in module:
                        course["resources"].extend(module["resources"])
                except Exception as module_error:
                    logger.error(f"Error creating module {i}: {str(module_error)}")
                    # Add a fallback module
                    course["modules"].append(self._create_minimal_module(i, topic, level))
            
            # Generate course conclusion
            course["conclusion"] = self._generate_course_conclusion(topic, level, course["modules"])
            
            # Generate metadata
            course["metadata"] = {
                "creation_date": datetime.now().isoformat(),
                "version": "1.0",
                "generator": "CourseGenerator",
                "course_id": str(uuid.uuid4()),
                "level": level,
                "modules_count": len(course["modules"]),
                "total_sections": sum(len(m.get("sections", [])) for m in course["modules"])            }
            
        except Exception as e:
            logger.error(f"Error generating course: {str(e)}")
            # Add a minimal module as fallback
            if not course["modules"]:
                course["modules"].append(self._create_minimal_module(1, topic, level))

        # Save to database if requested
        if save_to_db and self.db_manager:
            try:
                course_id = self._save_course_to_db(course)
                course["_id"] = course_id
                logger.info(f"Course saved to database with ID: {course_id}")
            except Exception as db_error:
                logger.error(f"Error saving to database: {str(db_error)}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Course generation completed in {duration:.2f} seconds")
        
        return course
    
    def _find_relevant_content(self, topic: str, level: str) -> List[Dict]:
        """Find relevant content from knowledge base with expanded search strategies"""
        # Try exact match first
        exact_matches = [item for item in self.knowledge
                       if item['topic'].lower() == topic.lower()
                       and item['level'].lower() == level.lower()]
        
        if exact_matches:
            return exact_matches
        
        # Try topic match at any level
        topic_matches = [item for item in self.knowledge 
                       if item['topic'].lower() == topic.lower()]
        
        if topic_matches:
            return topic_matches
            
        # Try keyword matching - find partial matches in topic and title
        keyword_matches = []
        topic_words = set(topic.lower().split())
        
        for item in self.knowledge:
            item_topic_words = set(item['topic'].lower().split())
            title_words = set(item['title'].lower().split())
            
            intersection_score = len(topic_words & (item_topic_words | title_words))
            if intersection_score > 0:
                item['match_score'] = intersection_score  # Add match score for sorting
                keyword_matches.append(item)
        
        if keyword_matches:
            # Sort by match score (highest first)
            return sorted(keyword_matches, key=lambda x: x.get('match_score', 0), reverse=True)
        
        # If still nothing, return a sample from knowledge base
        if self.knowledge:
            return self.knowledge[:min(10, len(self.knowledge))]
        
        return []
    
    def _initialize_course_structure(self, topic: str, level: str, 
                                    relevant_content: List[Dict], 
                                    instructor_notes: Optional[str] = None,
                                    syllabus_outline: Optional[List[str]] = None) -> Dict:
        """Initialize comprehensive course structure"""
        # Generate a better course title
        course_title = self._generate_course_title(topic, level, relevant_content)
        
        course = {
            "title": course_title,
            "topic": topic,
            "level": level,
            "modules": [],
            "resources": [],
            "instructor_notes": instructor_notes or "",
            "syllabus_outline": syllabus_outline or []
        }
        
        return course
    
    def _generate_course_title(self, topic: str, level: str, 
                              relevant_content: List[Dict]) -> str:
        """Generate an engaging course title"""
        try:
            title_prompt = f"Create an engaging title for a {level} course on {topic}"
            if relevant_content:
                sample_titles = [item.get('title', '') for item in relevant_content[:3]]
                title_prompt += f" considering these related topics: {', '.join(sample_titles)}"
            
            ai_title = self.ai_enhancer.enhance_content(title_prompt, 'title')
            
            # Clean up the title - remove quotes if present
            ai_title = ai_title.strip('"\'')
            
            # Fallback if AI title is too long or empty
            if len(ai_title) > 70 or not ai_title:
                return f"{topic.title()}: Comprehensive {level.title()} Course"
                
            return ai_title
        except Exception as e:
            logger.error(f"Error generating course title: {str(e)}")
            return f"{topic.title()}: {level.title()} Course"

    def _generate_course_introduction(self, topic: str, level: str, 
                                     relevant_content: List[Dict],
                                     syllabus_outline: Optional[List[str]] = None) -> str:
        """Generate comprehensive course introduction with AI enhancement"""
        try:
            # Generate AI-enhanced course description
            description_prompt = (
                f"Write a comprehensive introduction to a {level} course on {topic}. "
                f"Include why this topic is important and what students will gain."
            )
            ai_description = self.ai_enhancer.enhance_content(description_prompt, 'description')
            
            # Generate learning objectives
            objectives_prompt = (
                f"Create 5-7 specific learning objectives for a {level} course on {topic}. "
                f"Use measurable action verbs and focus on skills development."
            )
            learning_objectives = self.ai_enhancer.enhance_content(objectives_prompt, 'objectives')
            
            # Generate prerequisites
            prerequisites_prompt = (
                f"List the prerequisites for a {level} course on {topic}. "
                f"Include required knowledge, skills, and tools."
            )
            prerequisites = self.ai_enhancer.enhance_content(prerequisites_prompt, 'prerequisites')
            
            # Generate structure overview
            structure_prompt = (
                f"Outline the structure for a {level} course on {topic}. "
                f"Include module progression and learning path."
            )
            if syllabus_outline:
                structure_prompt += f" Incorporate these topics: {', '.join(syllabus_outline)}"
                
            structure_overview = self.ai_enhancer.enhance_content(structure_prompt, 'structure')
            
            # Generate learning path
            learning_path_prompt = (
                f"Describe the learning path from beginning to end for a {level} course on {topic}. "
                f"How will concepts build on each other?"
            )
            learning_path = self.ai_enhancer.enhance_content(learning_path_prompt, 'learning_path')
            
            # Format the introduction
            return self.templates['course']['introduction'].format(
                title=topic.title(),
                ai_enhanced_description=ai_description,
                learning_objectives=learning_objectives,
                prerequisites=prerequisites,
                level=level,
                topic=topic,
                structure_overview=structure_overview,
                learning_path=learning_path
            )
            
        except Exception as e:
            logger.error(f"Error generating course introduction: {str(e)}")
            # Return a simplified introduction
            return (
                f"# {topic.title()}: {level.title()} Course\n\n"
                f"Welcome to this comprehensive {level} course on {topic}!\n\n"
                f"## Course Objectives\n\n"
                f"- Understand key concepts of {topic}\n"
                f"- Apply {topic} principles to real-world problems\n"
                f"- Develop practical skills in {topic}\n\n"
                f"## Prerequisites\n\n"
                f"Basic understanding of related concepts is recommended.\n\n"
                f"## Course Structure\n\n"
                f"This course is divided into several modules, each focusing on different aspects of {topic}."
            )

    def _generate_course_conclusion(self, topic: str, level: str, modules: List[Dict]) -> str:
        """Generate comprehensive course conclusion"""
        try:
            # Extract module titles for context
            module_titles = [module.get("title", f"Module {i}") 
                           for i, module in enumerate(modules, 1)]
            
            # Generate key learnings
            key_learnings_prompt = (
                f"Summarize 5-8 key learnings from a {level} course on {topic} "
                f"covering: {', '.join(module_titles[:5])}"
            )
            key_learnings = self.ai_enhancer.enhance_content(key_learnings_prompt, 'key_learnings')
            
            # Generate next steps
            next_level = self._get_next_level(level)
            next_steps_prompt = (
                f"Suggest next steps for continued learning after completing a {level} "
                f"course on {topic}. Include project ideas and {next_level} topics."
            )
            next_steps = self.ai_enhancer.enhance_content(next_steps_prompt, 'next_steps')
            
            # Format the conclusion
            return self.templates['course']['conclusion'].format(
                level=level,
                topic=topic,
                key_learnings=key_learnings,
                next_steps=next_steps
            )
            
        except Exception as e:
            logger.error(f"Error generating course conclusion: {str(e)}")
            # Return a simplified conclusion
            return (
                f"# Course Conclusion\n\n"
                f"Congratulations on completing this {level} course on {topic}!\n\n"
                f"## Key Takeaways\n\n"
                f"You've learned the fundamentals of {topic} and how to apply them.\n\n"
                f"## Next Steps\n\n"
                f"Consider working on practical projects to further solidify your knowledge."
            )

    def _get_next_level(self, current_level: str) -> str:
        """Get the next difficulty level"""
        levels = ["beginner", "intermediate", "advanced", "expert"]
        try:
            current_index = levels.index(current_level.lower())
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
            return "mastery"
        except (ValueError, IndexError):
            return "advanced"

    def _create_synthetic_course(self, topic: str, level: str, 
                                modules_count: int,
                                instructor_notes: Optional[str] = None,
                                syllabus_outline: Optional[List[str]] = None) -> Dict:
        """Create a synthetic course when knowledge base is empty or irrelevant"""
        course = self._initialize_course_structure(topic, level, [], instructor_notes, syllabus_outline)
        
        # Generate course introduction
        course["introduction"] = self._generate_course_introduction(topic, level, [], syllabus_outline)
        
        # Generate synthetic modules
        for i in range(1, modules_count + 1):
            try:
                # Generate a module title based on syllabus if available
                if syllabus_outline and i <= len(syllabus_outline):
                    module_topic = syllabus_outline[i-1]
                    module_title = f"Module {i}: {module_topic}"
                else:
                    # Ask AI to generate a relevant module topic
                    module_topic_prompt = (
                        f"Suggest a title for module {i} of {modules_count} "
                        f"in a {level} course on {topic}"
                    )
                    module_title = self.ai_enhancer.enhance_content(module_topic_prompt, 'title')
                    module_title = f"Module {i}: {module_title.strip('\"')}"
                
                # Create synthetic module content
                module_content = [{
                    "title": module_title.split(": ", 1)[1] if ": " in module_title else module_title,
                    "topic": topic,
                    "level": level,
                    "content": f"Content for {module_title}",
                    "code_examples": [
                        f"Example code 1 for {topic}",
                        f"Example code 2 for {topic}"
                    ]
                }]
                
                # Create module
                module = self._create_module(module_content, i, topic, level)
                module["order"] = i
                course["modules"].append(module)
                
            except Exception as module_error:
                logger.error(f"Error creating synthetic module {i}: {str(module_error)}")
                course["modules"].append(self._create_minimal_module(i, topic, level))
        
        # Generate course conclusion
        course["conclusion"] = self._generate_course_conclusion(topic, level, course["modules"])
        
        # Generate metadata
        course["metadata"] = {
            "creation_date": datetime.now().isoformat(),
            "version": "1.0",
            "generator": "CourseGenerator (Synthetic)",
            "course_id": str(uuid.uuid4()),
            "level": level,
            "modules_count": len(course["modules"]),
            "total_sections": sum(len(m.get("sections", [])) for m in course["modules"]),
            "generated_type": "synthetic"
        }
        
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
            "modules": [],
            "units": [],
            "resources": []
        }

        # Create a single basic section
        section = {
            "title": f"Getting Started with {topic.title()}",
            "content": {
                "explanation": f"This section introduces the basic concepts of {topic}. You'll learn the fundamental principles and how to start working with {topic}.",
                "examples": [f"Example code and demonstrations for {topic} will be shown here."],
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

    def _organize_content(self, content: List[Dict], target_modules: int) -> List[List[Dict]]:
        """Organize content into logical learning modules with progressive difficulty"""
        try:
            # If we have very little content, just put it all in one module
            if len(content) <= 3:
                return [content]
                
            # If we have exactly what we need for the target modules
            if target_modules == 1:
                return [content]

            # First group by subtopics
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

                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_group = group_name

                if best_group and max_overlap > 0:
                    topic_groups[best_group].append(item)
                else:
                    topic_groups[item['title']].append(item)
                    
            # Sort groups by complexity/difficulty if possible
            sorted_groups = []
            groups = list(topic_groups.values())
            
            # Try to determine difficulty level for each group
            group_difficulties = []
            level_scores = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
            
            for group_items in groups:
                # Use the average difficulty level in the group
                avg_difficulty = sum(level_scores.get(item.get('level', 'beginner').lower(), 1) 
                                   for item in group_items) / len(group_items)
                group_difficulties.append(avg_difficulty)
                
            # Sort groups by difficulty score (easier topics first)
            sorted_indices = np.argsort(group_difficulties)
            for idx in sorted_indices:
                sorted_groups.append(groups[idx])
                
            # Adjust number of modules if we don't have enough content
            actual_modules = min(target_modules, len(sorted_groups))
            if actual_modules < target_modules:
                logger.warning(f"Only generated {actual_modules} modules instead of requested {target_modules}")
                
            # If we have more groups than target modules, merge some groups
            if len(sorted_groups) > actual_modules:
                # Calculate how many groups to merge into each module
                groups_per_module = len(sorted_groups) // actual_modules
                remainder = len(sorted_groups) % actual_modules
                
                result = []
                start_idx = 0
                
                for i in range(actual_modules):
                    # Calculate how many groups go in this module (distribute remainder)
                    module_groups = groups_per_module + (1 if i < remainder else 0)
                    end_idx = start_idx + module_groups
                    
                    # Flatten the groups for this module
                    module_items = []
                    for j in range(start_idx, min(end_idx, len(sorted_groups))):
                        module_items.extend(sorted_groups[j])
                    
                    result.append(module_items)
                    start_idx = end_idx
                
                return result
            else:
                # We have fewer groups than modules, so each group is a module
                # and we might have fewer modules than requested
                return sorted_groups
            
        except Exception as e:
            logger.error(f"Error creating module: {str(e)}")
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
                            "examples": []
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

        return units
    
    def _generate_module_title(self, content: List[Dict], module_num: int, topic: str) -> str:
        """Generate an appropriate module title based on content"""
        try:
            # Try to extract common words across content items
            common_words = self._find_common_words([item.get("title", "") for item in content]) if content else []
            
            if common_words:
                return f"Module {module_num}: {' '.join(common_words).title()}"
            elif content and "title" in content[0]:
                return f"Module {module_num}: {content[0]['title']}"
            else:
                # Generate a title with AI
                title_prompt = f"Generate a title for module {module_num} of a course on {topic}"
                ai_title = self.ai_enhancer.enhance_content(title_prompt, 'title')
                return f"Module {module_num}: {ai_title.strip('\"')}"
        except Exception as e:
            logger.error(f"Error generating module title: {str(e)}")
            return f"Module {module_num}: {topic.title()} Concepts"
    
    def _extract_section_topics(self, module_outline: str, num_topics: int) -> List[str]:
        """Extract potential section topics from a module outline"""
        try:
            # Try to find bullet points or numbered list items
            topics = re.findall(r'[-*•]?\s*(\w[^•\n]*?)(?=\n|$)', module_outline)
            
            # If we found enough topics, use them
            if len(topics) >= num_topics:
                return topics[:num_topics]
                
            # Otherwise try to find sentences that might be topics
            sentences = re.split(r'(?<=[.!?])\s+', module_outline)
            topics = [s.strip() for s in sentences if 3 <= len(s.split()) <= 8 and len(s) > 10]
            
            if topics:
                return topics[:num_topics]
                
            # Fallback: just generate generic topics
            return [f"Topic {i+1}" for i in range(num_topics)]
            
        except Exception as e:
            logger.error(f"Error extracting section topics: {str(e)}")
            return [f"Topic {i+1}" for i in range(num_topics)]

    def _create_section(self, item: Dict, topic: str, order: int, 
                       section_type: str = "explanation", level: str = "beginner") -> Dict:
        """Create a specialized section based on section type"""
        try:
            section = {
                "title": item.get("title", f"Section {order}"),
                "type": section_type,
                "content": self._generate_section_content(item, topic, section_type, level),
                "resources": [
                    {"title": item.get("title", "Resource"), "url": item.get("url", "")}
                ],
                "order": order
            }
            
            return section
        except Exception as e:
            logger.error(f"Error in _create_section: {str(e)}")
            # Return minimal section
            return {
                "title": item.get("title", f"Section {order}"),
                "type": "explanation",
                "content": {
                    "explanation": f"Content about {item.get('title', 'this topic')}.",
                    "examples": []
                },
                "resources": [{"title": item.get("title", "Resource"), "url": item.get("url", "")}],
                "order": order
            }

    def _generate_section_content(self, content: Dict, topic: str, 
                                section_type: str, level: str) -> Dict:
        """Generate comprehensive content for different section types"""
        try:
            # Base content to work with
            content_text = content.get('content', f"Content about {content.get('title', topic)}")
            section_title = content.get('title', topic)
            
            # Generate content based on section type
            if section_type == "explanation":
                return self._generate_explanation_content(content_text, section_title, topic, level)
            elif section_type == "example":
                return self._generate_example_content(content, section_title, topic, level)
            elif section_type == "case_study":
                return self._generate_case_study_content(content_text, section_title, topic, level)
            else:
                # Default to explanation
                return self._generate_explanation_content(content_text, section_title, topic, level)
                
        except Exception as e:
            logger.error(f"Error generating section content: {str(e)}")
            # Return simplified content
            return {
                "explanation": f"## {content.get('title', 'Topic')}\n\nContent about {content.get('title', 'this topic')}.",
                "examples": [f"### Example\n\nExample for {content.get('title', 'this topic')}"],
            }
            
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
                ]
            }
            
        except ValueError as e:
            # Handle the "too many values to unpack" error
            logger.error(f"Error in _enhance_section: {str(e)}")
            # Return a simplified section with placeholder content
            return {
                "explanation": f"## {content.get('title', 'Topic')}\n\nThis section covers important concepts related to {content.get('title', 'this topic')}.",
                "examples": [f"### Example\n\nExample code for {content.get('title', 'this topic')} would be shown here."]            }
        except Exception as e:
            logger.error(f"Error in _enhance_section: {str(e)}")
            # Return a simplified section with placeholder content
            return {
                "explanation": f"## {content.get('title', 'Topic')}\n\nThis section covers important concepts related to {content.get('title', 'this topic')}.",
                "examples": [f"### Example\n\nExample code for {content.get('title', 'this topic')} would be shown here."],
            }

    def _generate_explanation_content(self, content_text: str, 
                                     section_title: str, topic: str, level: str) -> Dict:
        """Generate comprehensive explanation content"""
        try:
            # Generate AI-enhanced explanations
            ai_explanation = self.ai_enhancer.enhance_content(
                f"Write a comprehensive explanation of '{section_title}' for {level} students. "
                f"Context: {content_text[:500]}",
                'explanation'
            )

            # Generate key points
            key_points = self.ai_enhancer.enhance_content(
                f"Extract 4-5 key points about '{section_title}' that {level} students should understand",
                'explanation'
            )

            # Generate real-world application
            real_world = self.ai_enhancer.enhance_content(
                f"Explain a real-world application of '{section_title}' with practical examples",
                'explanation'
            )
            
            # Generate conceptual model
            conceptual_model = self.ai_enhancer.enhance_content(
                f"Create a conceptual model or framework to understand '{section_title}' for {level} students",
                'explanation'
            )
            
            # Generate common misconceptions
            misconceptions = self.ai_enhancer.enhance_content(
                f"Describe 2-3 common misconceptions about '{section_title}' and clarify them",
                'explanation'
            )

            return {
                "explanation": self.templates['module']['section']['explanation'].format(
                    title=section_title,
                    ai_enhanced_explanation=ai_explanation,
                    key_points=key_points,
                    real_world_application=real_world,
                    conceptual_model=conceptual_model,
                    misconceptions=misconceptions
                ),
                "examples": [],  # Handled in other sections
            }
        except Exception as e:
            logger.error(f"Error generating explanation content: {str(e)}")
            return {
                "explanation": f"## {section_title}\n\nThis section explains concepts related to {section_title}.",
                "examples": []
            }

    def _generate_example_content(self, content: Dict, section_title: str, 
                                topic: str, level: str) -> Dict:
        """Generate comprehensive example content with code"""
        examples_list = []
        
        try:
            # Get code examples from content or generate them
            code_examples = content.get("code_examples", [])
            
            # If no code examples provided, generate placeholder
            if not code_examples:
                code_examples = [f"# Example code for {section_title}\nprint('Hello World')"]
            
            # For each code example, create an enhanced example
            for i, code in enumerate(code_examples[:2], 1):
                # Generate problem statement
                problem_prompt = (
                    f"Create a clear problem statement for a {level} {topic} example about {section_title}"
                )
                problem_statement = self.ai_enhancer.enhance_content(problem_prompt, 'example')
                
                # Generate solution approach
                solution_prompt = (
                    f"Describe the approach to solve this {topic} problem: {problem_statement}"
                )
                solution_approach = self.ai_enhancer.enhance_content(solution_prompt, 'example')
                
                # Generate explanation
                explanation_prompt = (
                    f"Explain this {topic} code example in detail for {level} learners: {code}"
                )
                example_explanation = self.ai_enhancer.enhance_content(explanation_prompt, 'example')
                
                # Generate alternative approaches
                alternatives_prompt = (
                    f"Suggest alternative approaches to solve the same problem in {topic}"
                )
                alternative_approaches = self.ai_enhancer.enhance_content(alternatives_prompt, 'example')
                
                # Generate practice variation
                practice_prompt = (
                    f"Create a slight variation of this problem for students to practice: {problem_statement}"
                )
                practice_variation = self.ai_enhancer.enhance_content(practice_prompt, 'example')
                
                # Determine language for code formatting
                language = topic.lower() if topic.lower() in ["python", "javascript", "java", "c++", "ruby"] else "python"
                
                # Format the example
                example = self.templates['module']['section']['example'].format(
                    title=f"{section_title} Example {i}",
                    problem_statement=problem_statement,
                    solution_approach=solution_approach,
                    code=code,
                    language=language,
                    ai_enhanced_explanation=example_explanation,
                    alternative_approaches=alternative_approaches,
                    practice_variation=practice_variation
                )
                
                examples_list.append(example)
                
            return {
                "explanation": "",  # Handled in explanation section
                "examples": examples_list
            }
            
        except Exception as e:
            logger.error(f"Error generating example content: {str(e)}")
            return {
                "explanation": "",
                "examples": [f"### Example: {section_title}\n\nExample code and explanation would be shown here."]
            }

    def _generate_case_study_content(self, content_text: str, 
                                   section_title: str, topic: str, level: str) -> Dict:
        """Generate comprehensive case study content"""
        try:
            # Generate background
            background_prompt = (
                f"Write a background introduction for a case study on {section_title} in {topic}"
            )
            background = self.ai_enhancer.enhance_content(background_prompt, 'case_study')
            
            # Generate challenge
            challenge_prompt = (
                f"Describe a realistic challenge or problem related to {section_title} in {topic}"
            )
            challenge = self.ai_enhancer.enhance_content(challenge_prompt, 'case_study')
            
            # Generate analysis
            analysis_prompt = (
                f"Provide a thorough analysis of the challenge in this {section_title} case study"
            )
            analysis = self.ai_enhancer.enhance_content(analysis_prompt, 'case_study')
            
            # Generate solution
            solution_prompt = (
                f"Describe a detailed solution approach for the {section_title} case study challenge"
            )
            solution = self.ai_enhancer.enhance_content(solution_prompt, 'case_study')
            
            # Generate lessons learned
            lessons_prompt = (
                f"Extract key lessons learned from this {section_title} case study"
            )
            lessons_learned = self.ai_enhancer.enhance_content(lessons_prompt, 'case_study')
            
            # Generate discussion questions
            questions_prompt = (
                f"Create thought-provoking discussion questions based on this {section_title} case study"
            )
            discussion_questions = self.ai_enhancer.enhance_content(questions_prompt, 'case_study')
            
            # Format the case study
            case_study = self.templates['module']['section']['case_study'].format(
                title=section_title,
                background=background,
                challenge=challenge,
                analysis=analysis,
                solution=solution,
                lessons_learned=lessons_learned,
                discussion_questions=discussion_questions
            )
            
            return {
                "case_study": case_study,
                "explanation": "",  # This is a different section type
                "examples": []
            }
            
        except Exception as e:
            logger.error(f"Error generating case study content: {str(e)}")
            return {
                "case_study": f"## Case Study: {section_title}\n\nThis case study explores real-world applications of {section_title}.",
                "explanation": "",
                "examples": []
            }




###############################################################
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