import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClient, HttpErrorResponse, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AlertActions } from '../redux/actions/alertActions';
import { selectLanguage } from '../redux/selectors';

import { ErrorInterceptor } from './error-interceptor.interceptor';

describe('TS63 ErrorInterceptorInterceptor', () => {
  let interceptor: ErrorInterceptor;
  let httpMock: HttpTestingController;
  let httpClient: HttpClient;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        NgReduxTestingModule,
      ],
      providers: [
        ErrorInterceptor,
        { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
        AlertActions,
      ]
    });

    // reset redux
    MockNgRedux.reset();

    interceptor = TestBed.inject(ErrorInterceptor);
    httpMock = TestBed.inject(HttpTestingController);
    httpClient = TestBed.inject(HttpClient);
  });

  it('T63.1 should be created', () => { expect(interceptor).toBeTruthy(); });

  it('T63.2 should update app language from redux', () => {
    // spies
    let reduxSubSpy = spyOn(interceptor, 'subscribeToRedux').and.callThrough();

    // select language state and initialize
    const langStub = MockNgRedux.getSelectorStub(selectLanguage);
    langStub.next('pt');
    langStub.complete();

    interceptor.subscribeToRedux();

    // expectations
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    interceptor.language$.subscribe(
      (actualInfo: any) => {
        // language received should be as expected        
        expect(actualInfo).toEqual('pt');
        expect(interceptor.language).toEqual('pt');
      }
    );
  });

  it('T63.3 provide default message to errors without status', (done) => {
    let body = {};
    let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

    httpClient.get('').subscribe((response: any) => { fail('should have thrown error'); },
      (error: HttpErrorResponse) => {
        expect(alertSpy).toHaveBeenCalled();
        done();
      }
    );
    const req = httpMock.expectOne('');
    expect(req.request.method).toEqual('GET');
    req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
  });

  describe('TS63.1 Errors in portuguese', () => {
    beforeEach((done) => {
      const langStub = MockNgRedux.getSelectorStub(selectLanguage);
      langStub.next('pt');
      langStub.complete();

      interceptor.language$.subscribe(
        (actualInfo: any) => {
          // language received should be as expected        
          expect(actualInfo).toEqual('pt');
          expect(interceptor.language).toEqual('pt');
          done();
        }
      );
    });

    afterAll(() => { MockNgRedux.reset(); });

    it('T63.1.1 intercept A01 error', (done) => {
      let body = { status: { code: 'A01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Email ou Password incorretas.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the A01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.2 intercept A02 error', (done) => {
      let body = { status: { code: 'A02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Credenciais de autenticação são necessárias.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the A02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.3 intercept E01 error', (done) => {
      let body = { status: { code: 'E01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Campo obrigatório não preenchido.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.4 intercept E02 error', (done) => {
      let body = { status: { code: 'E02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Não está a usar uma aplicação FireLoc verificada.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.5 intercept E03 error', (done) => {
      let body = { status: { code: 'E03', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Não tem permissão para realizar esta operação.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E03 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.6 intercept E04 error', (done) => {
      let body = { status: { code: 'E04', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Operação não permitida.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E04 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.7 intercept E05 error', (done) => {
      let body = { status: { code: 'E05', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Dados não se encontram no formato JSON.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E05 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.8 intercept E06 error', (done) => {
      let body = { status: { code: 'E06', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Dados inválidos.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E06 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.9 intercept E07 error', (done) => {
      let body = { status: { code: 'E07', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data é inválida.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E07 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.11 intercept E08 error', (done) => {
      let body = { status: { code: 'E08', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Fuso horário é inválido.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E08 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.12 intercept E09 error', (done) => {
      let body = { status: { code: 'E09', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Dados necessitam de ter a mesma dimensão.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E09 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.13 intercept E10 error', (done) => {
      let body = { status: { code: 'E10', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Sistema de referência espacial inválido.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E10 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.14 intercept E11 error', (done) => {
      let body = { status: { code: 'E11', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Relação topológica é inválida.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E11 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.15 intercept I01 error', (done) => {
      let body = { status: { code: 'I01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Dados não encontrados.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.16 intercept I02 error', (done) => {
      let body = { status: { code: 'I02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Dados já se encontram registados.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.17 intercept I03 error', (done) => {
      let body = { status: { code: 'I03', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Dados não encontrados.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I03 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.18 intercept I04 error', (done) => {
      let body = { status: { code: 'I04', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>É permitido apenas um valor por atributo.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I04 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.19 intercept G01 error', (done) => {
      let body = { status: { code: 'G01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Geometria é inválida.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the G01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.20 intercept G02 error', (done) => {
      let body = { status: { code: 'G02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>EPSG é inválido.</strong> Tente novamente.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the G02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.21 intercept GS1 error', (done) => {
      let body = { status: { code: 'GS1', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Não foi possível a connecção com o servidor geográfico.</strong> Tente novamente mais tarde.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the GS1 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.21 intercept GS2 error', (done) => {
      let body = { status: { code: 'GS2', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Erro do servidor geográfico.</strong> Tente novamente mais tarde.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the GS2 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.22 intercept X01 error', (done) => {
      let body = { status: { code: 'X01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Ocorreu um erro e não foi possível enviar email.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the X01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.23 intercept X02 error', (done) => {
      let body = { status: { code: 'X02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Código de recuperação de password inválido.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the X02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.1.24 should give standard error when other codes are received', (done) => {
      let body = { status: { code: '', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = 'Ocorreu um erro. Tente novamente mais tarde';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the standard error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });
  });

  describe('TS63.2 Errors in english', () => {
    beforeEach((done) => {
      const langStub = MockNgRedux.getSelectorStub(selectLanguage);
      langStub.next('en');
      langStub.complete();

      interceptor.language$.subscribe(
        (actualInfo: any) => {
          // language received should be as expected        
          expect(actualInfo).toEqual('en');
          expect(interceptor.language).toEqual('en');
          done();
        }
      );
    });

    afterAll(() => { MockNgRedux.reset(); });

    it('T63.2.1 intercept A01 error', (done) => {
      let body = { status: { code: 'A01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Incorrect Email or Password.</strong> Try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the A01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.2 intercept A02 error', (done) => {
      let body = { status: { code: 'A02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Authentication credentials were not provided</strong> Try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the A02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.3 intercept E01 error', (done) => {
      let body = { status: { code: 'E01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Mandatory field not provided.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.4 intercept E02 error', (done) => {
      let body = { status: { code: 'E02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>You are not using a verified FireLoc application.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.5 intercept E03 error', (done) => {
      let body = { status: { code: 'E03', message: 'Group doesn\'t exist.' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>You don\'t have permission to perform this action.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E03 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.6 intercept E04 error', (done) => {
      let body = { status: { code: 'E04', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Action not allowed.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E04 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.7 intercept E05 error', (done) => {
      let body = { status: { code: 'E05', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data is not in JSON format.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E05 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.8 intercept E06 error', (done) => {
      let body = { status: { code: 'E06', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data is invalid.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E06 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.9 intercept E07 error', (done) => {
      let body = { status: { code: 'E07', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Invalid date.</strong> Try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E07 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.10 intercept E08 error', (done) => {
      let body = { status: { code: 'E08', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Timezone is invalid.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E08 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.11 intercept E09 error', (done) => {
      let body = { status: { code: 'E09', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data must have the same dimension.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E09 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.12 intercept E10 error', (done) => {
      let body = { status: { code: 'E10', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Spatial reference system is invalid.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E10 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.13 intercept E11 error', (done) => {
      let body = { status: { code: 'E11', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Topological relation is invalid.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the E11 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.14 intercept I01 error', (done) => {
      let body = { status: { code: 'I01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data not found.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.15 intercept I02 error', (done) => {
      let body = { status: { code: 'I02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data already registered.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.16 intercept I03 error', (done) => {
      let body = { status: { code: 'I03', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Data not found.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I03 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.17 intercept I04 error', (done) => {
      let body = { status: { code: 'I04', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Only one value per attribute is allowed.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the I04 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.18 intercept G01 error', (done) => {
      let body = { status: { code: 'G01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Geometry is invalid.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the G01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.19 intercept G02 error', (done) => {
      let body = { status: { code: 'G02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>EPSG is invalid.</strong> Please try again.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the G02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.20 intercept GS1 error', (done) => {
      let body = { status: { code: 'GS1', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Could not connect to geographical server.</strong> Please try again later.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the GS1 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.21 intercept GS2 error', (done) => {
      let body = { status: { code: 'GS2', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Error from geographical server.</strong> Please try again later.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the GS2 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.22 intercept X01 error', (done) => {
      let body = { status: { code: 'X01', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>An error occured and email was not sent.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the X01 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.23 intercept X02 error', (done) => {
      let body = { status: { code: 'X02', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = '<strong>Invalid password recovery code.</strong>';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the X02 error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });

    it('T63.2.24 should give standard error when other codes are received', (done) => {
      let body = { status: { code: '', message: '' } };
      let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
      const expectedMessage = 'An error occurred. Try again later.';

      httpClient.get('').subscribe((response: any) => { fail('should have failed with the standard error'); },
        (error: HttpErrorResponse) => {
          expect(alertSpy).toHaveBeenCalledWith('danger', expectedMessage);
          done();
        }
      );

      const req = httpMock.expectOne('');
      expect(req.request.method).toEqual('GET');
      req.error(body as unknown as ErrorEvent, { status: 404, statusText: 'Not Found' });
    });
  });
});
