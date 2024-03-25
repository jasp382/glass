import { Component } from '@angular/core';

export interface Product {
  designation: string,
  price: number
}

@Component({
  selector: 'app-store',
  templateUrl: './store.component.html',
  styleUrls: ['./store.component.css']
})
export class StoreComponent {

  productsTypes: string[] = ["Smartphones", "PC's", "Games"];

  selPType: string|undefined;

  smartphones: Product[] = [{
    designation: 'Smartphone 1',
    price: 200
  },{
    designation: 'Smartphone 2',
    price: 100
  },{
    designation: 'Smartphone 3',
    price: 500
  },{
    designation: 'Smartphone 4',
    price: 450
  },{
    designation: 'Smartphone 5',
    price: 120
  }];

  pcs: Product[] = [{
    designation: 'PC 1',
    price: 699
  },{
    designation: 'PC 2',
    price: 500
  },{
    designation: 'PC 3',
    price: 1299
  },{
    designation: 'PC 4',
    price: 1550
  },{
    designation: 'PC 5',
    price: 2000
  }];

  games: Product[] = [{
    designation: 'Game 1',
    price: 20
  },{
    designation: 'Game 2',
    price: 60
  },{
    designation: 'Game 3',
    price: 40
  },{
    designation: 'Game 4',
    price: 75
  },{
    designation: 'Game 5',
    price: 50
  }];

  selProds: Product[] = this.smartphones;

  cart: Product[] = [];

  totalprice: number = 0;


  /**
   * Functions
   * 
  */

  selectProdType(ptype: string) {
    this.selPType = ptype;

    if (ptype === 'Smartphones') {
      this.selProds = this.smartphones;
    } else if (ptype === "PC's") {
      this.selProds = this.pcs;
    } else {
      this.selProds = this.games;
    }
    console.log(this.selProds);
  }

  addProductToCart(p: Product) {
    this.cart.push(p);

    this.totalprice = this.totalprice + p.price;
  }

  rmProductFmCart(i: number, price: number) {
    this.cart.splice(i, 1);

    this.totalprice = this.totalprice - price
  }

}
