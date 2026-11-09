# ArtConnect – version minimale (MVC, CRUD, tests)

Version réduite d'ArtConnect (réseau social pour artistes) avec **une seule entité : `Artist`**,
pour montrer simplement ce qui a été vu en cours. Spring Boot 4.1.1, Java 25, H2.

## Lancer

```powershell
.\mvnw.cmd spring-boot:run     # API sur http://localhost:8080/api/artists
.\mvnw.cmd test                # 17 tests
```
Console H2 : http://localhost:8080/h2-console (JDBC URL `jdbc:h2:mem:artconnect`, user `sa`).

## Architecture MVC (Controller → Service → Repository → Base)

```
src/main
├── resources/schema.sql                     TP 1  création de la table artists
├── java/com/artconnect/model/Artist.java    TP 2  entité (le M de MVC)
├── repository/ArtistRepository.java         TP 3/6 accès base (JpaRepository)
├── service/ArtistService.java               TP 3/4 interface : add, modify, show, showAll, delete
├── service/ArtistServiceImpl.java           TP 5  implémentation (logique métier)
├── controller/ArtistController.java         TP 6  API REST (le C de MVC, la vue = JSON)
└── exception/ResourceNotFoundException.java id inexistant -> 404
src/test
├── service/ArtistServiceImplTest.java       TP 5 Task 2 : tests unitaires (Mockito @Mock / @InjectMocks)
├── controller/ArtistControllerTest.java     TP 5 Task 1 : tests unitaires (@WebMvcTest + @MockitoBean)
└── ArtistIntegrationTest.java               test d'intégration (@SpringBootTest, vraie base H2)
```

## API CRUD

| HTTP | URL | Méthode | Statut |
|---|---|---|---|
| POST | `/api/artists` | `add` | 201 |
| GET | `/api/artists` | `showAll` | 200 |
| GET | `/api/artists/{id}` | `show` | 200 / 404 |
| PUT | `/api/artists/{id}` | `modify` | 200 / 404 |
| DELETE | `/api/artists/{id}` | `delete` | 204 / 404 |

## Les tests

| Type | Ce qui est testé | Mock ? |
|---|---|---|
| Unitaire service | la classe `ArtistServiceImpl` seule | repository mocké (`@Mock`) |
| Unitaire controller | la couche web seule (HTTP, statut, JSON) | service mocké (`@MockitoBean`) |
| Intégration | les 3 couches ensemble + base H2 | rien |

Les cas demandés dans le TP 5 sont couverts : succès + « not found » pour show, modify, delete,
et la liste vide pour showAll.

## SOLID (expliqué dans les commentaires du code)

- **S** : chaque couche a une seule responsabilité (HTTP / logique métier / base).
- **O** : on peut ajouter une nouvelle implémentation de `ArtistService` sans modifier le controller.
- **L** : `ArtistServiceImpl` (ou un mock) peut remplacer `ArtistService` partout.
- **I** : l'interface `ArtistService` ne contient que les méthodes CRUD utiles.
- **D** : le controller dépend de l'interface `ArtistService`, injectée par constructeur, ce qui permet de la mocker dans les tests.
