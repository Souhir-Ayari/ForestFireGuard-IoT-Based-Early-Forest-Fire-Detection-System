package com.artconnect.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.artconnect.exception.ResourceNotFoundException;
import com.artconnect.model.Artist;
import com.artconnect.repository.ArtistRepository;

// TP 5 - Task 2 : tests UNITAIRES du service.
//
// Test unitaire = on teste UNE classe seule, isolée de tout le reste.
// Ici : pas de Spring, pas de base de données. Le repository est remplacé par un MOCK (un faux objet).
//  @Mock        -> Mockito crée un faux ArtistRepository : il ne fait rien sauf ce qu'on lui dit avec when(...)
//  @InjectMocks -> Mockito crée le VRAI ArtistServiceImpl et lui passe le mock dans son constructeur
// Chaque test suit le schéma : Arrange (préparer) / Act (appeler) / Assert (vérifier).
@ExtendWith(MockitoExtension.class)
class ArtistServiceImplTest {

	@Mock
	private ArtistRepository artistRepository;

	@InjectMocks
	private ArtistServiceImpl artistService;

	// Create : le repository save() est appelé et l'artiste enregistré est retourné
	@Test
	void add_shouldSaveAndReturnArtist() {
		Artist input = new Artist(null, "Claire", "PAINTER");
		Artist saved = new Artist(1L, "Claire", "PAINTER");
		when(artistRepository.save(input)).thenReturn(saved);

		Artist result = artistService.add(input);

		assertThat(result.getId()).isEqualTo(1L);
		verify(artistRepository).save(input);
	}

	// Read all : la liste du repository est retournée
	@Test
	void showAll_shouldReturnAllArtists() {
		when(artistRepository.findAll()).thenReturn(List.of(
				new Artist(1L, "Claire", "PAINTER"),
				new Artist(2L, "Yanis", "MUSICIAN")));

		List<Artist> result = artistService.showAll();

		assertThat(result).hasSize(2);
	}

	// Read all : cas de la liste vide
	@Test
	void showAll_shouldReturnEmptyList_whenNoArtist() {
		when(artistRepository.findAll()).thenReturn(List.of());

		assertThat(artistService.showAll()).isEmpty();
	}

	// Read by id : l'artiste existe
	@Test
	void show_shouldReturnArtist_whenFound() {
		when(artistRepository.findById(1L)).thenReturn(Optional.of(new Artist(1L, "Claire", "PAINTER")));

		Artist result = artistService.show(1L);

		assertThat(result.getName()).isEqualTo("Claire");
	}

	// Read by id : l'artiste n'existe pas -> exception
	@Test
	void show_shouldThrow_whenNotFound() {
		when(artistRepository.findById(99L)).thenReturn(Optional.empty());

		assertThatThrownBy(() -> artistService.show(99L)).isInstanceOf(ResourceNotFoundException.class);
	}

	// Update : récupérer, modifier, enregistrer
	@Test
	void modify_shouldUpdateAndSave_whenFound() {
		Artist existing = new Artist(1L, "Claire", "PAINTER");
		when(artistRepository.findById(1L)).thenReturn(Optional.of(existing));
		when(artistRepository.save(existing)).thenReturn(existing);

		Artist result = artistService.modify(1L, new Artist(null, "Claire M.", "PHOTOGRAPHER"));

		assertThat(result.getName()).isEqualTo("Claire M.");
		assertThat(result.getDomain()).isEqualTo("PHOTOGRAPHER");
		verify(artistRepository).save(existing);
	}

	// Update : l'artiste n'existe pas -> exception et rien n'est enregistré
	@Test
	void modify_shouldThrow_whenNotFound() {
		when(artistRepository.findById(99L)).thenReturn(Optional.empty());

		assertThatThrownBy(() -> artistService.modify(99L, new Artist(null, "X", "PAINTER")))
				.isInstanceOf(ResourceNotFoundException.class);
		verify(artistRepository, never()).save(any());
	}

	// Delete : l'artiste existe -> deleteById est appelé
	@Test
	void delete_shouldDelete_whenFound() {
		when(artistRepository.existsById(1L)).thenReturn(true);

		artistService.delete(1L);

		verify(artistRepository).deleteById(1L);
	}

	// Delete : l'artiste n'existe pas -> exception et rien n'est supprimé
	@Test
	void delete_shouldThrow_whenNotFound() {
		when(artistRepository.existsById(99L)).thenReturn(false);

		assertThatThrownBy(() -> artistService.delete(99L)).isInstanceOf(ResourceNotFoundException.class);
		verify(artistRepository, never()).deleteById(any());
	}
}
