#################################################################################
# Used in knowledge_scraper.py
# Header to use throughout searching
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
    
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    
    # Linux browsers
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

# Base headers with other required fields
BASE_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/"
}

# Look for code blocks in pre and code tags
CODE_SELECTORS = [
    "pre code",      
    "pre",           
    "code",           
    ".code", "#code", 
    ".highlight", ".syntax", ".sourceCode",     
    ".codehilite", ".prettyprint",             
    ".code-block", ".codeblock",             
    "div[class*='code']", "div[class*='Code']",
    "div[class*='syntax']", "div[class*='Syntax']",
    "div[class*='highlight']", "div[class*='Highlight']",
    "[class*='language-']",                     
    "[class*='hljs']",                                     
    "[data-lang]", 
]

# Advanced topics
ADVANCED_INDICATORS = [
    "advanced", "expert", "complex", "deep dive", "in-depth",
    "optimization", "performance tuning", "memory management",
    "architecture", "system design", "design pattern", "DDD",
    "microservice", "monolith to microservices", "event-driven",
    "distributed", "scalability", "high availability", "load balancing",
    "data structure", "graph", "tree", "dynamic programming",
    "greedy", "backtracking", "recursion", "time complexity", "big o",
    "multithreading", "threading", "parallelism", "concurrency",
    "asynchronous", "asyncio", "event loop", "race condition", "lock",
    "low-level", "bit manipulation", "assembly", "systems programming",
    "kernel", "device driver", "compiler", "interpreter"
]

# Basic topics
BASIC_INDICATORS = [
    "introduction", "intro", "getting started", "beginner", "for beginners",
    "basics", "basic", "start here", "step by step", "first steps",
    "easy", "simple", "quickstart", "tutorial", "learn",
    "how to", "guide", "walkthrough", "101", "zero to hero",
    "start coding", "hello world"
]

# Elements to remove from main content
ELEMENTS_TO_REMOVE = [
    'script', 'style', 'iframe', 'nav', 'footer', 
    'aside', 'form', 'button', 'input', 'select',
    'textarea', 'label', 'fieldset', 'legend',
    'noscript', 'svg', 'figure', 'img', 'video',
    'audio', 'source', 'track', 'canvas', 'map',
    'area', 'pre', 'code', 'header', 'menu',
    'dialog', 'datalist', 'output', 'progress',
    'meter', 'details', 'summary', 'template',
    'aside', 'advertisement', 'ad', 'banner', 'promo', 'sponsored', 
    'popup', 'modal', 'notification', 'alert', 'carousel', 'social-share', 
    'share', 'related-posts', 'disclaimer', 'subscription', 'cookie-consent',
    'toolbar', 'download', 'terms-of-service', 'privacy-policy', 'copyright',
    'sidebar', 'widget', 'widgets', 'sidebar-ad', 'ads', 'ad-container',
    'hidden', 'mobile-nav', 'mobile-menu', 'bottom-bar', 'popup-wrapper',
    'scrollable', 'sticky-header', 'sticky-footer', 'inline'
]

# Classes/IDs that typically indicate non-content
NON_CONTENT_CASES = [
    'ad', 'ads', 'advert', 'banner', 'sidebar',
    'navbar', 'menu', 'footer', 'header', 'modal',
    'popup', 'lightbox', 'cookie', 'consent',
    'notification', 'promo', 'sponsor', 'affiliate',
    'recommendation', 'related', 'comments', 'social',
    'share', 'login', 'signup', 'newsletter', 'pagination',
    'advertisement', 'popup-wrapper', 'sticky-header', 'sticky-footer',
    'back-to-top', 'scroll-to-top', 'toaster', 'alert', 'message', 
    'widget', 'widgets', 'sidebar-ad', 'ad-container', 'search',
    'search-bar', 'breadcrumb', 'footer-links', 'bottom-bar', 
    'call-to-action', 'cta', 'form-wrapper', 'user', 'profile',
    'subscription', 'subscription-form', 'cookie-policy', 'terms', 'disclaimer',
    'privacy-policy', 'footer-menu', 'top-nav', 'topbar', 'mobile-nav',
    'popup-modal', 'floating', 'slide-out', 'error-message', 'captcha'
]

# Paywall detection patterns
PAYWALL_PATTERNS = [
    "subscribe", "subscription", "sign in to continue", 
    "continue reading", "create an account", "premium content",
    "paid member", "unlock", "free trial", "register to read",
    "remaining free articles", "remaining articles", "for full access",
    "join now", "become a member", "sign up today", 
    "limited access", "exclusive content", "only for members", 
    "paywall", "sign up for full access", "get access now",
    "read more", "unlock content", "access denied", "subscribe now",
    "member-only", "access premium", "subscribe to read", 
    "full access", "full article", "article behind paywall", 
    "get the full story", "view full content", "unlock full access", 
    "limited access content", "premium membership", "read the full article",
    "only available to subscribers", "premium subscription", "content locked"
]

# Common consent button selectors
CONSENT_SELECTORS = [
    "button[id*='cookie']", "button[class*='cookie']",
    "button:has-text('Accept')", "button:has-text('Agree')",
    "button:has-text('Accept all')", "a:has-text('Accept cookies')",
    "[id*='cookie'] button", "[class*='cookie'] button",
    "button:has-text('OK')", "button:has-text('Got it')",
    "button:has-text('I agree')", "button:has-text('Confirm')",
    "button:has-text('Allow all cookies')", "button:has-text('Allow cookies')",
    "button:has-text('Yes, I agree')", "button:has-text('Continue')",
    "button:has-text('Close')", "a:has-text('Got it')",
    "button[id*='accept']", "button[class*='accept']",
    "button[id*='agree']", "button[class*='agree']",
    "button[id*='consent']", "button[class*='consent']",
    "button[id*='allow']", "button[class*='allow']",
    "[id*='accept'] button", "[class*='accept'] button",
    "[id*='consent'] button", "[class*='consent'] button",
    "a[href*='cookie']", "a[href*='accept']", "a[href*='agree']",
    "div[id*='cookie']", "div[class*='cookie']",
    "div[id*='consent']", "div[class*='consent']"
]

MODAL_SELECTORS = [
    ".paywall", "[id*='paywall']", 
    "[id*='subscribe-wall']", "[class*='paywall']",
    "[id*='modal']", "[class*='modal']", 
    "[id*='overlay']", "[class*='overlay']", 
    "[id*='popup']", "[class*='popup']", 
    "[id*='subscription']", "[class*='subscription']", 
    "[id*='cookie']", "[class*='cookie']", 
    "[id*='consent']", "[class*='consent']", 
    "[id*='dialog']", "[class*='dialog']",
    "[id*='login']", "[class*='login']",
    "[id*='signin']", "[class*='signin']",
    "[id*='register']", "[class*='register']",
    "[id*='signup']", "[class*='signup']",
    ".modal-overlay", ".modal-dialog", ".popup-wrapper", ".overlay-content"
]

COMMON_CONTENT_SELECTORS = [
    "article", ".article", ".post", ".content", "#content", 
    "main", "#main", ".main-content", ".post-content", 
    ".entry-content", ".article-content", ".tutorial-content",
    ".blog-post", ".news-article", ".page-content", 
    ".text-content", ".single-post", "#primary", ".primary-content",
    ".content-wrapper", ".content-area", ".details-content", 
    ".article-body", ".body-content", ".section-content", ".educational-content",
    ".lesson-content", ".course-content", ".study-material", ".exam-content"
]

#################################################################################
# Used in course_gen.py

# Course templates with placeholders for AI-enhanced content
COURSE_TEMPLATE = { 
    'course': {
        'introduction': (
            "# {title}\n\n"
            "## Course Overview\n\n"
            "{ai_enhanced_description}\n\n"
            "### Course Objectives\n\n"
            "{learning_objectives}\n\n"
            "### Prerequisites\n\n"
            "{prerequisites}\n\n"
            "### Target Audience\n\n"
            "This {level} course on {topic} is designed for {audience}.\n\n"
            "### Course Structure\n\n"
            "{structure_overview}\n\n"
            "### Learning Path\n\n"
            "{learning_path}"
        ),
        'conclusion': (
            "# Course Conclusion\n\n"
            "## Congratulations!\n\n"
            "You've completed the {level} course on {topic}! Let's recap what you've learned:\n\n"
            "{key_learnings}\n\n"
            "## Next Steps\n\n"
            "{next_steps}\n\n"
            "## Certificate\n\n"
            "Complete the final assessment to receive your certificate of completion.\n\n"
            "## Connect & Continue Learning\n\n"
            "{community_resources}"
        )
    },
    'module': {
        'introduction': (
            "# Module {module_num}: {title}\n\n"
            "## Overview\n\n"
            "{ai_enhanced_overview}\n\n"
            "## Learning Objectives\n\n"
            "{learning_objectives}\n\n"
            "## Module Outline\n\n"
            "{module_outline}\n\n"
            "## Estimated Time: {estimated_time}\n\n"
            "## Key Concepts\n\n"
            "{key_concepts}"
        ),
        'section': {
            'explanation': (
                "## {title}\n\n"
                "{ai_enhanced_explanation}\n\n"
                "### Key Points\n\n"
                "{key_points}\n\n"
                "### Real-world Application\n\n"
                "{real_world_application}\n\n"
                "### Conceptual Model\n\n"
                "{conceptual_model}\n\n"
                "### Common Misconceptions\n\n"
                "{misconceptions}"
            ),
            'example': (
                "### Example: {title}\n\n"
                "#### Problem Statement\n\n"
                "{problem_statement}\n\n"
                "#### Solution Approach\n\n"
                "{solution_approach}\n\n"
                "```{language}\n{code}\n```\n\n"
                "#### Explanation\n\n"
                "{ai_enhanced_explanation}\n\n"
                "#### Alternative Approaches\n\n"
                "{alternative_approaches}\n\n"
                "#### Practice Variation\n\n"
                "{practice_variation}"
            ),
            'exercise': (
                "## Exercise: {title}\n\n"
                "### Objective\n\n"
                "{objective}\n\n"
                "### Context\n\n"
                "{context}\n\n"
                "### Requirements\n\n"
                "{requirements}\n\n"
                "### Scaffold (Starting Point)\n\n"
                "```{language}\n{scaffold_code}\n```\n\n"
                "### Steps to Solve\n\n"
                "{steps}\n\n"
                "### Hints\n\n"
                "{hints}\n\n"
                "### Assessment Criteria\n\n"
                "{assessment_criteria}"
            ),
            'case_study': (
                "## Case Study: {title}\n\n"
                "### Background\n\n"
                "{background}\n\n"
                "### Challenge\n\n"
                "{challenge}\n\n"
                "### Analysis\n\n"
                "{analysis}\n\n"
                "### Solution\n\n"
                "{solution}\n\n"
                "### Lessons Learned\n\n"
                "{lessons_learned}\n\n"
                "### Discussion Questions\n\n"
                "{discussion_questions}"
            ),
            'quiz': (
                "## Knowledge Check: {title}\n\n"
                "{introduction}\n\n"
                "{questions}\n\n"
                "### Answer Key\n\n"
                "{answer_key}"
            )
        },
        'summary': (
            "## Module {module_num} Summary\n\n"
            "### Key Takeaways\n\n"
            "{key_takeaways}\n\n"
            "### Skills Acquired\n\n"
            "{skills_acquired}\n\n"
            "### Module Assessment\n\n"
            "{assessment_description}\n\n"
            "### Further Reading\n\n"
            "{further_reading}\n\n"
            "### Next Module Preview\n\n"
            "{next_module_preview}"
        )
    }
}

LEVEL_MAP = {
    "beginner": {"order": 1, "prerequisites": []},
    "intermediate": {"order": 2, "prerequisites": ["beginner"]},
    "advanced": {"order": 3, "prerequisites": ["intermediate"]},
    "expert": {"order": 4, "prerequisites": ["advanced"]}
}


################################################################################
# Used in content_enhancer.py
SPECIAL_TOKENS = {
                    'explanation': '<|explanation|>',
                    'example': '<|example|>',
                    'exercise': '<|exercise|>',
                    'summary': '<|summary|>',
                    'description': '<|description|>',
                    'objectives': '<|objectives|>',
                    'prerequisites': '<|prerequisites|>',
                    'structure': '<|structure|>',
                    'learning_path': '<|learning_path|>',
                    'key_learnings': '<|key_learnings|>',
                    'next_steps': '<|next_steps|>',
                    'beginner': '<|beginner|>',
                    'intermediate': '<|intermediate|>',
                    'advanced': '<|advanced|>',
                    'expert': '<|expert|>',
                    
                    'title': '<|title|>'
}