import { Injectable } from '@angular/core';

interface MonthContent {
  monthNumber: number;
  title: string;
  introduction: string;
  keyConcepts: string[];
  sections: {
    heading: string;
    content: string | any[];
  }[];
}

@Injectable({
  providedIn: 'root',
})
export class ContentParserService {
  private readonly CHUNK_DELAY = 10;

  // Parse content in smaller chunks
  async parseContent(
    content: string,
    chunkSize: number = 1000
  ): Promise<MonthContent[]> {
    try {
      // First, split the content into major sections to preserve structure
      const contentSections = this.splitIntoMajorSections(content);
      const results: MonthContent[] = [];

      // Process each major section with delays to prevent blocking
      for (const section of contentSections) {
        await new Promise((resolve) => setTimeout(resolve, this.CHUNK_DELAY));

        try {
          const parsedSection = await this.processSectionSafely(section);
          if (parsedSection) {
            results.push(parsedSection);
          }
        } catch (error) {
          console.error('Error processing section:', error);
        }
      }

      return results;
    } catch (error) {
      console.error('Error in parseContent:', error);
      return [];
    }
  }

  private chunkString(str: string, size: number): string[] {
    const chunks = [];
    for (let i = 0; i < str.length; i += size) {
      chunks.push(str.slice(i, i + size));
    }
    return chunks;
  }

  private async parseSections(content: string): Promise<any[]> {
    const sections: any[] = [];
    const sectionRegex = /(?<=^|\n)(\d+\.)\s+(.*?)(?=\n\d+\.|\n?$)/gs;
  
    let match;
    while ((match = sectionRegex.exec(content)) !== null) {
      const [_, sectionNumber, sectionTitle] = match;
      const sectionContent = match.input.slice(
        match.index + match[0].length,
        sectionRegex.lastIndex
      );
  
      await new Promise((resolve) => setTimeout(resolve, this.CHUNK_DELAY)); // Delay for async parsing
      sections.push({
        heading: `${sectionNumber} ${sectionTitle}`.trim(),
        content: await this.parseContentSafely(sectionContent.trim()),
      });
    }
  
    return sections;
  }
  

  private splitIntoMajorSections(content: string): string[] {
    // Split content at major section boundaries (e.g., months or units)
    const sectionDelimiter = /(?=Month \d+:|Unit \d+:)/g;
    return content.split(sectionDelimiter).filter((section) => section.trim());
  }

  private async processSectionSafely(
    section: string
  ): Promise<MonthContent | null> {
    try {
      // Extract basic information
      const titleMatch = section.match(/^(Month|Unit) \d+:/);
      if (!titleMatch) return null;

      const monthNumber = parseInt(section.match(/\d+/)?.[0] || '0');
      const title = section.match(/^.*$/m)?.[0] || '';

      // Process introduction (everything before first numbered section)
      const introEnd = section.search(/\d+\.\s+[^\n]+/);
      const introduction =
        introEnd > -1
          ? section.slice(0, introEnd).replace(title, '').trim()
          : '';

      // Extract key concepts
      const keyConcepts = this.extractKeyConcepts(section);

      // Process sections in chunks
      const sections = await this.parseSectionsInChunks(section);

      return {
        monthNumber,
        title,
        introduction,
        keyConcepts,
        sections,
      };
    } catch (error) {
      console.error('Error processing section:', error);
      return null;
    }
  }

  private extractKeyConcepts(content: string): string[] {
    try {
      const conceptsMatch = content.match(/Key Concepts:([^]*?)(?=\d+\.|$)/);
      if (!conceptsMatch) return [];

      return this.extractListItems(conceptsMatch[1]);
    } catch (error) {
      console.error('Error extracting key concepts:', error);
      return [];
    }
  }

  private async parseSectionsInChunks(content: string): Promise<any[]> {
    const sections: any[] = [];
    const sectionMatches = content.matchAll(/\d+\.\s+([^\n]+)/g);

    for (const match of sectionMatches) {
      await new Promise((resolve) => setTimeout(resolve, this.CHUNK_DELAY));

      try {
        const sectionTitle = match[1];
        const sectionStart = match.index!;
        const nextSection = content
          .slice(sectionStart + 1)
          .match(/\d+\.\s+[^\n]+/);
        const sectionEnd = nextSection
          ? sectionStart + 1 + nextSection.index!
          : content.length;

        const sectionContent = content
          .substring(sectionStart + match[0].length, sectionEnd)
          .trim();

        const parsedContent = await this.parseContentSafely(
          sectionContent
        );

        sections.push({
          heading: sectionTitle,
          content: parsedContent,
        });
      } catch (error) {
        console.error('Error parsing section:', error);
      }
    }

    return sections;
  }

  private async parseContentSafely(content: string): Promise<string | any[]> {
    try {
      // Check content type and parse accordingly
      if (content.includes('```')) {
        return this.parseCodeBlocks(content);
      } else if (content.match(/^\d+\./) || content.includes('- ')) {
        return this.parseStructuredContent(content);
      } else if (content.includes('**')) {
        return this.parseBoldText(content);
      } else if (content.match(/https?:\/\//)) {
        return this.parseLinks(content);
      }
  
      return content.trim(); // Default case
    } catch (error) {
      console.error('Error parsing content:', error);
      return content.trim();
    }
  }
  

  // private parseSectionContent(content: string): string | any[] {
  //   // Check if content contains lists
  //   if (content.includes('- ') || content.match(/\d+\./)) {
  //     return this.parseStructuredContent(content);
  //   }

  //   // Handle code blocks
  //   if (content.includes('```')) {
  //     return this.parseCodeBlocks(content);
  //   }

  //   // Handle bold text
  //   if (content.includes('**')) {
  //     content = this.parseBoldText(content);
  //   }

  //   // Handle links
  //   if (content.match(/https?:\/\//)) {
  //     content = this.parseLinks(content);
  //   }

  //   // If no special parsing is needed, return trimmed content
  //   return content.trim();
  // }

  private parseLinks(content: string): string {
    // Regex to match URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;

    // Replace URLs with anchor tags
    return content.replace(
      urlRegex,
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
  }

  private parseStructuredContent(content: string): any[] {
    const items: any[] = [];
    const lines = content.split('\n').map((line) => line.trim());

    let currentMainItem: any = null;

    lines.forEach((line) => {
      if (line.match(/^\d+\./)) {
        // Main list item
        if (currentMainItem) {
          items.push(currentMainItem);
        }
        currentMainItem = {
          text: line.replace(/^\d+\./, '').trim(),
          subItems: [],
        };
      } else if (line.startsWith('- ') && currentMainItem) {
        // Sub list item
        currentMainItem.subItems.push(line.replace('- ', '').trim());
      } else if (line.startsWith('- ')) {
        // Regular bullet point
        items.push(line.replace('- ', '').trim());
      }
    });

    if (currentMainItem) {
      items.push(currentMainItem);
    }

    return items;
  }

  private parseCodeBlocks(content: string): any[] {
    const blocks = [];
    const regex = /```(\w+)?\n([\s\S]*?)```/g;
    let match;

    while ((match = regex.exec(content)) !== null) {
      blocks.push({
        language: match[1] || 'text',
        code: match[2].trim(),
      });
    }

    return blocks;
  }

  private parseBoldText(content: string): string {
    // Replace "**text**" with "<strong>text</strong>"
    return content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  }

  private extractListItems(content: string): string[] {
    return content
      .split('\n')
      .filter((line) => line.trim().startsWith('- '))
      .map((line) => line.replace('- ', '').trim());
  }
}
