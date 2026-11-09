package com.artconnect;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import com.jayway.jsonpath.JsonPath;

// Test d'INTÉGRATION : contrairement aux tests unitaires, RIEN n'est mocké.
// @SpringBootTest démarre toute l'application : controller -> service -> repository -> vraie base H2.
// On vérifie que les 3 couches fonctionnent ENSEMBLE, sur le cycle complet CRUD d'un artiste.
@SpringBootTest
@AutoConfigureMockMvc
class ArtistIntegrationTest {

	@Autowired
	private MockMvc mockMvc;

	@Test
	void crud_shouldCreateReadUpdateAndDeleteAnArtist() throws Exception {
		// Create
		String body = mockMvc.perform(post("/api/artists")
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"name\": \"Lina\", \"domain\": \"PHOTOGRAPHER\"}"))
			.andExpect(status().isCreated())
			.andReturn().getResponse().getContentAsString();
		Integer id = JsonPath.read(body, "$.id"); // id généré par la base

		// Read
		mockMvc.perform(get("/api/artists/" + id))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.name").value("Lina"));

		// Update
		mockMvc.perform(put("/api/artists/" + id)
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"name\": \"Lina K.\", \"domain\": \"PAINTER\"}"))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.domain").value("PAINTER"));

		// Delete, puis l'artiste n'existe plus -> 404
		mockMvc.perform(delete("/api/artists/" + id)).andExpect(status().isNoContent());
		mockMvc.perform(get("/api/artists/" + id)).andExpect(status().isNotFound());
	}
}
