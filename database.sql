-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 03, 2017 at 02:41 PM
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

--
-- Dumping data for table `mails`
--

INSERT INTO `mails` (`id`, `to_user`, `from_user`, `type`, `description`, `sent_on`, `opened`, `junk`) VALUES
(1, 3, 0, 1, 'Test Description', '2017-11-02 11:18:49', 1, 1),
(2, 3, 0, 27, 'Test Description', '2017-11-02 11:18:49', 1, 0);
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
  `hands` int(11) NOT NULL DEFAULT '0',
  `body` int(11) NOT NULL DEFAULT '0',
  `photo` int(11) NOT NULL DEFAULT '0',
  `pin` int(11) NOT NULL DEFAULT '0',
  `color` int(11) NOT NULL DEFAULT '1',
  `igloo` int(11) NOT NULL DEFAULT '0',
  `igloos` text NOT NULL,
  `furnitures` text NOT NULL,
  `floors` text NOT NULL,
  `locations` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `penguins`
--

INSERT INTO `penguins` (`id`, `username`, `swid`, `nickname`, `password`, `email`, `hash`, `create`, `last_update`, `membership`, `inventory`, `coins`, `head`, `face`, `neck`, `feet`, `hands`, `body`, `photo`, `pin`, `color`, `igloo`, `igloos`, `furnitures`, `floors`, `locations`) VALUES
(120, 'test', '{882977da-bf7d-11e7-ac97-a02bb82e593b}', 'Peanut', '5f4dcc3b5aa765d61d8327deb882cf99', 'peanutlabs@bill.com', NULL, '2017-11-02 03:25:53', '2017-11-03 13:20:25', '2017-11-02 18:30:00', '1%2%3%1%2%3%1%2%1%2%3%1%2%1%2%3%1%2%3', 500, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, '0|1509593153,1|1509593153', '793|1509593153|1', '0|1509593153', '1|1509593153');

--
-- Triggers `penguins`
--
DELIMITER $$
CREATE TRIGGER `penguins_OnInsert` BEFORE INSERT ON `penguins` FOR EACH ROW SET NEW.`create` = NOW(),
NEW.`swid` = CONCAT('{', uuid(), '}')
$$
DELIMITER ;

--
-- Indexes for dumped tables
--

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
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `igloos`
--
ALTER TABLE `igloos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `mails`
--
ALTER TABLE `mails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `penguins`
--
ALTER TABLE `penguins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
