import { Component } from '@angular/core';

import { NgForm } from '@angular/forms';

export interface eginterface {
  numero: number,
  texto : string,
  boleano : boolean
}

@Component({
  selector: 'app-examples',
  templateUrl: './examples.component.html',
  styleUrl: './examples.component.css'
})
export class ExamplesComponent {

  texto: string = 'Mostra valor variável';

  intexto:string = '';

  soma1: number = 0;
  soma2: number = 0;
  somar: number = 0;

  elm1: number = 0;
  elm2: number= 0;
  operator: string = '';
  result: number = 0;

  conta: number = 0;

  mostra:boolean = true;
  mostra2:boolean = true;

  isblue:boolean = false;

  tstarray: string[] = [];

  egint: eginterface[] = [
    {numero: 926000999, texto: 'Nome 1', boleano: true},
    {numero: 926111777, texto: 'Nome 2', boleano: false},
    {numero: 926222888, texto: 'Nome 3', boleano: true},
    {numero: 926546125, texto: 'Nome 4', boleano: false},
  ];

  ngOnInit(): void {
    var lol = [1, 2, 3, 4, 5];

    for (let i=0; i < lol.length; i++) {
      console.log(lol[i]);
    };

    for (let e of lol) {
      console.log(e);
    };

    lol.forEach(l => {
      console.log(l);
    });
  }

  soma() {
    this.somar = Number(this.soma1) + Number(this.soma2);
  }

  calcexp() {
    let x = Number(this.elm1),
        y = Number(this.elm2);
      
    if (this.operator === '+') {
      this.result = x + y;
    } else if (this.operator === '-') {
      this.result = x - y;
    } else if (this.operator === '*' || this.operator === 'x') {
      this.result = x * y;
    } else if (this.operator === '/') {
      this.result = x / y;
    }
  }

  contador (oquefazer: string) {
    if (oquefazer === 'mais') {
      this.conta += 1;
    } else {
      this.conta -= 1;
    }
  }

  toogleh1 () {
    this.mostra = !this.mostra ? true : false;
  }

  addForm(f: NgForm) {
    var nelem = Number(f.value.nelm);
    var int   = Number(f.value.interval);

    var oarray: string[] = [];

    for (let i=0; i < nelem; i++) {
      if (i === 0) {
        oarray.push(String(i));
      } else {
        oarray.push(String(Number(oarray[i-1]) + int));
      }
    }

    this.tstarray = oarray;
  }

  removec(idx:number) {
    this.egint.splice(idx, 1);
  }

  addContact(e: NgForm) {
    var nc: eginterface = {
      numero: e.value.numero,
      texto  : e.value.nome,
      boleano : false
    }
    this.egint.push(nc);
  }

}
