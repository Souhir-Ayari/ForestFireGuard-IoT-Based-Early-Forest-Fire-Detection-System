package com.artconnect.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.artconnect.model.Artist;

// TP 3) et 6) Repository : la couche qui parle à la base de données.
//
// On écrit seulement une interface : Spring Data JPA génère le code à notre place.
// En héritant de JpaRepository<Artist, Long> on obtient déjà :
//   save(artist)   -> INSERT ou UPDATE
//   findAll()      -> SELECT * FROM artists
//   findById(id)   -> SELECT ... WHERE id = ?
//   existsById(id) -> vrai si la ligne existe
//   deleteById(id) -> DELETE ... WHERE id = ?
// Le repository ne contient AUCUNE règle métier : il ne fait que lire/écrire (SOLID - S).
@Repository
public interface ArtistRepository extends JpaRepository<Artist, Long> {
}
