package com.artconnect.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.artconnect.exception.ResourceNotFoundException;
import com.artconnect.model.Artist;
import com.artconnect.service.ArtistService;

// TP 5 - Task 1 : tests UNITAIRES du controller.
//
// @WebMvcTest démarre SEULEMENT la couche web (ce controller + conversion JSON) : pas de service réel, pas de base.
// MockMvc simule des requêtes HTTP sans lancer de vrai serveur.
// @MockitoBean : comme @Mock, mais le faux service est enregistré dans Spring pour être injecté dans le controller.
// Grâce à l'interface ArtistService (SOLID - D), remplacer le vrai service par un mock est très simple.
@WebMvcTest(ArtistController.class)
class ArtistControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@MockitoBean
	private ArtistService artistService;

	// Create : 201 Created + l'artiste créé dans le corps de la réponse
	@Test
	void add_shouldReturn201AndCreatedArtist() throws Exception {
		when(artistService.add(any(Artist.class))).thenReturn(new Artist(1L, "Claire", "PAINTER"));

		mockMvc.perform(post("/api/artists")
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"name\": \"Claire\", \"domain\": \"PAINTER\"}"))
			.andExpect(status().isCreated())
			.andExpect(jsonPath("$.id").value(1))
			.andExpect(jsonPath("$.name").value("Claire"));
	}

	// Read all : 200 OK + la liste
	@Test
	void showAll_shouldReturn200AndAllArtists() throws Exception {
		when(artistService.showAll()).thenReturn(List.of(
				new Artist(1L, "Claire", "PAINTER"),
				new Artist(2L, "Yanis", "MUSICIAN")));

		mockMvc.perform(get("/api/artists"))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.length()").value(2))
			.andExpect(jsonPath("$[1].name").value("Yanis"));
	}

	// Read by id : l'artiste existe -> 200 OK
	@Test
	void show_shouldReturn200_whenFound() throws Exception {
		when(artistService.show(1L)).thenReturn(new Artist(1L, "Claire", "PAINTER"));

		mockMvc.perform(get("/api/artists/1"))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.name").value("Claire"));
	}

	// Read by id : l'artiste n'existe pas -> 404 Not Found
	@Test
	void show_shouldReturn404_whenNotFound() throws Exception {
		when(artistService.show(99L)).thenThrow(new ResourceNotFoundException("Artist not found with id: 99"));

		mockMvc.perform(get("/api/artists/99"))
			.andExpect(status().isNotFound());
	}

	// Update : succès -> 200 OK + l'artiste modifié
	@Test
	void modify_shouldReturn200_whenFound() throws Exception {
		when(artistService.modify(eq(1L), any(Artist.class))).thenReturn(new Artist(1L, "Claire M.", "PAINTER"));

		mockMvc.perform(put("/api/artists/1")
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"name\": \"Claire M.\", \"domain\": \"PAINTER\"}"))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.name").value("Claire M."));
	}

	// Update : l'artiste n'existe pas -> 404 Not Found
	@Test
	void modify_shouldReturn404_whenNotFound() throws Exception {
		when(artistService.modify(eq(99L), any(Artist.class)))
				.thenThrow(new ResourceNotFoundException("Artist not found with id: 99"));

		mockMvc.perform(put("/api/artists/99")
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"name\": \"X\", \"domain\": \"PAINTER\"}"))
			.andExpect(status().isNotFound());
	}

	// Delete : 204 No Content + le service a bien été appelé
	@Test
	void delete_shouldReturn204AndCallService() throws Exception {
		mockMvc.perform(delete("/api/artists/1"))
			.andExpect(status().isNoContent());

		verify(artistService).delete(1L);
	}
}
