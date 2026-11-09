package com.artconnect.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

// TP 2) Create the entity classes in the model folder.
//
// MODEL (le "M" de MVC) : une classe Java qui représente une ligne de la table "artists".
// @Entity  -> JPA/Hibernate sait que cette classe correspond à une table.
// @Table   -> nom de la table créée dans schema.sql.
// Notre idée : ArtConnect est un réseau social pour artistes, l'artiste est donc l'entité principale.
@Entity
@Table(name = "artists")
public class Artist {

	// Clé primaire, générée par la base (AUTO_INCREMENT)
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	@Column(nullable = false, length = 100)
	private String name;

	// Domaine artistique : PAINTER, MUSICIAN, PHOTOGRAPHER...
	@Column(nullable = false, length = 50)
	private String domain;

	// Constructeur vide obligatoire pour JPA (et pour la conversion JSON -> objet)
	public Artist() {
	}

	public Artist(Long id, String name, String domain) {
		this.id = id;
		this.name = name;
		this.domain = domain;
	}

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDomain() {
		return domain;
	}

	public void setDomain(String domain) {
		this.domain = domain;
	}
}
