-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema pollution_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema pollution_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `pollution_db` DEFAULT CHARACTER SET utf8 ;
USE `pollution_db` ;

-- -----------------------------------------------------
-- Table `pollution_db`.`Monitors`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pollution_db`.`Monitors` (
  `Index` INT NOT NULL AUTO_INCREMENT,
  `Location` VARCHAR(45) NULL,
  `geo_point_2d` VARCHAR(45) NULL,
  PRIMARY KEY (`Index`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pollution_db`.`Measurements`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pollution_db`.`Measurements` (
  `Measurement_ID` INT NOT NULL AUTO_INCREMENT,
  `DateTime` DATETIME NULL,
  `NOx` INT(3) NULL,
  `NO2` FLOAT NULL,
  `NO` FLOAT NULL,
  `PM10` FLOAT NULL,
  `NVPM10` FLOAT NULL,
  `VPM10` FLOAT NULL,
  `NVPM2.5` FLOAT NULL,
  `PM2.5` FLOAT NULL,
  `VPM2.5` FLOAT NULL,
  `CO` FLOAT NULL,
  `O3` FLOAT NULL,
  `SO2` FLOAT NULL,
  `Temperature` FLOAT NULL,
  `RH` FLOAT NULL,
  `Air Pressure` VARCHAR(45) NULL,
  `DateStart` DATETIME NULL,
  `DateEnd` DATETIME NULL,
  `Current` VARCHAR(45) NULL,
  `Instrument Type` VARCHAR(45) NULL,
  `SiteID` INT(3) NOT NULL,
  `Monitors_Index` INT NULL,
  PRIMARY KEY (`Measurement_ID`, `SiteID`),
  INDEX `fk_Measurements_Monitors_idx` (`Monitors_Index` ASC) VISIBLE,
  CONSTRAINT `fk_Measurements_Monitors`
    FOREIGN KEY (`Monitors_Index`)
    REFERENCES `pollution_db`.`Monitors` (`Index`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
