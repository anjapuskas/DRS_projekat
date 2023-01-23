CREATE TABLE `kartica` (
  `ime` varchar(50) NOT NULL,
  `brojKartice` varchar(50) NOT NULL,
  `datumIsteka` varchar(10) NOT NULL,
  `kod` varchar(50) NOT NULL,
  PRIMARY KEY (`brojKartice`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `korisnik` (
  `id` int(10) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `ime` varchar(50) NOT NULL,
  `prezime` varchar(50) NOT NULL,
  `adresa` varchar(50) NOT NULL,
  `grad` varchar(50) NOT NULL,
  `drzava` varchar(50) NOT NULL,
  `brojTelefona` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `lozinka` varchar(50) NOT NULL,
  `verifikovan` tinyint(1) NOT NULL,
  `stanjeNaRacunu` int DEFAULT '0',
  `brojKartice` varchar(50) DEFAULT '-1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `racun` (
  `korisnik` varchar(64) NOT NULL,
  `valuta` varchar(5) NOT NULL,
  `iznos` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `transakcije` (
  `id` int(10) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `posiljalac` varchar(50) DEFAULT NULL,
  `primalac` varchar(50) DEFAULT NULL,
  `kolicina` varchar(50) NOT NULL,
  `stanje` varchar(50) DEFAULT 'OBRADA',
  `valuta` varchar(5) DEFAULT NULL,
  `tip` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
