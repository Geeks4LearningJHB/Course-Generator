import { Injectable } from '@angular/core';
import { ListItem, ParsedSection, ParsedUnit } from '../interface/unit.interfaces';

@Injectable({
  providedIn: 'root'
})
export class CourseAdapterService {

  constructor() { }

  /**
   * Transforms the backend course JSON structure into the frontend-expected format
   */
  adaptCourseForFrontend(backendCourse: any): any {
    if (!backendCourse) {
      return null;
    }

    // We expect backendCourse.course.modules here
    const courseData = backendCourse.course || {};
    const modules = courseData.modules || [];

    // Extract first module info (assuming one module focus or for summary)
    const moduleInfo = this.extractModuleInfo(modules);

    // Extract all units from all modules
    const units = this.extractUnits(modules);

    return {
      module: moduleInfo,
      units: units,
      difficulty: this.extractDifficulty(backendCourse)
    };
  }

  private extractModuleInfo(modules: any[]): any {
    if (!modules || modules.length === 0) {
      return { moduleName: '', moduleId: '' };
    }

    const firstModule = modules[0];
    const moduleName = firstModule.title || '';
    const moduleId = firstModule._id || 'module_' + Math.random().toString(36).substring(2, 9);

    return { moduleName, moduleId };
  }

  private extractUnits(modules: any[]): ParsedUnit[] {
    const units: ParsedUnit[] = [];

    modules.forEach((module: any, moduleIndex: number) => {
      if (module.units && module.units.length > 0) {
        module.units.forEach((unit: any, unitIndex: number) => {
          const fullContent = this.combineUnitContent(unit.content);

          units.push({
            unitId: unit._id || `unit_${moduleIndex}_${unitIndex}`,
            unitName: unit.title || `Unit ${unitIndex + 1}`,
            unitDescription: unit.description || '',
            content: fullContent,
            unitNum: unitIndex + 1,
            title: unit.title || `Unit ${unitIndex + 1}`,
            introduction: this.extractIntroduction(fullContent),
            keyConcepts: this.extractKeyConcepts(fullContent),
            sections: this.extractSections(fullContent),
            type: unit.type || 'explanation',
            isLoaded: false,
            originalContent: unit.content
          });
        });
      }
    });

    return units;
  }

  private combineUnitContent(content: any): string {
    if (!content) return '';

    const parts: string[] = [];

    if (content.explanation) {
      parts.push(`## Explanation\n\n${content.explanation}`);
    }

    if (content.examples && Array.isArray(content.examples) && content.examples.length > 0) {
      parts.push(`## Examples`);
      content.examples.forEach((example: any, idx: number) => {
        // Assuming example is a string or object with title and explanation
        if (typeof example === 'string') {
          parts.push(`### Example ${idx + 1}\n\n${example}`);
        } else if (example.title && example.problem_statement && example.solution_approach) {
          parts.push(
            `### Example: ${example.title}\n\n` +
            `#### Problem Statement\n\n${example.problem_statement}\n\n` +
            `#### Solution Approach\n\n${example.solution_approach}\n\n` +
            (example.language && example.code ? `\`\`\`${example.language}\n${example.code}\n\`\`\`\n\n` : '') +
            `#### Explanation\n\n${example.ai_enhanced_explanation || ''}\n\n` +
            `#### Alternative Approaches\n\n${example.alternative_approaches || ''}\n\n` +
            `#### Practice Variation\n\n${example.practice_variation || ''}`
          );
        }
      });
    }

    // Add case studies if exist
    if (content.case_study && Array.isArray(content.case_study)) {
      content.case_study.forEach((caseStudy: any, idx: number) => {
        parts.push(
          `## Case Study: ${caseStudy.title}\n\n` +
          `### Background\n\n${caseStudy.background}\n\n` +
          `### Challenge\n\n${caseStudy.challenge}\n\n` +
          `### Analysis\n\n${caseStudy.analysis}\n\n` +
          `### Solution\n\n${caseStudy.solution}\n\n` +
          `### Lessons Learned\n\n${caseStudy.lessons_learned}\n\n` +
          `### Discussion Questions\n\n${caseStudy.discussion_questions}`
        );
      });
    }

    if (content.misconceptions) {
      parts.push(`## Common Misconceptions\n\n${content.misconceptions}`);
    }

    if (content.conceptual_model) {
      parts.push(`## Conceptual Model\n\n${content.conceptual_model}`);
    }

    if (content.real_world_application) {
      parts.push(`## Real-world Application\n\n${content.real_world_application}`);
    }

    return parts.join('\n\n');
  }

  private extractIntroduction(content: string): string {
    if (!content) return '';

    const introPattern = /##?\s+(Overview|Introduction)\s*\n+(.*?)(?=##|$)/s;
    const match = content.match(introPattern);
    if (match) {
      return match[2].trim();
    }

    // Fallback: first paragraph
    const firstParaMatch = content.match(/^(.*?)(?:\n\n|$)/s);
    return firstParaMatch ? firstParaMatch[1].trim() : '';
  }

  private extractKeyConcepts(content: string): string[] {
    if (!content) return [];

    const pattern = /##?\s+(Key\s+Points|Key\s+Concepts|Learning\s+Objectives)\s*\n+(.*?)(?=##|$)/s;
    const match = content.match(pattern);
    if (!match) return [];

    const bulletLines = match[2].split('\n').filter(line => line.trim().startsWith('-') || line.trim().startsWith('*'));
    return bulletLines.map(line => line.replace(/^[*-]\s*/, '').trim());
  }

  private extractSections(content: string): ParsedSection[] {
    if (!content) return [];

    const sections: ParsedSection[] = [];

    const headers = content.match(/^(##+)\s+(.*)$/gm) || [];
    const blocks = content.split(/^(##+)\s+.*$/gm);

    let blockIndex = 1;
    headers.forEach((header, i) => {
      const heading = header.replace(/^##+\s+/, '').trim();
      const blockContent = blocks[blockIndex] ? blocks[blockIndex].trim() : '';
      blockIndex += 2;

      if (/introduction|overview|key points|key concepts|learning objectives/i.test(heading)) {
        return;
      }

      sections.push({
        heading,
        content: this.processContentBlock(blockContent)
      });
    });

    return sections;
  }

  private processContentBlock(content: string): string | ListItem[] {
    if (!content) return '';

    const bulletRegex = /^[*-]\s+.+$/gm;

    if (bulletRegex.test(content)) {
      const items: ListItem[] = content
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0 && (line.startsWith('-') || line.startsWith('*')))
        .map(line => ({
          text: line.replace(/^[*-]\s*/, '').trim()
        }));

      return items;
    }

    return content;
  }

  private extractDifficulty(backendCourse: any): string {
    return backendCourse.metadata?.level || 'Intermediate';
  }
}