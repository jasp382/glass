import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// Guards
import { AuthGuard } from './auth/guards/auth.guard';
import { RoleGuard } from './auth/guards/role.guard';

// Home Component
import { HomeComponent } from './general/home/home.component';

// Main Interface components
import { MaincComponent } from './geoportal/mainc/mainc.component';

// Profile Interface components
import { MainpComponent } from './profile/mainp/mainp.component';

// Backoffice Components
import { MainComponent } from './boff/main/main.component';

// Other Components
import { UnauthorizedComponent } from './auth/unauthorized/unauthorized.component';
import { NotfoundComponent } from './general/notfound/notfound.component';

const routes: Routes = [
  { path: '', component: HomeComponent },

  // Main Interface
  { path: 'geoportal', redirectTo: 'geoportal/main/app', pathMatch: 'full' },
  { path: 'geoportal/:page', redirectTo: 'geoportal/main/app', pathMatch: 'full' },
  { path: 'geoportal/:page/:tab', component: MaincComponent },

  // Geoportal Profile
  { path: 'profile', component: MainpComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'profile/password', component: MainpComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'profile/contributions', component: MainpComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },

  // Backoffice Interface
  { path: 'admin', redirectTo: '/admin/home', pathMatch: 'full' },
  { path: 'admin/:page', component: MainComponent, canActivate: [AuthGuard, RoleGuard], runGuardsAndResolvers: 'always' },
  { path: 'admin/:page/:page', component: MainComponent, canActivate: [AuthGuard, RoleGuard], runGuardsAndResolvers: 'always' },

  // Other components
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: '**', component: NotfoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { onSameUrlNavigation: 'ignore'})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
