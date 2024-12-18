import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewGeneratedCourseComponent } from './view-generated-course.component';

describe('ViewGeneratedCourseComponent', () => {
  let component: ViewGeneratedCourseComponent;
  let fixture: ComponentFixture<ViewGeneratedCourseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ViewGeneratedCourseComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewGeneratedCourseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
