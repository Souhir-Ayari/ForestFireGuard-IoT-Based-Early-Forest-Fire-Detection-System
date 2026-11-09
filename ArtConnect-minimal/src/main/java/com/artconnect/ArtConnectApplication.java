package com.artconnect;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// Point d'entrée de l'application. @SpringBootApplication demande à Spring de scanner ce package
// et ses sous-packages (controller, service, repository, model) pour créer les objets ("beans").
@SpringBootApplication
public class ArtConnectApplication {

	public static void main(String[] args) {
		SpringApplication.run(ArtConnectApplication.class, args);
	}
}
