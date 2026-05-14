-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1:3307
-- Время создания: Май 13 2026 г., 21:05
-- Версия сервера: 8.0.45
-- Версия PHP: 8.5.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `airport_tracking`
--
CREATE DATABASE IF NOT EXISTS `airport_tracking` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `airport_tracking`;

-- --------------------------------------------------------

--
-- Структура таблицы `airplane`
--
-- Создание: Май 13 2026 г., 20:20
-- Последнее обновление: Май 13 2026 г., 20:20
--

CREATE TABLE `airplane` (
  `airplane_id` int NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `registration_number` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `capacity` int NOT NULL
) ;

--
-- Дамп данных таблицы `airplane`
--

INSERT INTO `airplane` (`airplane_id`, `model`, `registration_number`, `capacity`) VALUES
(1, 'Boeing 737-800', 'RA-73101', 189),
(2, 'Airbus A320neo', 'RA-73205', 180),
(3, 'Sukhoi Superjet 100', 'RA-89001', 100),
(4, 'Boeing 777-300ER', 'RA-77123', 402),
(5, 'Airbus A330-300', 'RA-73310', 293);

-- --------------------------------------------------------

--
-- Структура таблицы `airport`
--
-- Создание: Май 13 2026 г., 20:20
-- Последнее обновление: Май 13 2026 г., 20:27
--

CREATE TABLE `airport` (
  `airport_id` int NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `city` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `country` varchar(100) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп данных таблицы `airport`
--

INSERT INTO `airport` (`airport_id`, `name`, `city`, `country`) VALUES
(1, 'Шереметьево', 'Москва', 'Россия'),
(2, 'Домодедово', 'Москва', 'Россия'),
(3, 'Пулково', 'Санкт-Петербургo', 'Россия'),
(4, 'Толмачёво', 'Новосибирск', 'Россия'),
(5, 'Кольцово', 'Екатеринбург', 'Россия');

-- --------------------------------------------------------

--
-- Структура таблицы `crew`
--
-- Создание: Май 13 2026 г., 20:20
-- Последнее обновление: Май 13 2026 г., 20:20
--

CREATE TABLE `crew` (
  `crew_id` int NOT NULL,
  `last_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `middle_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `qualification` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `position` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `gender` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `date_of_birth` date NOT NULL
) ;

--
-- Дамп данных таблицы `crew`
--

INSERT INTO `crew` (`crew_id`, `last_name`, `first_name`, `middle_name`, `qualification`, `position`, `gender`, `date_of_birth`) VALUES
(1, 'Смирнов', 'Андрей', 'Петрович', 'КВС 1 класса', 'Пилот', 'Мужской', '1978-03-15'),
(3, 'Васильев', 'Сергей', 'Николаевич', 'Старший бортпроводник', 'Бортпроводник', 'Мужской', '1990-11-05'),
(4, 'Попова', 'Мария', 'Дмитриевна', 'Бортпроводник', 'Бортпроводник', 'Женский', '1992-09-18'),
(5, 'Лебедь', 'Михаил', 'Сергеевич', 'КВС', 'Пилот', 'Мужской', '1975-12-30'),
(6, 'Соколова', 'Алина', 'Владимировна', 'Бортпроводник', 'Бортпроводник', 'Женский', '1993-04-12'),
(7, 'Михайлов', 'Денис', 'Алексеевич', 'Второй пилот', 'Второй пилот', 'Мужской', '1982-08-25'),
(8, 'Андреева', 'Светлана', 'Олеговна', 'Старший бортпроводник', 'Бортпроводник', 'Женский', '1988-06-14'),
(9, 'Ходырева', 'Регина', 'Равилевна', 'Бортпроводник', 'Бортпроводник', 'Женский', '2007-03-01');

-- --------------------------------------------------------

--
-- Структура таблицы `flight`
--
-- Создание: Май 13 2026 г., 20:49
--

CREATE TABLE `flight` (
  `flight_id` int NOT NULL,
  `airport_id` int NOT NULL,
  `airplane_id` int NOT NULL,
  `flight_number` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `departure_time` time NOT NULL,
  `arrival_time` time NOT NULL,
  `departure_date` date NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'По расписанию',
  `economy_seats` int NOT NULL DEFAULT '0',
  `business_seats` int NOT NULL DEFAULT '0',
  `first_class_seats` int NOT NULL DEFAULT '0'
) ;

--
-- Дамп данных таблицы `flight`
--

INSERT INTO `flight` (`flight_id`, `airport_id`, `airplane_id`, `flight_number`, `departure_time`, `arrival_time`, `departure_date`, `status`, `economy_seats`, `business_seats`, `first_class_seats`) VALUES
(4, 4, 4, 'SU444', '09:45:00', '14:20:00', '2024-03-16', 'По расписанию', 0, 0, 0),
(6, 1, 2, 'SU606', '07:00:00', '10:15:00', '2024-03-17', 'Выполнен', 0, 0, 0),
(8, 3, 3, 'SU808', '18:50:00', '22:05:00', '2024-03-18', 'По расписанию', 0, 0, 0),
(10, 1, 4, 'SU666', '10:20:00', '12:15:00', '2026-05-04', 'Задержан', 0, 0, 0);

-- --------------------------------------------------------

--
-- Структура таблицы `flight_crew`
--
-- Создание: Май 13 2026 г., 20:20
--

CREATE TABLE `flight_crew` (
  `flight_crew` int NOT NULL,
  `flight_id` int NOT NULL,
  `crew_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `passenger`
--
-- Создание: Май 13 2026 г., 20:20
-- Последнее обновление: Май 13 2026 г., 20:20
--

CREATE TABLE `passenger` (
  `passenger_id` int NOT NULL,
  `last_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `middle_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `passport_data` varchar(11) COLLATE utf8mb4_general_ci NOT NULL,
  `phone_number` varchar(15) COLLATE utf8mb4_general_ci NOT NULL
) ;

--
-- Дамп данных таблицы `passenger`
--

INSERT INTO `passenger` (`passenger_id`, `last_name`, `first_name`, `middle_name`, `passport_data`, `phone_number`) VALUES
(5, 'Мороз', 'Алексей', 'Владимирович', '5678 901234', '+79055678901'),
(6, 'Волкова', 'Ольга', 'Андреевна', '6789 012345', '+79066789012'),
(7, 'Соколов', 'Дмитрий', 'Павлович', '7890 123456', '+79077890123'),
(10, 'Федорова', 'Наталья', 'Александровна', '0123 456789', '+79100123456'),
(11, 'Ходырева', 'Регина', 'Равилевна', '4421 371560', '+79872030797');

-- --------------------------------------------------------

--
-- Структура таблицы `ticket`
--
-- Создание: Май 13 2026 г., 20:25
--

CREATE TABLE `ticket` (
  `ticket_id` int NOT NULL,
  `passenger_id` int NOT NULL,
  `flight_id` int NOT NULL,
  `ticket_number` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `purchase_date` date NOT NULL DEFAULT (curdate()),
  `travel_class` enum('Эконом','Бизнес','Первый') COLLATE utf8mb4_general_ci NOT NULL,
  `seat` varchar(5) COLLATE utf8mb4_general_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Активен'
) ;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--
-- Создание: Май 13 2026 г., 20:44
-- Последнее обновление: Май 13 2026 г., 20:46
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `login` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`id`, `login`, `password`, `role`) VALUES
(1, 'admin', 'admin', 'Администратор'),
(2, 'operator', '123', 'Оператор');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `ticket`
--
ALTER TABLE `ticket`
  MODIFY `ticket_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
