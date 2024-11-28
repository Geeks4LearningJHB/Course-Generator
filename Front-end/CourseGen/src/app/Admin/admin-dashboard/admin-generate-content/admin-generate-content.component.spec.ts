import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminGenerateContentComponent } from './admin-generate-content.component';

describe('AdminGenerateContentComponent', () => {
  let component: AdminGenerateContentComponent;
  let fixture: ComponentFixture<AdminGenerateContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AdminGenerateContentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminGenerateContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
