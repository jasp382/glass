import { Component } from '@angular/core';

@Component({
  selector: 'app-store',
  templateUrl: './store.component.html',
  styleUrl: './store.component.css'
})
export class StoreComponent {

  productsTypes: string[] = ["Smartphones", "PC's", "Games"];

}
