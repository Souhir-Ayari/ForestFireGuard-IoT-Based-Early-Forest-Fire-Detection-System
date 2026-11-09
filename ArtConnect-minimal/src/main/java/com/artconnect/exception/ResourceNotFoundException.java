package com.artconnect.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

// Exception levée par le service quand l'id demandé n'existe pas.
// @ResponseStatus(NOT_FOUND) : si elle remonte jusqu'au controller, Spring répond automatiquement 404.
// Ainsi le controller n'a pas besoin de try/catch.
@ResponseStatus(HttpStatus.NOT_FOUND)
public class ResourceNotFoundException extends RuntimeException {

	public ResourceNotFoundException(String message) {
		super(message);
	}
}
