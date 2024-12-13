import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CourseSaveComponentComponent } from './course-save-component.component';

describe('CourseSaveComponentComponent', () => {
  let component: CourseSaveComponentComponent;
  let fixture: ComponentFixture<CourseSaveComponentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CourseSaveComponentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CourseSaveComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
