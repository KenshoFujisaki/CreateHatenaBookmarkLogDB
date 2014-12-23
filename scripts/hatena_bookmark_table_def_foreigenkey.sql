-- MySQL dump 10.13  Distrib 5.5.28, for osx10.7 (i386)
--
-- Host: localhost    Database: hatena_bookmark
-- ------------------------------------------------------
-- Server version	5.5.28-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `morpheme`
--

DROP TABLE IF EXISTS `morpheme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `morpheme` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `idf` float DEFAULT NULL,
  `ridf` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `morpheme`
--

LOCK TABLES `morpheme` WRITE;
/*!40000 ALTER TABLE `morpheme` DISABLE KEYS */;
/*!40000 ALTER TABLE `morpheme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag`
--

LOCK TABLES `tag` WRITE;
/*!40000 ALTER TABLE `tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `url`
--

DROP TABLE IF EXISTS `url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1024) NOT NULL,
  `title` varchar(512) NOT NULL,
  `update_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url`
--

LOCK TABLES `url` WRITE;
/*!40000 ALTER TABLE `url` DISABLE KEYS */;
/*!40000 ALTER TABLE `url` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `url_content`
--

DROP TABLE IF EXISTS `url_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url_content` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url_id` int(11) NOT NULL,
  `content` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `url_id` (`url_id`),
  CONSTRAINT `url_content_ibfk_1` FOREIGN KEY (`url_id`) REFERENCES `url` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url_content`
--

LOCK TABLES `url_content` WRITE;
/*!40000 ALTER TABLE `url_content` DISABLE KEYS */;
/*!40000 ALTER TABLE `url_content` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `url_morpheme`
--

DROP TABLE IF EXISTS `url_morpheme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url_morpheme` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url_id` int(11) NOT NULL,
  `morpheme_id` int(11) NOT NULL,
  `morpheme_count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `url_id` (`url_id`),
  KEY `morpheme_id` (`morpheme_id`),
  CONSTRAINT `url_morpheme_ibfk_2` FOREIGN KEY (`morpheme_id`) REFERENCES `morpheme` (`id`),
  CONSTRAINT `url_morpheme_ibfk_1` FOREIGN KEY (`url_id`) REFERENCES `url` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url_morpheme`
--

LOCK TABLES `url_morpheme` WRITE;
/*!40000 ALTER TABLE `url_morpheme` DISABLE KEYS */;
/*!40000 ALTER TABLE `url_morpheme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `url_tag`
--

DROP TABLE IF EXISTS `url_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `url_id` (`url_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `url_tag_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`),
  CONSTRAINT `url_tag_ibfk_1` FOREIGN KEY (`url_id`) REFERENCES `url` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url_tag`
--

LOCK TABLES `url_tag` WRITE;
/*!40000 ALTER TABLE `url_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `url_tag` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-05-05 12:34:34
