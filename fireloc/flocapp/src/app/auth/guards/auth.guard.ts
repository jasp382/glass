import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, of } from 'rxjs';

// Service
import { AuthService } from 'src/app/serv/rest/users/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  /**
   * Constructor.
   * @param authServ Authentication service. See {@link AuthService}.
   * @param router Angular router.
   */
  constructor(
    private authServ: AuthService,
    private router: Router
  ) { }

  /**
   * Determines wheter the user can navigate to the route or not depending on logged status.
   * Uses the authentication service. If user is logged in, navigation proceeds as normal.
   * Otherwise, user is redirected to the unauthorized page.
   * @param route activate route snapshot 
   * @param state router state snapshot
   * @returns true if user is logged in, false if otherwise.
   */
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean> {
    
    // authorized users are allowed
    if (this.authServ.isLoggedIn()) return of(true);
    // unauthorized users are redirected
    else {
      this.router.navigate(['unauthorized']);
      return of(false);
    }
  }
  
}
