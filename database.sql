-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 06, 2017 at 02:18 PM
-- Server version: 10.1.28-MariaDB
-- PHP Version: 7.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `times-cp`
--

-- --------------------------------------------------------

--
-- Table structure for table `igloos`
--

CREATE TABLE `igloos` (
  `id` int(11) NOT NULL,
  `owner` int(11) NOT NULL,
  `type` int(11) NOT NULL DEFAULT '1',
  `floor` int(11) NOT NULL DEFAULT '0',
  `music` int(11) NOT NULL DEFAULT '0',
  `furniture` text NOT NULL,
  `location` int(11) NOT NULL DEFAULT '0',
  `likes` text NOT NULL,
  `locked` tinyint(4) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `mails`
--

CREATE TABLE `mails` (
  `id` int(11) NOT NULL,
  `to_user` int(11) NOT NULL,
  `from_user` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `description` text NOT NULL,
  `sent_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `opened` tinyint(4) NOT NULL DEFAULT '0',
  `junk` tinyint(4) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `penguins`
--

CREATE TABLE `penguins` (
  `id` int(11) NOT NULL,
  `username` varchar(12) NOT NULL,
  `swid` char(38) NOT NULL,
  `nickname` varchar(20) NOT NULL,
  `password` varchar(32) NOT NULL,
  `email` varchar(50) NOT NULL,
  `hash` text,
  `create` timestamp NULL DEFAULT NULL,
  `last_update` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `membership` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'membership expiry',
  `inventory` text,
  `coins` int(11) NOT NULL DEFAULT '500',
  `head` int(11) NOT NULL DEFAULT '0',
  `face` int(11) NOT NULL DEFAULT '0',
  `neck` int(11) NOT NULL DEFAULT '0',
  `feet` int(11) NOT NULL DEFAULT '0',
  `hand` int(11) NOT NULL DEFAULT '0',
  `body` int(11) NOT NULL DEFAULT '0',
  `photo` int(11) NOT NULL DEFAULT '0',
  `pin` int(11) NOT NULL DEFAULT '0',
  `color` int(11) NOT NULL DEFAULT '1',
  `igloo` int(11) NOT NULL DEFAULT '0',
  `igloos` text NOT NULL,
  `furnitures` text NOT NULL,
  `floors` text NOT NULL,
  `locations` text NOT NULL,
  `care` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `penguins`
--

INSERT INTO `penguins` (`id`, `username`, `swid`, `nickname`, `password`, `email`, `hash`, `create`, `last_update`, `membership`, `inventory`, `coins`, `head`, `face`, `neck`, `feet`, `hand`, `body`, `photo`, `pin`, `color`, `igloo`, `igloos`, `furnitures`, `floors`, `locations`, `care`) VALUES
(3, 'test', '{882977da-bf7d-11e7-ac97-a02bb82e593b}', 'Peanut', '5f4dcc3b5aa765d61d8327deb882cf99', 'peanutlabs@bill.com', NULL, '2017-11-02 03:25:53', '2017-11-06 08:41:23', '2017-11-06 18:30:00', '1%2%3', 14695, 0, 2075, 0, 0, 0, 0, 0, 501, 16, 2, '0|1509593153,1|1509593153,73|1509865708', '793|1509593153|1,2208|1509865415|1,2046|1509865436|2,2058|1509865439|2,2054|1509865442|2,2059|1509865444|2,2062|1509865449|2,749|1509865720|1,810|1509865735|1', '0|1509593153,21|1509865462,11|1509865467', '4|1509872170', ''),
(4, 'test2', '{24aee21f-c2ce-11e7-a02a-a02bb82e593b}', 'Roulette', '5f4dcc3b5aa765d61d8327deb882cf99', 'peanutlabs@bill.com', NULL, '2017-11-06 08:40:29', '2017-11-06 08:40:29', '2017-11-29 18:30:00', '1', 200, 0, 0, 0, 0, 0, 0, 0, 0, 1, 7, '0|1509593153,1|1509593153', '793|1509957629|1', '0|1509593153', '1|1509957629', '');

--
-- Triggers `penguins`
--
DELIMITER $$
CREATE TRIGGER `penguins_OnInsert` BEFORE INSERT ON `penguins` FOR EACH ROW SET NEW.`create` = NOW(),
NEW.`swid` = CONCAT('{', uuid(), '}')
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `puffles`
--

CREATE TABLE `puffles` (
  `id` int(11) NOT NULL,
  `owner` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `type` int(11) NOT NULL,
  `subtype` int(11) NOT NULL DEFAULT '0',
  `adopted` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `food` int(11) NOT NULL DEFAULT '100',
  `play` int(11) NOT NULL DEFAULT '100',
  `rest` int(11) NOT NULL DEFAULT '100',
  `clean` int(11) NOT NULL DEFAULT '100',
  `hat` int(11) NOT NULL DEFAULT '0',
  `backyard` int(11) NOT NULL DEFAULT '0',
  `walking` int(11) NOT NULL DEFAULT '0',
  `lastcare` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for table `igloos`
--
ALTER TABLE `igloos`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `mails`
--
ALTER TABLE `mails`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `penguins`
--
ALTER TABLE `penguins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `swid` (`swid`),
  ADD UNIQUE KEY `igloo` (`igloo`);

--
-- Indexes for table `puffles`
--
ALTER TABLE `puffles`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `igloos`
--
ALTER TABLE `igloos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `mails`
--
ALTER TABLE `mails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `penguins`
--
ALTER TABLE `penguins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `puffles`
--
ALTER TABLE `puffles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
