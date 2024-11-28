import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminViewContentComponent } from './admin-view-content.component';

describe('AdminViewContentComponent', () => {
  let component: AdminViewContentComponent;
  let fixture: ComponentFixture<AdminViewContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AdminViewContentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminViewContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
