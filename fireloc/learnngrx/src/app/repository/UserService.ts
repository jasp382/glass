import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UserModel } from '../models/UsersModel';

@Injectable({providedIn: 'root'})
export class UserService {

    constructor(private http: HttpClient) {}

    getUsers() {
        return this.http.get<UserModel[]>('http://localhost:3000/users');
    }

    getUser(id: number) {
        return this.http.get<UserModel>('http://localhost:3000/users/' + id);
    }

    addUser(nuser: UserModel) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );
        return this.http.post<UserModel>(
            'http://localhost:3000/users',
            JSON.stringify(nuser),
            {headers : headers}
        );
    }

    updateUser(nuser: UserModel) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );
        return this.http.put<UserModel>(
            'http://localhost:3000/users/' + nuser.id,
            JSON.stringify(nuser),
            {headers : headers}
        );
    }

    delUser(id: number) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );
        return this.http.delete(
            'http://localhost:3000/users/' + id,
            {headers : headers}
        );
    }
}