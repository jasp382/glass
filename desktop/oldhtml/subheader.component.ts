import { Component, OnInit, Input } from '@angular/core';
import { GlobalConstants } from '../../../../../gaspcli-app/src/app/common/global-constants';


@Component({
  selector: 'subheader',
  templateUrl: './subheader.component.html',
  styleUrls: ['./subheader.component.css']
})

export class SubheaderComponent implements OnInit {
  @Input('current-url') currentUrl : string;

  urllst:string[];
  servname:string = '';
  headers:object = GlobalConstants.HEADERS;

  ngOnChanges(): void {
    this.urllst = this.currentUrl.split('/');
    if (this.urllst.length == 4) {
      this.servname = this.headers[this.urllst[2]];
    } else {
      this.servname = '';
    }
  }

  ngOnInit() {
  }

}
