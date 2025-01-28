import { ParsedUnit, UnitWithContent } from "../interface/unit.interfaces";


export class UnitMapper {
  static parsedUnitToUnit(parsedUnit: ParsedUnit): UnitWithContent {
    return {
      unitId: this.generateUnitId(parsedUnit.title),
      unitName: parsedUnit.title,
      unitDescription: parsedUnit.introduction,
      duration: 0,
      monthNumber: parsedUnit.monthNumber,
      title: parsedUnit.title,
      introduction: parsedUnit.introduction,
      keyConcepts: parsedUnit.keyConcepts,
      sections: parsedUnit.sections,
      isLoaded: parsedUnit.isLoaded
    };
  }

  static unitToParsedUnit(unit: UnitWithContent): ParsedUnit {
    return {
      monthNumber: unit.monthNumber,
      title: unit.unitName,
      introduction: unit.unitDescription,
      keyConcepts: unit.keyConcepts || [],
      sections: unit.sections || [],
      isLoaded: unit.isLoaded
    };
  }

  private static generateUnitId(title: string): string {
    return `${title.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`;
  }
}