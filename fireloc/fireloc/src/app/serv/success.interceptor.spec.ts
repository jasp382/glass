import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClient, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { api } from 'src/apicons';
import { AlertActions } from '../redux/actions/alertActions';
import { selectLanguage } from '../redux/selectors';

import { SuccessInterceptor } from './success.interceptor';

describe('TS79 SuccessInterceptor', () => {
  let interceptor: SuccessInterceptor;
  let httpMock: HttpTestingController;
  let httpClient: HttpClient;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        NgReduxTestingModule,
      ],
      providers: [
        SuccessInterceptor,
        { provide: HTTP_INTERCEPTORS, useClass: SuccessInterceptor, multi: true },
        AlertActions,
      ]
    });

    // reset redux
    MockNgRedux.reset();

    interceptor = TestBed.inject(SuccessInterceptor);
    httpMock = TestBed.inject(HttpTestingController);
    httpClient = TestBed.inject(HttpClient);
  });

  it('T79.1 should be created', () => { expect(interceptor).toBeTruthy(); });

  it('T79.2 should update app language from redux', () => {
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

  describe('TS79.1 Success in Portuguese', () => {
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

    describe('TS79.1.1 should intercept GET request responses appropriately', () => {
      let body = { status: { code: 'S20' } };

      it('T79.1.1.1 intercept GET users', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Utilizadores</strong> recebidos com sucesso.';

        httpClient.get(api.usersUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.usersUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.2 intercept GET events', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Locais observados</strong> recebidos com sucesso.';

        httpClient.get(api.eventTokenUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.eventTokenUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.3 intercept GET events (no authentication)', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Locais observados</strong> recebidos com sucesso.';

        httpClient.get(api.eventUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.eventUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.4 intercept GET contributions', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Contribuições</strong> recebidas com sucesso.';

        httpClient.get(api.contribsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.contribsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.5 intercept GET groups', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Grupos</strong> recebidos com sucesso.';

        httpClient.get(api.groupsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.groupsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.6 intercept GET real events', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Eventos Reais</strong> recebidos com sucesso.';

        httpClient.get(api.realEventsTokenUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.realEventsTokenUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.7 intercept GET layers', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Camadas geoespaciais</strong> recebidas com sucesso.';

        httpClient.get(api.layersTokenUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.layersTokenUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.8 intercept GET charts', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Gráficos</strong> recebidos com sucesso.';

        httpClient.get(api.chartsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.chartsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.9 intercept GET satellite datasets', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Dados de Satélite</strong> recebidos com sucesso.';

        httpClient.get(api.satDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.satDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.10 intercept GET vetorial datasets', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Dados Vetoriais</strong> recebidos com sucesso.';

        httpClient.get(api.vecDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.vecDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.11 intercept GET raster datasets', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Dados Raster</strong> recebidos com sucesso.';

        httpClient.get(api.rasterDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.rasterDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.12 should ignore other GETs', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.get(api.userUrl).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne(api.userUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.1.1.13 should ignore GET codes different from S20', (done) => {
        body = { status: { code: 'S21' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.get(api.rasterDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne(api.rasterDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });
    });

    describe('TS79.1.2 should intercept POST request responses appropriately', () => {
      it('T79.1.2.1 intercept POST user', (done) => {
        let body = { status: { code: 'S21', message: 'New user was created' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Novo utilizador registado com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.2 intercept POST group', (done) => {
        let body = { status: { code: 'S21', message: 'New Group created!' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Novo grupo criado com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.3 intercept POST real event', (done) => {
        let body = { status: { code: 'S21', message: 'New Real Fire Event added.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Novo evento real criado com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.4 intercept POST layer', (done) => {
        let body = { status: { code: 'S21', message: 'Layer Created' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Nova camada geoespacial criada com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.5 intercept POST charts', (done) => {
        let body = { status: { code: 'S21', message: 'New Chart and its series created.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Novo gráfico criado com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.6 intercept POST raster dataset', (done) => {
        let body = { status: { code: 'S21', message: 'Raster dataset was received and stored' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Novos dados raster criados com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.7 intercept POST vectorial dataset', (done) => {
        let body = { status: { code: 'S21', message: 'Vector dataset was created' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Novos dados vetoriais criados com sucesso.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.8 should ignore other POSTs', (done) => {
        let body = { status: { code: 'S21', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.2.9 should ignore POST codes different from S21', (done) => {
        let body = { status: { code: 'S20', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });
    });

    describe('TS79.1.3 should intercept PUT request responses appropriately', () => {
      it('T79.1.3.1 intercept PUT user', (done) => {
        let body = { status: { code: 'S22', message: 'User edited' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de utilizador atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.2 intercept PUT password', (done) => {
        let body = { status: { code: 'S22', message: 'User password was changed' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Password de utilizador atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.3 intercept PUT user confirmation (and ignore)', (done) => {
        let body = { status: { code: 'S22', message: 'User confirmation token was sended' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');


        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.4 intercept PUT group', (done) => {
        let body = { status: { code: 'S22', message: 'Group updated!' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de grupo atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.5 intercept PUT real event', (done) => {
        let body = { status: { code: 'S22', message: 'Real Fire Event was updated.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de evento real atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.6 intercept PUT layer', (done) => {
        let body = { status: { code: 'S22', message: 'Layer updated' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de camada geoespacial atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.7 intercept PUT group layers', (done) => {
        let body = { status: { code: 'S22', message: 'Relations were edited' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Camadas de grupo atualizadas com sucesso';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.8 intercept PUT chart', (done) => {
        let body = { status: { code: 'S22', message: 'Chart and it\'s series were updated.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de gráfico atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.9 intercept PUT raster dataset', (done) => {
        let body = { status: { code: 'S22', message: 'Raster Dataset Updated' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de dados raster atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.10 intercept PUT vectorial dataset', (done) => {
        let body = { status: { code: 'S22', message: 'Vector Dataset Updated' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Informação de dados vetoriais atualizada com sucesso.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.11 intercept PUT recovery code', (done) => {
        let body = { status: { code: 'X21', message: '' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Código de recuperação foi enviado para o seu email.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.3.12 should ignore PUT codes different from S21 and S22', (done) => {
        let body = { status: { code: 'S20', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });
    });

    describe('TS79.1.4 should intercept DELETE request responses appropriately', () => {
      it('T79.1.4.1 intercept DELETE user', (done) => {
        let body = { status: { code: 'S23', message: 'User deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Utilizador removido com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.2 intercept DELETE group', (done) => {
        let body = { status: { code: 'S23', message: 'User Group deleted.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Grupo removido com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.3 intercept DELETE real event', (done) => {
        let body = { status: { code: 'S23', message: 'Real Fire Event deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Evento real removido com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.4 intercept DELETE layer', (done) => {
        let body = { status: { code: 'S23', message: 'Layer deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Camada geoespacial removida com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.5 intercept DELETE chart', (done) => {
        let body = { status: { code: 'S23', message: 'Chart and it serie deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Gráfico removido com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.6 intercept DELETE satellite dataset', (done) => {
        let body = { status: { code: 'S23', message: 'Image deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Dados de satélite removidos com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.7 intercept DELETE raster dataset', (done) => {
        let body = { status: { code: 'S23', message: "Raster dataset deleted" } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Dados raster removidos com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.8 intercept DELETE vectorial dataset', (done) => {
        let body = { status: { code: 'S23', message: 'Vector dataset deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Dados vetoriais removidos com sucesso.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.1.4.9 should ignore PUT codes different from S22 and S23', (done) => {
        let body = { status: { code: 'S20', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });
    });
  });

  describe('TS79.2 Success in English', () => {
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

    describe('TS79.2.1 should intercept GET request responses appropriately', () => {
      let body = { status: { code: 'S20' } };

      it('T79.2.1.1 intercept GET users', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Users</strong> successfully received.';

        httpClient.get(api.usersUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.usersUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.2 intercept GET events', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Observed locations</strong> successfully received.';

        httpClient.get(api.eventTokenUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.eventTokenUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.3 intercept GET events (no authentication)', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Observed locations</strong> successfully received.';

        httpClient.get(api.eventUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.eventUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.4 intercept GET contributions', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Contributions</strong> successfully received.';

        httpClient.get(api.contribsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.contribsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.5 intercept GET groups', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Groups</strong> successfully received.';

        httpClient.get(api.groupsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.groupsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.6 intercept GET real events', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Real events</strong> successfully received.';

        httpClient.get(api.realEventsTokenUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.realEventsTokenUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.7 intercept GET layers', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Geospatial layers</strong> successfully received.';

        httpClient.get(api.layersTokenUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.layersTokenUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.8 intercept GET charts', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Graphs</strong> successfully received.';

        httpClient.get(api.chartsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.chartsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.9 intercept GET satellite datasets', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Satellite datasets</strong> successfully received.';

        httpClient.get(api.satDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.satDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.10 intercept GET vetorial datasets', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Vetorial datasets</strong> successfully received.';

        httpClient.get(api.vecDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.vecDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.11 intercept GET raster datasets', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = '<strong>Raster datasets</strong> successfully received.';

        httpClient.get(api.rasterDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne(api.rasterDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.12 should ignore other GETs', (done) => {
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.get(api.userUrl).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne(api.userUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });

      it('T79.2.1.13 should ignore GET codes different from S20', (done) => {
        body = { status: { code: 'S21' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.get(api.rasterDatasetsUrl).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne(api.rasterDatasetsUrl);
        expect(req.request.method).toEqual('GET');
        req.flush(body, { status: 200, statusText: 'OK' });
      });
    });

    describe('TS79.2.2 should intercept POST request responses appropriately', () => {
      it('T79.2.2.1 intercept POST user', (done) => {
        let body = { status: { code: 'S21', message: 'New user was created' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New user registered successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.2 intercept POST group', (done) => {
        let body = { status: { code: 'S21', message: 'New Group created!' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New group created successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.3 intercept POST real event', (done) => {
        let body = { status: { code: 'S21', message: 'New Real Fire Event added.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New real event created successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.4 intercept POST layer', (done) => {
        let body = { status: { code: 'S21', message: 'Layer Created' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New geospatial layer created successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.5 intercept POST charts', (done) => {
        let body = { status: { code: 'S21', message: 'New Chart and its series created.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New graph created successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.6 intercept POST raster dataset', (done) => {
        let body = { status: { code: 'S21', message: 'Raster dataset was received and stored' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New raster dataset created successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.7 intercept POST vectorial dataset', (done) => {
        let body = { status: { code: 'S21', message: 'Vector dataset was created' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'New vectorial dataset created successfully.';

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.8 should ignore other POSTs', (done) => {
        let body = { status: { code: 'S21', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.2.9 should ignore POST codes different from S21', (done) => {
        let body = { status: { code: 'S20', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.post('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('POST');
        req.flush(body, { status: 201, statusText: 'OK' });
      });
    });

    describe('TS79.2.3 should intercept PUT request responses appropriately', () => {
      it('T79.2.3.1 intercept PUT user', (done) => {
        let body = { status: { code: 'S22', message: 'User edited' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'User information updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.2 intercept PUT password', (done) => {
        let body = { status: { code: 'S22', message: 'User password was changed' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'User password updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.3 intercept PUT user confirmation (and ignore)', (done) => {
        let body = { status: { code: 'S22', message: 'User confirmation token was sended' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.4 intercept PUT group', (done) => {
        let body = { status: { code: 'S22', message: 'Group updated!' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Group information updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.5 intercept PUT real event', (done) => {
        let body = { status: { code: 'S22', message: 'Real Fire Event was updated.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Real event information updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.6 intercept PUT layer', (done) => {
        let body = { status: { code: 'S22', message: 'Layer updated' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Geospatial layer information updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.7 intercept PUT group layers', (done) => {
        let body = { status: { code: 'S22', message: 'Relations were edited' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Group geospatial layers updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.8 intercept PUT chart', (done) => {
        let body = { status: { code: 'S22', message: 'Chart and it\'s series were updated.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Graph information updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.9 intercept PUT raster dataset', (done) => {
        let body = { status: { code: 'S22', message: 'Raster Dataset Updated' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Raster dataset updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.10 intercept PUT vectorial dataset', (done) => {
        let body = { status: { code: 'S22', message: 'Vector Dataset Updated' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Vetorial dataset updated successfully.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.11 intercept PUT recovery code', (done) => {
        let body = { status: { code: 'X21', message: '' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Password recovery code was sent to your email.';

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.3.12 should ignore PUT codes different from S21 and S22', (done) => {
        let body = { status: { code: 'S20', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.put('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('PUT');
        req.flush(body, { status: 201, statusText: 'OK' });
      });
    });

    describe('TS79.2.4 should intercept DELETE request responses appropriately', () => {
      it('T79.2.4.1 intercept DELETE user', (done) => {
        let body = { status: { code: 'S23', message: 'User deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'User successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.2 intercept DELETE group', (done) => {
        let body = { status: { code: 'S23', message: 'User Group deleted.' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Group successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.3 intercept DELETE real event', (done) => {
        let body = { status: { code: 'S23', message: 'Real Fire Event deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Real event successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.4 intercept DELETE layer', (done) => {
        let body = { status: { code: 'S23', message: 'Layer deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Geospatial layer successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.5 intercept DELETE chart', (done) => {
        let body = { status: { code: 'S23', message: 'Chart and it serie deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Graph successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.6 intercept DELETE satellite dataset', (done) => {
        let body = { status: { code: 'S23', message: 'Image deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Satellite dataset successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.7 intercept DELETE raster dataset', (done) => {
        let body = { status: { code: 'S23', message: "Raster dataset deleted" } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Raster Dataset successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.8 intercept DELETE vectorial dataset', (done) => {
        let body = { status: { code: 'S23', message: 'Vector dataset deleted' } };

        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');
        const expectedMessage = 'Vetorial Dataset successfully removed.';

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).toHaveBeenCalledWith('success', expectedMessage);
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });

      it('T79.2.4.9 should ignore PUT codes different from S22 and S23', (done) => {
        let body = { status: { code: 'S20', message: '' } };
        let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

        httpClient.delete('', {}).subscribe((response: any) => {
          expect(alertSpy).not.toHaveBeenCalled();
          done();
        });

        const req = httpMock.expectOne('');
        expect(req.request.method).toEqual('DELETE');
        req.flush(body, { status: 201, statusText: 'OK' });
      });
    });
  });

  it('T79.3 should just pass successes without status', (done) => {
    let body = {};
    let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

    httpClient.get('', {}).subscribe((response: any) => {
      expect(alertSpy).not.toHaveBeenCalled();
      done();
    });

    const req = httpMock.expectOne('');
    expect(req.request.method).toEqual('GET');
    req.flush(body, { status: 201, statusText: 'OK' });
  });

  it('T79.4 should ignore requests different from GET, POST, PUT and DELETE', (done) => {
    let body = { status: { code: 'S20', message: '' } };
    let alertSpy = spyOn(interceptor['alertActions'], 'addAlert');

    httpClient.patch('', {}).subscribe((response: any) => {
      expect(alertSpy).not.toHaveBeenCalled();
      done();
    });

    const req = httpMock.expectOne('');
    expect(req.request.method).toEqual('PATCH');
    req.flush(body, { status: 201, statusText: 'OK' });
  });
});
