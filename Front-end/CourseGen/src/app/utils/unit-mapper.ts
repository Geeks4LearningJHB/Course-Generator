import { parseArgs } from 'util';
import { ParsedUnit, UnitWithContent } from '../interface/unit.interfaces';

export class UnitMapper {
  /**
   * Converts a ParsedUnit object to a UnitWithContent object
   */
  static parsedUnitToUnit(parsedUnit: ParsedUnit): UnitWithContent {
    return {
      unitId: parsedUnit.unitId,
      unitName: parsedUnit.unitName || parsedUnit.title,
      unitDescription: parsedUnit.unitDescription || '',
      content: parsedUnit.content || '',
      type: parsedUnit.type || 'explanation',
      // Add these to maintain all original data
      originalContent: parsedUnit.originalContent,
      unitNum: parsedUnit.unitNum || 0
    }
  }

  /**
   * Converts a UnitWithContent object to a ParsedUnit object
   */
  static unitToParsedUnit(unit: UnitWithContent): ParsedUnit {
    let parsedUnit: ParsedUnit = {
      unitId: unit.unitId,
      unitName: unit.unitName,
      unitDescription: unit.unitDescription || '',
      content: unit.content || '',
      unitNum: unit.unitNum || 0,
      title: unit.unitName,
      introduction: '',
      keyConcepts: [],
      sections: [],
      type: unit.type || 'explanation',
      isLoaded: false
    }

    // Parse either from combined content or original structure
    if (unit.originalContent) {
      // Parse from original structured content
      if (unit.originalContent.explanation) {
        parsedUnit.introduction = this.extractFirstParagraph(unit.originalContent.explanation);
      }
      
      if (unit.originalContent.examples) {
        parsedUnit.keyConcepts = unit.originalContent.examples
          .map((ex: string, i: number) => `Example ${i+1}: ${this.extractExampleTitle(ex)}`);
      }
    } 
    else if (unit.content) {
      // Fallback to parsing from combined content
      parsedUnit.introduction = this.extractIntroduction(unit.content);
      parsedUnit.keyConcepts = this.extractKeyConcepts(unit.content);
    }
    
    return parsedUnit;
  }

  private static extractFirstParagraph(text: string): string {
      const match = text.match(/^(.*?)(?:\n\n|$)/s);
      return match ? match[1].trim() : '';
  }

  private static extractExampleTitle(example: string): string {
      const titleMatch = example.match(/### Example: (.+?)\n/);
      return titleMatch ? titleMatch[1].trim() : 'Untitled Example';
  }

  private static extractIntroduction(content: string): string {
    // Try to find an "Introduction" section
    const introMatch = content.match(/##\s*Introduction\s*\n+([\s\S]+?)(?:\n##|$)/i);
    if (introMatch) {
      return introMatch[1].trim().split('\n\n')[0]; // First paragraph in the intro section
    }

    // Fallback: return the very first paragraph
    const fallbackMatch = content.match(/^(.*?)(?:\n\n|$)/s);
    return fallbackMatch ? fallbackMatch[1].trim() : '';
  }

  private static extractKeyConcepts(content: string): string[] {
    const examples = [];
    const regex = /###\s*Example:\s*(.+?)\n/gi;
    let match;
    let index = 1;

    while ((match = regex.exec(content)) !== null) {
      examples.push(`Example ${index++}: ${match[1].trim()}`);
    }

    return examples;
  }
}