package com.artconnect.service;

import java.util.List;

import com.artconnect.model.Artist;

// TP 3) et 4) Interface du service : on DÉCLARE les méthodes CRUD (add, modify, show, delete).
//
// Pourquoi une interface ? Principes SOLID :
//  - D (Dependency Inversion) : le controller dépend de cette abstraction, pas de la classe concrète.
//    On peut donc remplacer l'implémentation (ou la remplacer par un mock dans les tests) sans toucher au controller.
//  - I (Interface Segregation) : l'interface contient seulement ce dont le controller a besoin.
//  - O (Open/Closed) : pour changer le comportement on peut écrire une nouvelle implémentation
//    au lieu de modifier le code existant.
public interface ArtistService {

	// Create
	Artist add(Artist artist);

	// Update : lève ResourceNotFoundException si l'id n'existe pas
	Artist modify(Long id, Artist artist);

	// Read by id : lève ResourceNotFoundException si l'id n'existe pas
	Artist show(Long id);

	// Read all
	List<Artist> showAll();

	// Delete : lève ResourceNotFoundException si l'id n'existe pas
	void delete(Long id);
}
