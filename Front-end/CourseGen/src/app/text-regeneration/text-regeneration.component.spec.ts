import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextRegenerationComponent } from './text-regeneration.component';

describe('TextRegenerationComponent', () => {
  let component: TextRegenerationComponent;
  let fixture: ComponentFixture<TextRegenerationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TextRegenerationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextRegenerationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
