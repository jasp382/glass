import { Component, DebugElement, ElementRef } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { HorizontalScrollDirective } from './horizontal-scroll.directive';

class MockElementRef extends ElementRef { }

describe('TS31 HorizontalScrollDirective', () => {
  // test component
  @Component({
    template: `<div appHorizontalScroll></div>`
  })
  class TestComponent {}

  let fixture: ComponentFixture<TestComponent>;
  let input: DebugElement;
  var directive: HorizontalScrollDirective;

  beforeEach(() => {
    fixture = TestBed.configureTestingModule({
      declarations: [HorizontalScrollDirective, TestComponent]
    }).createComponent(TestComponent);

    input = fixture.debugElement.query(By.directive(HorizontalScrollDirective));
    fixture.detectChanges();

    const element: MockElementRef = new MockElementRef("");
    directive = new HorizontalScrollDirective(element);
  })

  it('T31.1 should create an instance', () => {
    expect(directive).toBeTruthy();
  });

  it('T31.2 should emit y value of scroll on wheel event #onScroll', () => {
    // setup spy
    let emitterSpy = spyOn(directive.scrollEvent, 'emit');

    // create scroll event
    let wheelEvent = new WheelEvent('wheel', {
      deltaX: 0,
      deltaY: 1,
      deltaZ: 0,
      deltaMode: WheelEvent.DOM_DELTA_PIXEL
    });

    // dispatch event
    directive.onScroll(wheelEvent);

    // expectations
    expect(emitterSpy).toHaveBeenCalledOnceWith(1);
  });
});
