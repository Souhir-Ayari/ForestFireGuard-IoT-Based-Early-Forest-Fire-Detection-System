package com.artconnect.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.artconnect.exception.ResourceNotFoundException;
import com.artconnect.model.Artist;
import com.artconnect.repository.ArtistRepository;

// TP 5) Develop the CRUD methods in the service classes.
//
// SERVICE : contient la logique métier (ex. "on ne modifie pas un artiste qui n'existe pas").
// Il se place entre le controller (HTTP) et le repository (base de données).
// SOLID - S (Single Responsibility) : le service ne connaît ni HTTP ni SQL, seulement les règles métier.
@Service
public class ArtistServiceImpl implements ArtistService {

	private final ArtistRepository artistRepository;

	// Injection de dépendance par constructeur : Spring fournit le repository.
	// Avantage pour les tests : avec Mockito, @InjectMocks passe un faux repository dans ce constructeur.
	public ArtistServiceImpl(ArtistRepository artistRepository) {
		this.artistRepository = artistRepository;
	}

	@Override
	public Artist add(Artist artist) {
		artist.setId(null); // l'id est toujours généré par la base, jamais choisi par le client
		return artistRepository.save(artist);
	}

	@Override
	public Artist modify(Long id, Artist artist) {
		Artist existing = show(id); // 1) récupérer (404 si absent)
		existing.setName(artist.getName()); // 2) modifier
		existing.setDomain(artist.getDomain());
		return artistRepository.save(existing); // 3) enregistrer
	}

	@Override
	public Artist show(Long id) {
		return artistRepository.findById(id)
				.orElseThrow(() -> new ResourceNotFoundException("Artist not found with id: " + id));
	}

	@Override
	public List<Artist> showAll() {
		return artistRepository.findAll();
	}

	@Override
	public void delete(Long id) {
		if (!artistRepository.existsById(id)) {
			throw new ResourceNotFoundException("Artist not found with id: " + id);
		}
		artistRepository.deleteById(id);
	}
}
