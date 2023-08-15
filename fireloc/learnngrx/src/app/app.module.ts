import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ListUsersComponent } from './list-users/list-users.component';
import { MainComponent } from './main/main.component';
import { AddUsersComponent } from './add-users/add-users.component';
import { StoreModule } from '@ngrx/store';
import { appEffects, appReducer } from './stores/app-state';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { ListUsersAdminComponent } from './list-users-admin/list-users-admin.component';

@NgModule({
  declarations: [
    AppComponent,
    ListUsersComponent,
    MainComponent,
    AddUsersComponent,
    ListUsersAdminComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    StoreModule.forRoot(appReducer),
    EffectsModule.forRoot(appEffects),
    StoreDevtoolsModule.instrument()
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
