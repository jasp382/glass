import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, of } from 'rxjs';

// Service
import { AuthService } from 'src/app/serv/rest/users/auth.service';

/**
 * Role guard. Implemented in some routes to check user user role for special permission privileges.
 */
@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  /**
   * Empty constructor.
   * @param authServ Authentication service. See {@link AuthService}.
   * @param router Angular router.
   */
  constructor(private authServ: AuthService, private router: Router) { }

  /**
   * Determines wheter the user can navigate to the route or not depending on their user role.
   * Uses the authentication service. If user has role of 'superuser' or 'fireloc', navigation proceeds as normal.
   * Otherwise, user is redirected to the unauthorized page.
   * @param route activate route snapshot 
   * @param state router state snapshot
   * @returns true if user has permission to view the content, false if otherwise.
   */
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean> {
    // check if user is authenticated
    if (this.authServ.isLoggedIn()) {
      // check if user has admin roles
      let role = localStorage.getItem('user_role');
      if (role === 'superuser' || role === 'fireloc') return of(true);
    }
    // unauthorized users are redirected
    this.router.navigate(['unauthorized']);
    return of(false);
  }

}
