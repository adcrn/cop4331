import { Component, Injectable } from '@angular/core';
import { Http, Headers, Response, RequestOptions } from '@angular/http';


@Injectable()
export class YoutubeDlService {

    constructor(private http: Http) { }

    public downloadYoutubeUrl(body: string) {
        console.log('youtube-dl.service url', body);
        return this.http.post('/api/youtube', body);
    }
}