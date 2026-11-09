package com.artconnect.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.artconnect.model.Artist;
import com.artconnect.service.ArtistService;

// TP 6) Develop the methods in the controller.
//
// CONTROLLER (le "C" de MVC) : reçoit les requêtes HTTP, appelle le service, renvoie la réponse.
// @RestController : les objets retournés sont convertis en JSON (la "Vue" de MVC est donc le JSON).
// Le controller ne contient pas de logique métier : il délègue tout au service (SOLID - S).
//
//  HTTP    URL                 méthode     statut
//  POST    /api/artists        add         201 Created
//  GET     /api/artists        showAll     200 OK
//  GET     /api/artists/{id}   show        200 OK  (404 si absent)
//  PUT     /api/artists/{id}   modify      200 OK  (404 si absent)
//  DELETE  /api/artists/{id}   delete      204 No Content (404 si absent)
@RestController
@RequestMapping("/api/artists")
public class ArtistController {

	// SOLID - D : on dépend de l'INTERFACE ArtistService, pas de ArtistServiceImpl
	private final ArtistService artistService;

	public ArtistController(ArtistService artistService) {
		this.artistService = artistService;
	}

	@PostMapping
	@ResponseStatus(HttpStatus.CREATED)
	public Artist add(@RequestBody Artist artist) {
		return artistService.add(artist);
	}

	@GetMapping
	public List<Artist> showAll() {
		return artistService.showAll();
	}

	@GetMapping("/{id}")
	public Artist show(@PathVariable Long id) {
		return artistService.show(id);
	}

	@PutMapping("/{id}")
	public Artist modify(@PathVariable Long id, @RequestBody Artist artist) {
		return artistService.modify(id, artist);
	}

	@DeleteMapping("/{id}")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	public void delete(@PathVariable Long id) {
		artistService.delete(id);
	}
}
