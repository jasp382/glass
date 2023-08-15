import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from 'src/app/serv/rest/users/auth.service';

import { RoleGuard } from './role.guard';

class AuthMock implements Partial<AuthService> {
  isLoggedIn(): boolean {
    return false;
  }
}

describe('TS5 RoleGuard', () => {
  let roleGuard: RoleGuard;
  let authService: AuthMock;
  const routerMock = jasmine.createSpyObj('Router', ['navigate']);
  const authMock = jasmine.createSpyObj('AuthService', ['isLoggedIn']);

  beforeEach(() => {
    authService = new AuthMock();
    roleGuard = new RoleGuard(authMock, routerMock);
  });

  it('T5.1 should be created', () => {
    expect(roleGuard).toBeTruthy();
  });

  it('T5.2 should not allow user to proceed if they are not logged in', (done) => {
    authMock.isLoggedIn.and.returnValue(false);
    const result = roleGuard.canActivate(new ActivatedRouteSnapshot(), <RouterStateSnapshot>{ url: 'testUrl' });
    result.subscribe(
      (result) => {
        expect(routerMock.navigate).toHaveBeenCalledWith(['unauthorized']);
        expect(result).toEqual(false);
        done();
      }
    );
  });

  it('T5.3 should allow user to proceed if they are logged in and have superuser role', (done) => {
    authMock.isLoggedIn.and.returnValue(true);
    spyOn(Storage.prototype, 'getItem').and.returnValue('superuser');

    const result = roleGuard.canActivate(new ActivatedRouteSnapshot(), <RouterStateSnapshot>{ url: 'testUrl' });
    result.subscribe((result) => { expect(result).toEqual(true); done(); });
  });

  it('T5.4 should allow user to proceed if they are logged in and have fireloc role', (done) => {
    authMock.isLoggedIn.and.returnValue(true);
    spyOn(Storage.prototype, 'getItem').and.returnValue('fireloc');

    const result = roleGuard.canActivate(new ActivatedRouteSnapshot(), <RouterStateSnapshot>{ url: 'testUrl' });
    result.subscribe((result) => { expect(result).toEqual(true); done(); });
  });

  it('T5.5 should not allow user to proceed if they are logged in and have any other role', (done) => {
    authMock.isLoggedIn.and.returnValue(true);
    spyOn(Storage.prototype, 'getItem').and.returnValue('justauser');

    const result = roleGuard.canActivate(new ActivatedRouteSnapshot(), <RouterStateSnapshot>{ url: 'testUrl' });
    result.subscribe((result) => {
      expect(routerMock.navigate).toHaveBeenCalledWith(['unauthorized']);
      expect(result).toEqual(false);
      done();
    });
  });
});
