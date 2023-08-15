import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from 'src/app/serv/rest/users/auth.service';

import { AuthGuard } from './auth.guard';

class AuthMock implements Partial<AuthService> {
  isLoggedIn(): boolean {
    return false;
  }
}

describe('TS4 AuthGuard', () => {
  let authGuard: AuthGuard;
  let authService: AuthMock;
  const routerMock = jasmine.createSpyObj('Router', ['navigate']);
  const authMock = jasmine.createSpyObj('AuthService', ['isLoggedIn']);

  beforeEach(() => {
    authService = new AuthMock();
    authGuard = new AuthGuard(authMock, routerMock);
  });

  it('T4.1 should be created', () => { expect(authGuard).toBeTruthy(); });

  it('T4.2 should allow user to proceed if they are logged in', (done) => {
    authMock.isLoggedIn.and.returnValue(true);
    const result = authGuard.canActivate(new ActivatedRouteSnapshot(), <RouterStateSnapshot>{ url: 'testUrl' });
    result.subscribe((result) => { expect(result).toEqual(true); done(); });
  });

  it('T4.3 should not allow user to proceed if they are not logged in', (done) => {
    authMock.isLoggedIn.and.returnValue(false);
    const result = authGuard.canActivate(new ActivatedRouteSnapshot(), <RouterStateSnapshot>{ url: 'testUrl' });
    result.subscribe(
      (result) => {
        expect(routerMock.navigate).toHaveBeenCalledOnceWith(['unauthorized']);
        expect(result).toEqual(false);
        done();
      }
    );
  });

});
