import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

// redux
import { AlertActions } from '../redux/actions/alertActions';
import { selectLanguage } from '../redux/selectors';
import { select } from '@angular-redux/store';

/**
 * Interceptor for all API requests made. Intercepts only API responses that resulted in an Error.
 * 
 * Responsible for checking a response and dispatching a self-closing error bootstrap modal with an appropriate message.
 * 
 * See {@link AlertActions} for information on modal content. 
 * See {@link AppComponent} for modal usage.
 */
@Injectable()
export class ErrorInterceptor implements HttpInterceptor {

  /**
   * Holds current app language
   */
  language: string = 'pt';
  /**
   * Redux selector for receiving updates about app language changes
   */
  @select(selectLanguage) language$!: Observable<boolean>;

  /**
   * Constructor for Error Interceptor. Uses alert actions to dispatch an action when bootstrap alert needs to be displayed.
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
   * Intercepts requests and responses made to/from the API. Catches errors thrown.
   * 
   * Gets the errors status code to be handled by the handleError method (See [handleError]{@link ErrorInterceptor#handleError}).
   * If the message is meant to be displayed, it dispatches a Redux action for it.
   * @param request HTTP request made
   * @param next Reference to the next http handler
   * @returns An observable HTTP event
   */
  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((requestError: any) => {
        // handle API errors
        if (requestError.error.status) {
          let errorCode = requestError.error.status.code;
          let errorMessage = this.handleError(errorCode);

          // dispatch action for error
          this.alertActions.addAlert('danger', errorMessage);

          // send error with error payload
          return throwError({ code: errorCode, message: errorMessage });
        }

        // handle other errors (default error message)
        let otherMessage = this.handleError('');
        // dispatch action for error
        this.alertActions.addAlert('danger', otherMessage);

        return throwError(requestError);
      })
    );
  }

  /**
   * Handles error messages for error responses. Expected codes: 
   * 
   * A: A01, A02
   * 
   * E: E01, E02, E03, E04, E05, E06, E07, E08, E09, E10, E11
   * 
   * I: I01, I02, I03, I04
   * 
   * G: G01, G01, GS1, GS2
   * 
   * X: X01, X02
   * 
   * Z: Z01 (Applied the same as default error message)
   * @param code status code provided by the HTTP status error payload
   * @returns error message with the appropriate user feedback to be displayed
   */
  handleError(code: string): string {
    switch (code) {
      // A
      case 'A01':
        if (this.language === 'pt') return '<strong>Email ou Password incorretas.</strong> Tente novamente.';
        return '<strong>Incorrect Email or Password.</strong> Try again.';
      case 'A02':
        if (this.language === 'pt') return '<strong>Credenciais de autenticação são necessárias.</strong> Tente novamente.';
        return '<strong>Authentication credentials were not provided</strong> Try again.';

      // E
      case 'E01':
        if (this.language === 'pt') return '<strong>Campo obrigatório não preenchido.</strong> Tente novamente.';
        return '<strong>Mandatory field not provided.</strong> Please try again.';
      case 'E02':
        if (this.language === 'pt') return '<strong>Não está a usar uma aplicação FireLoc verificada.</strong>';
        return '<strong>You are not using a verified FireLoc application.</strong>';
      case 'E03':
        if (this.language === 'pt') return '<strong>Não tem permissão para realizar esta operação.</strong>';
        return '<strong>You don\'t have permission to perform this action.</strong>';
      case 'E04':
        if (this.language === 'pt') return '<strong>Operação não permitida.</strong>';
        return '<strong>Action not allowed.</strong>';
      case 'E05':
        if (this.language === 'pt') return '<strong>Dados não se encontram no formato JSON.</strong>';
        return '<strong>Data is not in JSON format.</strong>';
      case 'E06':
        if (this.language === 'pt') return '<strong>Dados inválidos.</strong> Tente novamente.';
        return '<strong>Data is invalid.</strong> Please try again.';
      case 'E07':
        if (this.language === 'pt') return '<strong>Data é inválida.</strong> Tente novamente.';
        return '<strong>Invalid date.</strong> Try again.';
      case 'E08':
        if (this.language === 'pt') return '<strong>Fuso horário é inválido.</strong> Tente novamente.';
        return '<strong>Timezone is invalid.</strong> Please try again.';
      case 'E09':
        if (this.language === 'pt') return '<strong>Dados necessitam de ter a mesma dimensão.</strong> Tente novamente.';
        return '<strong>Data must have the same dimension.</strong> Please try again.';
      case 'E10':
        if (this.language === 'pt') return '<strong>Sistema de referência espacial inválido.</strong> Tente novamente.';
        return '<strong>Spatial reference system is invalid.</strong> Please try again.';
      case 'E11':
        if (this.language === 'pt') return '<strong>Relação topológica é inválida.</strong> Tente novamente.';
        return '<strong>Topological relation is invalid.</strong> Please try again.';

      // I
      case 'I01':
        if (this.language === 'pt') return '<strong>Dados não encontrados.</strong>';
        return '<strong>Data not found.</strong>';
      case 'I02':
        if (this.language === 'pt') return '<strong>Dados já se encontram registados.</strong> Tente novamente.';
        return '<strong>Data already registered.</strong> Please try again.';
      case 'I03':
        if (this.language === 'pt') return '<strong>Dados não encontrados.</strong>';
        return '<strong>Data not found.</strong>';
      case 'I04':
        if (this.language === 'pt') return '<strong>É permitido apenas um valor por atributo.</strong> Tente novamente.';
        return '<strong>Only one value per attribute is allowed.</strong> Please try again.';

      // G
      case 'G01':
        if (this.language === 'pt') return '<strong>Geometria é inválida.</strong> Tente novamente.';
        return '<strong>Geometry is invalid.</strong> Please try again.';
      case 'G02':
        if (this.language === 'pt') return '<strong>EPSG é inválido.</strong> Tente novamente.';
        return '<strong>EPSG is invalid.</strong> Please try again.';
      case 'GS1':
        if (this.language === 'pt') return '<strong>Não foi possível a connecção com o servidor geográfico.</strong> Tente novamente mais tarde.';
        return '<strong>Could not connect to geographical server.</strong> Please try again later.';
      case 'GS2':
        if (this.language === 'pt') return '<strong>Erro do servidor geográfico.</strong> Tente novamente mais tarde.';
        return '<strong>Error from geographical server.</strong> Please try again later.';

      // X
      case 'X01':
        if (this.language === 'pt') return '<strong>Ocorreu um erro e não foi possível enviar email.</strong>';
        return '<strong>An error occured and email was not sent.</strong>';
      case 'X02':
        if (this.language === 'pt') return '<strong>Código de recuperação de password inválido.</strong>';
        return '<strong>Invalid password recovery code.</strong>';

      // default when code Z01 or unexpected
      default:
        if (this.language === 'pt') return 'Ocorreu um erro. Tente novamente mais tarde';
        return 'An error occurred. Try again later.';
    }
  }
}
