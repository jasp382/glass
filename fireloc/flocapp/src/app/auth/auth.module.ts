// Modules
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FeatModule } from '../feat/feat.module';
import { ReactiveFormsModule } from '@angular/forms';

// Components
import { ForgotpassComponent } from './forgotpass/forgotpass.component';
import { LoginComponent } from './login/login.component';
import { ResetpassComponent } from './resetpass/resetpass.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import { SignupComponent } from './signup/signup.component';

// Style
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Language
import { TranslateModule } from '@ngx-translate/core';


@NgModule({
  declarations: [
    ForgotpassComponent,
    LoginComponent,
    ResetpassComponent,
    UnauthorizedComponent,
    SignupComponent,
  ],
  imports: [
    CommonModule,
    FontAwesomeModule,
    RouterModule,
    FeatModule,
    ReactiveFormsModule,
    NgbModule,
    TranslateModule,
  ]
})
export class AuthModule { }
