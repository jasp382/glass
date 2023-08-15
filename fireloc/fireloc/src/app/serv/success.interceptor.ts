import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpResponse
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { api } from 'src/apicons';

// redux
import { AlertActions } from '../redux/actions/alertActions';
import { selectLanguage } from '../redux/selectors';
import { select } from '@angular-redux/store';

/**
 * Interceptor for all API requests made. Intercepts only successful API responses.
 * 
 * Responsible for checking a response and dispatching a self-closing success bootstrap modal with an appropriate message.
 * 
 * See {@link AlertActions} for information on modal content. 
 * See {@link AppComponent} for modal usage.
 */
@Injectable()
export class SuccessInterceptor implements HttpInterceptor {

  /**
   * Holds current app language
   */
  language: string = 'pt';
  /**
   * Redux selector for receiving updates about app language changes
   */
  @select(selectLanguage) language$!: Observable<boolean>;

  /**
   * Constructor for Success Interceptor. Uses alert actions to dispatch an action when bootstrap alert needs to be displayed.
   * 
   * Subscribes to redux updates.
   * @param alertActions Redux actions for bootstrap alert modals
   */
  constructor(private alertActions: AlertActions) { this.subscribeToRedux(); }

  /**
   * Subscribe to redux updates about the current language selected for usage in the app.
   */
  subscribeToRedux() { this.language$.subscribe((language: any) => { this.language = language; }); }

  /**
   * Intercepts requests and responses made to/from the API. Checks whether the intercepted object is a response.
   * 
   * Checks whether the request was of type GET, POST, PUT or DELETE and gets the appropriate message 
   * from the corresponding methods to provide user feedback.
   * If the message is meant to be displayed, it dispatches a Redux action for it.
   * @param request HTTP request made
   * @param next Reference to the next http handler
   * @returns An observable HTTP event
   */
  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      tap((requestSuccess: any) => {
        // check if it is intercepting a response
        if (requestSuccess instanceof HttpResponse) {
          // ignore success from translator service
          if (requestSuccess.body.status) {
            let requestUrl = requestSuccess.url ?? '';
            let statusCode = requestSuccess.body.status.code;
            let statusMessage = requestSuccess.body.status.message;

            // get message for user feedback
            let successMessage;
            if (request.method === 'GET') successMessage = this.handleGetSuccess(statusCode, requestUrl);
            else if (request.method === 'POST') successMessage = this.handlePostSuccess(statusCode, statusMessage);
            else if (request.method === 'PUT') successMessage = this.handlePutSuccess(statusCode, statusMessage);
            else if (request.method === 'DELETE') successMessage = this.handleDeleteSuccess(statusCode, statusMessage);

            // if there is a message, dispatch alert action to display it
            if (successMessage != undefined) {
              // dispatch action for success
              this.alertActions.addAlert('success', successMessage);
            }
          }
        }
        return requestSuccess;
      })
    );
  }

  // TODO MISSING GEOPORTAL REAL EVENTS AND CHARTS
  /**
   * Handles success messages for GET requests' successful responses. Expects code S20.
   * @param code status code provided by the HTTP response
   * @param url URL used to make the request to the API
   * @returns A message to be displayed to the user or undefined if no message to be shown
   */
  handleGetSuccess(code: string, url: string): string | undefined {
    let message;
    if (code === 'S20') {
      if (url.includes(api.usersUrl)) {
        if (this.language === 'pt') return '<strong>Utilizadores</strong> recebidos com sucesso.';
        return '<strong>Users</strong> successfully received.';
      }
      else if (url.includes(api.eventTokenUrl) || url.includes(api.eventUrl)) {
        if (this.language === 'pt') return '<strong>Locais observados</strong> recebidos com sucesso.';
        return '<strong>Observed locations</strong> successfully received.';
      }
      else if (url.includes(api.contribsUrl)) {
        if (this.language === 'pt') return '<strong>Contribuições</strong> recebidas com sucesso.';
        return '<strong>Contributions</strong> successfully received.';
      }
      else if (url.includes(api.groupsUrl)) {
        if (this.language === 'pt') return '<strong>Grupos</strong> recebidos com sucesso.';
        return '<strong>Groups</strong> successfully received.';
      }
      else if (url.includes(api.realEventsTokenUrl) || url.includes(api.realEventsUrl)) {
        if (this.language === 'pt') return '<strong>Eventos Reais</strong> recebidos com sucesso.';
        return '<strong>Real events</strong> successfully received.';
      }
      else if (url.includes(api.layersTokenUrl) || url.includes(api.layersUrl)) {
        if (this.language === 'pt') return '<strong>Camadas geoespaciais</strong> recebidas com sucesso.';
        return '<strong>Geospatial layers</strong> successfully received.';
      }
      else if (url.includes(api.chartsUrl)) {
        if (this.language === 'pt') return '<strong>Gráficos</strong> recebidos com sucesso.';
        return '<strong>Graphs</strong> successfully received.';
      }
      else if (url.includes(api.satDatasetsUrl)) {
        if (this.language === 'pt') return '<strong>Dados de Satélite</strong> recebidos com sucesso.';
        return '<strong>Satellite datasets</strong> successfully received.';
      }
      else if (url.includes(api.vecDatasetsUrl)) {
        if (this.language === 'pt') return '<strong>Dados Vetoriais</strong> recebidos com sucesso.';
        return '<strong>Vetorial datasets</strong> successfully received.';
      }
      else if (url.includes(api.rasterDatasetsUrl)) {
        if (this.language === 'pt') return '<strong>Dados Raster</strong> recebidos com sucesso.';
        return '<strong>Raster datasets</strong> successfully received.';
      }
    }
    return message;
  }

  /**
   * Handles success messages for POST requests' successful responses. Expects code S21.
   * @param code status code provided by the HTTP response
   * @param msg message provided by the HTTP response
   * @returns A message to be displayed to the user or undefined if no message to be shown
   */
  handlePostSuccess(code: string, msg: string): string | undefined {
    let message;
    if (code === 'S21') {
      switch (msg) {
        case 'New user was created':
          if (this.language === 'pt') return 'Novo utilizador registado com sucesso.';
          return 'New user registered successfully.';
        case 'New Group created!':
          if (this.language === 'pt') return 'Novo grupo criado com sucesso.';
          return 'New group created successfully.';
        case 'New Real Fire Event added.':
          if (this.language === 'pt') return 'Novo evento real criado com sucesso.';
          return 'New real event created successfully.';
        case 'Layer Created':
          if (this.language === 'pt') return 'Nova camada geoespacial criada com sucesso.';
          return 'New geospatial layer created successfully.';
        case 'New Chart and its series created.':
          if (this.language === 'pt') return 'Novo gráfico criado com sucesso.';
          return 'New graph created successfully.';
        case 'Raster dataset was received and stored':
          if (this.language === 'pt') return 'Novos dados raster criados com sucesso.';
          return 'New raster dataset created successfully.';
        case 'Vector dataset was created':
          if (this.language === 'pt') return 'Novos dados vetoriais criados com sucesso.';
          return 'New vectorial dataset created successfully.';
      }
    }
    return message;
  }

  /**
   * Handles success messages for PUT requests' successful responses. Expects codes S22 and X21.
   * @param code status code provided by the HTTP response
   * @param msg message provided by the HTTP response
   * @returns A message to be displayed to the user or undefined if no message to be shown
   */
  handlePutSuccess(code: string, msg: string): string | undefined {
    let message;
    if (code === 'S22') {
      switch (msg) {
        case 'User edited':
          if (this.language === 'pt') return 'Informação de utilizador atualizada com sucesso.';
          return 'User information updated successfully.';
        case 'User password was changed':
          if (this.language === 'pt') return 'Password de utilizador atualizada com sucesso.';
          return 'User password updated successfully.';
        case 'Group updated!':
          if (this.language === 'pt') return 'Informação de grupo atualizada com sucesso.';
          return 'Group information updated successfully.';
        case 'Real Fire Event was updated.':
          if (this.language === 'pt') return 'Informação de evento real atualizada com sucesso.';
          return 'Real event information updated successfully.';
        case 'Layer updated':
          if (this.language === 'pt') return 'Informação de camada geoespacial atualizada com sucesso.';
          return 'Geospatial layer information updated successfully.';
        case 'Relations were edited':
          if (this.language === 'pt') return 'Camadas de grupo atualizadas com sucesso';
          return 'Group geospatial layers updated successfully.';
        case 'Chart and it\'s series were updated.':
          if (this.language === 'pt') return 'Informação de gráfico atualizada com sucesso.';
          return 'Graph information updated successfully.';
        case 'Raster Dataset Updated':
          if (this.language === 'pt') return 'Informação de dados raster atualizada com sucesso.';
          return 'Raster dataset updated successfully.';
        case 'Vector Dataset Updated':
          if (this.language === 'pt') return 'Informação de dados vetoriais atualizada com sucesso.';
          return 'Vetorial dataset updated successfully.';
      }
    }
    else if (code === 'X21') {
      if (this.language === 'pt') return 'Código de recuperação foi enviado para o seu email.';
      return 'Password recovery code was sent to your email.';
    }
    return message;
  }

  // Handle DELETE success responses
  /**
   * Handles success messages for DELETE requests' successful responses. Expects code S23.
   * @param code status code provided by the HTTP response
   * @param msg message provided by the HTTP response
   * @returns A message to be displayed to the user or undefined if no message to be shown
   */
  handleDeleteSuccess(code: string, msg: string): string | undefined {
    let message;
    if (code === 'S23') {
      switch (msg) {
        case 'User deleted':
          if (this.language === 'pt') return 'Utilizador removido com sucesso.';
          return 'User successfully removed.';
        case 'User Group deleted.':
          if (this.language === 'pt') return 'Grupo removido com sucesso.';
          return 'Group successfully removed.';
        case 'Real Fire Event deleted':
          if (this.language === 'pt') return 'Evento real removido com sucesso.';
          return 'Real event successfully removed.';
        case 'Layer deleted':
          if (this.language === 'pt') return 'Camada geoespacial removida com sucesso.';
          return 'Geospatial layer successfully removed.';
        case 'Chart and it serie deleted':
          if (this.language === 'pt') return 'Gráfico removido com sucesso.';
          return 'Graph successfully removed.';
        case 'Image deleted':
          if (this.language === 'pt') return 'Dados de satélite removidos com sucesso.';
          return 'Satellite dataset successfully removed.';
        case "Raster dataset deleted":
          if (this.language === 'pt') return 'Dados raster removidos com sucesso.';
          return 'Raster Dataset successfully removed.';
        case 'Vector dataset deleted':
          if (this.language === 'pt') return 'Dados vetoriais removidos com sucesso.';
          return 'Vetorial Dataset successfully removed.';
      }
    }
    return message;
  }
}
