// Modules
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

// Guards
import { AuthGuard } from './auth/guards/auth.guard';
import { RoleGuard } from './auth/guards/role.guard';

// Home Component
import { HomeComponent } from './home/home.component';

// Main Interface Components
import { MainfrontComponent } from './maini/mainfront/mainfront.component';
import { ProfileComponent } from './maini/profile/profile.component';

// Backoffice Components
import { MainComponent } from './boff/main/main.component';

// Other Components
import { UnauthorizedComponent } from './auth/unauthorized/unauthorized.component';
import { NotfoundComponent } from './notfound/notfound.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },

  // Main Interface
  { path: 'geoportal', redirectTo: 'geoportal/main/app', pathMatch: 'full' },
  { path: 'geoportal/:page', redirectTo: 'geoportal/main/app', pathMatch: 'full' },
  { path: 'geoportal/:page/:tab', component: MainfrontComponent },

  // Geoportal Profile
  { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'profile/password', component: ProfileComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'profile/contributions', component: ProfileComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },

  // Backoffice Interface
  { path: 'admin', redirectTo: '/admin/home', pathMatch: 'full', canActivate: [AuthGuard, RoleGuard], runGuardsAndResolvers: 'always' },
  { path: 'admin/:page', component: MainComponent, canActivate: [AuthGuard, RoleGuard], runGuardsAndResolvers: 'always' },
  { path: 'admin/:page/:page', component: MainComponent, canActivate: [AuthGuard, RoleGuard], runGuardsAndResolvers: 'always' },

  // Other components
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: '**', component: NotfoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { onSameUrlNavigation: 'reload' })],
  exports: [RouterModule],
  providers: [AuthGuard, RoleGuard]
})
export class AppRoutingModule { }
