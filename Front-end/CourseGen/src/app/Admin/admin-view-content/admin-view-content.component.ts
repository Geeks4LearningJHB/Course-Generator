import { Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-admin-view-content',
  templateUrl: './admin-view-content.component.html',
  styleUrl: './admin-view-content.component.css'
})
export class AdminViewContentComponent {

  showModifyFields: boolean = false;
  module: string = '';
  topic: string = '';
  details: string = '';
  isCollapsed = true;

  // Course data
  courseModules = [
    {
      title: 'Module 1: Introduction to Java',
      isExpanded: false,
      topics: [
        {
          title: '1.1 Setting Up Java Environment',
          isExpanded: false,
          details: ['Installing JDK', 'Configuring IDE']
        },
        {
          title: '1.2 Java Basics: Syntax, Data Types',
          isExpanded: false,
          details: ['Primitive Data Types', 'Operators']
        }
      ]
    },
    {
      title: 'Module 2: Object-Oriented Programming',
      isExpanded: false,
      topics: [
        {
          title: '2.1 Encapsulation, Inheritance, Polymorphism',
          isExpanded: false,
          details: ['Examples', 'Scenarios']
        },
        {
          title: '2.2 Abstraction and Interfaces',
          isExpanded: false,
          details: ['Interface Design', 'Use Cases']
        }
      ]
    }
  ];

  // Toggle module visibility
  toggleModule(index: number) {
    this.courseModules[index].isExpanded = !this.courseModules[index].isExpanded;
  }

  // Toggle topic visibility
  toggleSubTopic(moduleIndex: number, topicIndex: number) {
    this.courseModules[moduleIndex].topics[topicIndex].isExpanded =
      !this.courseModules[moduleIndex].topics[topicIndex].isExpanded;
  }

  onModifyContent() {
    console.log('Module:', this.module);
    console.log('Topic:', this.topic);
    console.log('Details:', this.details);
    alert('Content modified successfully!');
    this.module = '';
    this.topic = '';
    this.details = '';
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
}