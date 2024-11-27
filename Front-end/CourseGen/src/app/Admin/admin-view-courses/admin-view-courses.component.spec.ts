import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminViewCoursesComponent } from './admin-view-courses.component';

describe('AdminViewCoursesComponent', () => {
  let component: AdminViewCoursesComponent;
  let fixture: ComponentFixture<AdminViewCoursesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AdminViewCoursesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminViewCoursesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
