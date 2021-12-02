
install.packages("oaxaca")
install.packages("fastDummies")
install.packages("readxl")

library(oaxaca)
library(readxl)
library(fastDummies)

#Введите путь до вашего файла
servants <- read_excel("df_declarations_for_regress.xlsx")

#Создаем дамми-переменные
servants <- dummy_cols(servants, select_columns = c('gender', 'position_standard',
                                                'married', "state_agency_short", "if_children"))

#Переименовываем колонки

names(servants)[names(servants) == 'position_standard_заместитель директора департамента'] <- 'position_zamdirectora_departamenta'
names(servants)[names(servants) == 'position_standard_директор департамента'] <- 'position_director_departamenta'
names(servants)[names(servants) == 'position_standard_заместитель федерального министра'] <- 'position_zamministra'
names(servants)[names(servants) == 'position_standard_начальник отдела'] <- 'position_nachalnic_otdela'
names(servants)[names(servants) == 'position_standard_помощник федерального министра'] <- 'position_pomoshnik_ministra'
names(servants)[names(servants) == 'position_standard_референт'] <- 'position_referent'
names(servants)[names(servants) == 'position_standard_советник федерального министра'] <- 'position_sovetnik_ministra'

#Проводим декомпозицию
results <- oaxaca(formula = log_income_diff ~ position_zamdirectora_departamenta + 
                    position_zamministra + position_nachalnic_otdela +
                    position_pomoshnik_ministra + position_referent + position_sovetnik_ministra +
                    married_yes + if_children_no + state_Минвостокразвития + state_Минкультуры + 
                    state_Минобр + state_Минприроды + state_Минсельхоз + state_Минспорт +
                    state_Минпромторг + state_Минстрой + state_Минтранс + state_Минтруд +
                    state_Минфин + state_Минцифры + state_Минэкономразвития + state_Минэнерго +
                    state_Минюст + year |gender_f, data = servants, R = 1000)


#Смотрим разницу в средних
results$y

#Оцениваем результаты декомпозиции
results$twofold$overall
