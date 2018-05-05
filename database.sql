-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 05, 2018 at 06:19 AM
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
-- Table structure for table `bans`
--

CREATE TABLE `bans` (
  `id` int(11) NOT NULL,
  `player` int(11) NOT NULL,
  `moderator` int(11) NOT NULL,
  `comment` text NOT NULL,
  `expire` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `bans`
--

INSERT INTO `bans` (`id`, `player`, `moderator`, `comment`, `expire`, `time`, `type`) VALUES
(1, 3, 4, 'Ban test', '2017-11-07 13:20:00', '2017-11-07 12:56:02', 1);

-- --------------------------------------------------------

--
-- Table structure for table `currencies`
--

CREATE TABLE `currencies` (
  `id` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `GOLDEN_NUGGETS` int(11) NOT NULL DEFAULT '0',
  `quest` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `epfcoms`
--

CREATE TABLE `epfcoms` (
  `id` int(11) NOT NULL,
  `mascot` int(11) NOT NULL,
  `message` text NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `friends`
--

CREATE TABLE `friends` (
  `id` int(11) NOT NULL,
  `swid` varchar(40) NOT NULL,
  `friends` text NOT NULL,
  `requests` text NOT NULL,
  `ignored` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

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
-- Table structure for table `musictracks`
--

CREATE TABLE `musictracks` (
  `id` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `data` text NOT NULL,
  `hash` varchar(40) NOT NULL,
  `deleted` int(11) NOT NULL,
  `likes` int(11) NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `ninjas`
--

CREATE TABLE `ninjas` (
  `id` int(11) NOT NULL COMMENT 'penguin id',
  `pid` int(11) NOT NULL,
  `belt` int(2) NOT NULL DEFAULT '0',
  `fire` int(11) NOT NULL DEFAULT '0',
  `water` int(11) NOT NULL DEFAULT '0',
  `snow` int(11) NOT NULL DEFAULT '0',
  `cards` text NOT NULL,
  `matches` text NOT NULL,
  `fire_matches` text NOT NULL,
  `water_matches` text NOT NULL
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
  `moderator` int(1) NOT NULL DEFAULT '0',
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
  `care` text NOT NULL,
  `stamps` text NOT NULL,
  `cover` text NOT NULL,
  `agent` int(1) NOT NULL DEFAULT '0',
  `epf` varchar(50) NOT NULL DEFAULT '0%0',
  `search_msg` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `penguins` (`id`, `username`, `swid`, `nickname`, `password`, `email`, `hash`, `create`, `last_update`, `membership`, `moderator`, `inventory`, `coins`, `head`, `face`, `neck`, `feet`, `hand`, `body`, `photo`, `pin`, `color`, `igloo`, `igloos`, `furnitures`, `floors`, `locations`, `care`, `stamps`, `cover`, `agent`, `epf`, `search_msg`) VALUES
(103, 'test', '{882977da-bf7d-11e7-ac97-a02bb82e593b}', 'Peanut', '5f4dcc3b5aa765d61d8327deb882cf99', 'peanutlabs@bill.com', '1,3|2,1|3,1|4,2|5,1|6,2|7,1|9,2|11,4|12,4|13,1|14,1|17,3|19,3|20,3|21,4|22,3|23,3|24,3|26,1|27,1|29,2|30,1|31,2|32,4|33,1|34,2|35,2|36,1|37,1|38,2|39,2|40,2|41,3|45,1|50,3|51,2|52,2|54,2|55,1|56,1|57,3|58,1|60,1|61,2|62,4|63,1|64,3|66,1|67,2|68,1|69,1|70,1|71,1|74,2|76,2|77,1|78,3|80,2|81,1|83,1|85,2|86,1|89,1|91,1|92,2|93,2|94,2|96,1|98,3|100,4|101,3|102,1|104,2|106,5|108,2|109,2|110,2|111,1|112,2|113,1|202,1|204,1|205,1|206,2|207,1|209,2|210,1|211,1|212,1|213,1|214,3|215,2|216,2|217,2|218,2|219,1|220,1|224,2|226,1|227,1|228,1|229,3|232,1|233,1|234,2|235,1|236,1|237,1|238,1|239,1|241,1|242,3|243,2|244,2|246,1|248,2|252,1|253,1|258,1|259,1|302,3|303,1|304,1|306,3|308,1|309,2|312,1|313,1|316,1|317,1|318,1|319,1|320,2|321,1|322,2|323,3|324,3|325,1|326,2|328,1|329,1|330,2|331,1|332,1|333,1|335,3|336,2|338,2|339,1|340,1|341,1|343,3|345,1|346,3|347,2|348,3|351,1|352,1|356,2|357,1|360,1|401,1|403,2|404,1|405,2|408,1|410,3|411,2|414,1|415,2|416,2|418,2|419,1|420,2|421,1|422,1|423,2|424,2|425,4|426,1|501,1|502,2|504,3|505,3|506,1|507,1|509,1|511,1|512,2|513,2|514,2|515,1|516,2|517,1|518,1|519,1|520,2|521,1|522,2|523,1|525,1|527,2|528,4|529,2|530,1|531,1|532,2|533,2|534,2|535,1|536,3|537,1|538,2|540,1|541,1|544,1|547,1|548,1|549,5|553,2|554,5|557,1|559,1|564,2|565,2|566,1|567,6|568,1|569,1|570,4|571,1|573,1|574,1|575,1|576,1|579,2|580,1|581,1|585,1|586,1|587,1|588,1|590,1|602,1|604,1|605,2|607,1|608,1|609,1|610,1|611,1|612,1|613,3|614,3|615,1|616,4|617,2|618,3|619,1|621,3|624,1|625,2|626,2|627,1|629,2|630,4|631,1|632,2|633,3|634,1|635,1|636,1|637,2|638,3|639,1|641,2|642,1|644,1|645,3|646,1|647,1|649,3|650,1|652,2|654,1|655,1|656,1|657,1|658,2|660,2|661,3|663,1|665,4|666,1|667,1|668,1|669,1|670,2|672,1|673,1|674,2|675,3|676,2|677,1|681,2|682,1|683,2|684,1|686,1|688,3|689,1|690,2|691,2|692,3|694,1|695,1|698,1|699,1|701,1|702,1|703,1|704,1|705,1|706,1|708,1|709,3|711,2|712,3|713,2|714,1|715,1|717,3|718,2|719,1|721,1|722,1|723,1|724,1|728,2|730,2|741,1|742,3|743,1|747,1|749,1|750,1|801,1|802,1|804,1', '2017-02-21 18:30:00', '2018-03-14 13:10:45', '2024-03-30 18:30:00', 2, '1%2%606%607%608%3032%821%8006%8010%8011%4026%4027%6158%4809%1560%3159%5220%118%469%412%184%326%3205%5080%4032%4033%104%4883%4154%4039%8%5%15%429%6025%4120%2013', 819, 429, 0, 0, 0, 0, 0, 9304, 0, 15, 12, '0|1509593153,1|1509593153,73|1509865708', '793|1509593153|1,2208|1509865415|1,2046|1509865436|3,2058|1509865439|2,2054|1509865442|2,2059|1509865444|2,2062|1509865449|2,749|1509865720|1,810|1509865735|1,507|1515848912|6,370|1515851495|1,149|1515935989|1,616|1516085616|1,786|1516102877|3', '0|1509593153,21|1509865462,11|1509865467', '4|1509872170', '1|1%3|1%8|1%27|1%28|1%29|1%30|1%31|1%32|1%33|1%34|1%35|1%36|1%37|1%38|1%103|1%125|1%129|1%130|1%131|1%132|1%26|10%71|0', '14,1512891565|63,1512892202|21,1515849336|20,1519873850', '2|4|4|2%1|606|372|240|225|17%1|608|368|134|0|16%1|607|378|338|0|15', 1, '0%0', NULL);

--
-- Triggers `penguins`
--
CREATE TRIGGER `penguins_OnInsert` BEFORE INSERT ON `penguins` FOR EACH ROW SET NEW.`create` = NOW(),
NEW.`swid` = CONCAT('{', uuid(), '}');

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

-- --------------------------------------------------------
--
-- Indexes for table `bans`
--
ALTER TABLE `bans`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `currencies`
--
ALTER TABLE `currencies`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `epfcoms`
--
ALTER TABLE `epfcoms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `friends`
--
ALTER TABLE `friends`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `swid` (`swid`);

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
-- Indexes for table `musictracks`
--
ALTER TABLE `musictracks`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ninjas`
--
ALTER TABLE `ninjas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `pid` (`pid`);

--
-- Indexes for table `penguins`
--
ALTER TABLE `penguins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `swid` (`swid`);

--
-- Indexes for table `puffles`
--
ALTER TABLE `puffles`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bans`
--
ALTER TABLE `bans`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `currencies`
--
ALTER TABLE `currencies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `epfcoms`
--
ALTER TABLE `epfcoms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `friends`
--
ALTER TABLE `friends`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `igloos`
--
ALTER TABLE `igloos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `mails`
--
ALTER TABLE `mails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;

--
-- AUTO_INCREMENT for table `musictracks`
--
ALTER TABLE `musictracks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `ninjas`
--
ALTER TABLE `ninjas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'penguin id', AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `penguins`
--
ALTER TABLE `penguins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=125;

--
-- AUTO_INCREMENT for table `puffles`
--
ALTER TABLE `puffles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
