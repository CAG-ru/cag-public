library(dplyr)
library(haven)
VNDN <- read_sav("C:/Program Files (x86)/Nesstar/HHOLD.sav")
RMES <- read_sav("C:/Program Files (x86)/Nesstar/r27h_os32.sav")


###Count the consumption spendings(RMES)

#Много NA в изначальном датасете, поэтому я решила заменить их на 0. (Может быть надо по-другому с ними иметь дело.)
my_f = function(a) {
  ifelse(is.na(a), 0, a)
}

rmes1 = RMES
rmes1[c("we1.1c", "we1.2c", "we1.3c", "we1.4c", "we1.5c", "we1.6c", "we1.7c", "we1.8c", "we1.9c", 
        "we1.10c", "we1.11c", "we1.12c", "we1.13c", "we1.14c", "we1.52c", "we1.15c", "we1.16c", "we1.17c", 
        "we1.18c", "we1.19c", "we1.20c", "we1.21c", "we1.22c", "we1.23c", "we1.24c", "we1.25c", "we1.26c", 
        "we1.27c", "we1.28c", "we1.29c", "we1.30c", "we1.31c", "we1.32c", "we1.33c", "we1.34c", "we1.35c", 
        "we1.36c", "we1.37c", "we1.38c", "we1.39c", "we1.40c", "we1.41c", "we1.42c", "we1.43c", "we1.44c", 
        "we1.45c", "we1.46c", "we1.47c", "we1.58c", "we1.59c", "we1.60c", "we1.48c", "we1.49c", "we1.50c", 
        "we1.51c", "we1.53c", "we1.54c", "we1.55c", "we1.56c", "we1.57c", "we3", "we6.1", "we6.2", 
        "we7.1.0b", "we7.1.1b", "we7.2b", "we7.3b", "we7.4b", "we7.5b", "we7.6b","we7.8b", "we13.11b", 
        "we13.12b", "we7.7b", "we7.9b", "we7.10b", "we8.1b", "we8.2b", "we8.3b", "we9.2b", "we9.3b", 
        "we9.4b", "we9.4.1b", "we9.5b","we9.6b", "we9.8b", "we9.9b", "we9.11b", "we9.10b", "we9.7b", 
        "we12.2", "we13.1b", "we13.4b", "we13.2b", "we13.21b", "we13.22b", "we13.23b", "we13.24b", 
        "we13.31b", "we13.32b", "we13.33b", "we13.34b", "we13.35b", "we13.72b")] = 
  lapply(
    rmes1[c("we1.1c", "we1.2c", "we1.3c", "we1.4c", "we1.5c", "we1.6c", "we1.7c", "we1.8c", "we1.9c", 
            "we1.10c", "we1.11c", "we1.12c", "we1.13c", "we1.14c", "we1.52c", "we1.15c", "we1.16c", "we1.17c", 
            "we1.18c", "we1.19c", "we1.20c", "we1.21c", "we1.22c", "we1.23c", "we1.24c", "we1.25c", "we1.26c", 
            "we1.27c", "we1.28c", "we1.29c", "we1.30c", "we1.31c", "we1.32c", "we1.33c", "we1.34c", "we1.35c", 
            "we1.36c", "we1.37c", "we1.38c", "we1.39c", "we1.40c", "we1.41c", "we1.42c", "we1.43c", "we1.44c", 
            "we1.45c", "we1.46c", "we1.47c", "we1.58c", "we1.59c", "we1.60c", "we1.48c", "we1.49c", "we1.50c", 
            "we1.51c", "we1.53c", "we1.54c", "we1.55c", "we1.56c", "we1.57c", "we3", "we6.1", "we6.2", 
            "we7.1.0b", "we7.1.1b", "we7.2b", "we7.3b", "we7.4b", "we7.5b", "we7.6b","we7.8b", "we13.11b", 
            "we13.12b", "we7.7b", "we7.9b", "we7.10b", "we8.1b", "we8.2b", "we8.3b", "we9.2b", "we9.3b", 
            "we9.4b", "we9.4.1b", "we9.5b","we9.6b", "we9.8b", "we9.9b", "we9.11b", "we9.10b", "we9.7b", 
            "we12.2", "we13.1b", "we13.4b", "we13.2b", "we13.21b", "we13.22b", "we13.23b", "we13.24b", 
            "we13.31b", "we13.32b", "we13.33b", "we13.34b", "we13.35b", "we13.72b")], my_f)

my_f1 = function(s) {
  ifelse(s == 99999999 | s == 99999998 | s == 99999997 | s == 99999996, 0, s)
} #remove other forms of na 

rmes1[c("we1.1c", "we1.2c", "we1.3c", "we1.4c", "we1.5c", "we1.6c", "we1.7c", "we1.8c", "we1.9c", 
        "we1.10c", "we1.11c", "we1.12c", "we1.13c", "we1.14c", "we1.52c", "we1.15c", "we1.16c", "we1.17c", 
        "we1.18c", "we1.19c", "we1.20c", "we1.21c", "we1.22c", "we1.23c", "we1.24c", "we1.25c", "we1.26c", 
        "we1.27c", "we1.28c", "we1.29c", "we1.30c", "we1.31c", "we1.32c", "we1.33c", "we1.34c", "we1.35c", 
        "we1.36c", "we1.37c", "we1.38c", "we1.39c", "we1.40c", "we1.41c", "we1.42c", "we1.43c", "we1.44c", 
        "we1.45c", "we1.46c", "we1.47c", "we1.58c", "we1.59c", "we1.60c", "we1.48c", "we1.49c", "we1.50c", 
        "we1.51c", "we1.53c", "we1.54c", "we1.55c", "we1.56c", "we1.57c", "we3", "we6.1", "we6.2", 
        "we7.1.0b", "we7.1.1b", "we7.2b", "we7.3b", "we7.4b", "we7.5b", "we7.6b","we7.8b", "we13.11b", 
        "we13.12b", "we7.7b", "we7.9b", "we7.10b", "we8.1b", "we8.2b", "we8.3b", "we9.2b", "we9.3b", 
        "we9.4b", "we9.4.1b", "we9.5b","we9.6b", "we9.8b", "we9.9b", "we9.11b", "we9.10b", "we9.7b", 
        "we12.2", "we13.1b", "we13.4b", "we13.2b", "we13.21b", "we13.22b", "we13.23b", "we13.24b", 
        "we13.31b", "we13.32b", "we13.33b", "we13.34b", "we13.35b", "we13.72b")] = 
  lapply(
    rmes1[c("we1.1c", "we1.2c", "we1.3c", "we1.4c", "we1.5c", "we1.6c", "we1.7c", "we1.8c", "we1.9c", 
            "we1.10c", "we1.11c", "we1.12c", "we1.13c", "we1.14c", "we1.52c", "we1.15c", "we1.16c", "we1.17c", 
            "we1.18c", "we1.19c", "we1.20c", "we1.21c", "we1.22c", "we1.23c", "we1.24c", "we1.25c", "we1.26c", 
            "we1.27c", "we1.28c", "we1.29c", "we1.30c", "we1.31c", "we1.32c", "we1.33c", "we1.34c", "we1.35c", 
            "we1.36c", "we1.37c", "we1.38c", "we1.39c", "we1.40c", "we1.41c", "we1.42c", "we1.43c", "we1.44c", 
            "we1.45c", "we1.46c", "we1.47c", "we1.58c", "we1.59c", "we1.60c", "we1.48c", "we1.49c", "we1.50c", 
            "we1.51c", "we1.53c", "we1.54c", "we1.55c", "we1.56c", "we1.57c", "we3", "we6.1", "we6.2", 
            "we7.1.0b", "we7.1.1b", "we7.2b", "we7.3b", "we7.4b", "we7.5b", "we7.6b","we7.8b", "we13.11b", 
            "we13.12b", "we7.7b", "we7.9b", "we7.10b", "we8.1b", "we8.2b", "we8.3b", "we9.2b", "we9.3b", 
            "we9.4b", "we9.4.1b", "we9.5b","we9.6b", "we9.8b", "we9.9b", "we9.11b", "we9.10b", "we9.7b", 
            "we12.2", "we13.1b", "we13.4b", "we13.2b", "we13.21b", "we13.22b", "we13.23b", "we13.24b", 
            "we13.31b", "we13.32b", "we13.33b", "we13.34b", "we13.35b", "we13.72b")], my_f1)

##Create product caategories and their annual consumption
rmes = rmes1 %>%
  mutate(bread = (we1.1c + we1.2c)*52, 
         cereal = we1.3c*52,
         flour = we1.4c*52,
         pasta = we1.5c*52,
         vegetables = (we1.6c + we1.7c +we1.8c +we1.9c +we1.10c +we1.11c +we1.12c +we1.13c + we1.14c + we1.52c)*52,
         fruit = (we1.15c + we1.16c +we1.17c +we1.18c +we1.19c)*52,
         nuts = we1.20c*52,
         meat = (we1.21c + we1.22c +we1.23c +we1.24c +we1.25c +we1.26c +we1.27c +we1.28c + we1.29c)*52,
         milk = (we1.30c + we1.31c +we1.32c +we1.33c +we1.34c +we1.35c +we1.36c +we1.37c)*52,
         butter = (we1.38c + we1.39c)*52,
         sugar = we1.40c*52,
         candy = (we1.41c + we1.42c +we1.43c + we1.44c)*52,
         eggs = we1.45c*52,
         fish = (we1.46c + we1.47c +we1.58c +we1.59c)*52,
         food = we1.60c*52,
         beverage = (we1.48c + we1.49c +we1.50c)*52,
         salt = we1.51c*52,
         alcohol = (we1.53c + we1.54c +we1.55c)*52,
         tabacco = we1.56c*52,
         gum = we1.57c*52,
         restaurant = we3*52,
         clothes_adult = we6.1*4,
         clothes_child = we6.2*4,
         electronics = (we7.1.0b + we7.1.1b)*4,
         furniture = (we7.2b + we7.3b)*4,
         vehicle = (we7.4b + we7.5b)*4,
         estate = (we7.6b + we7.8b)*4 + (we13.11b + we13.12b)*12,
         build_materials = we7.7b*4,
         stationary = we7.9b*4,
         sports = we7.10b*4,
         auto_fuel = we8.1b*12,
         fuel = (we8.2b  + we8.3b)*12,
         fix_cloth = we9.2b*12,
         fix_electro = we9.3b*12,
         fix_build = we9.4b*12,
         fix_vehicle = we9.4.1b *12,
         cleaning = we9.5b*12,
         communication = (we9.6b + we9.8b + we9.9b + we9.11b)*12,
         other_services = (we9.10b + we9.7b)*12,
         utilities = we12.2*4,
         education = (we13.1b + we13.4b )*12,
         vacation = we13.2b*12,
         entertainment = we13.21b*12,
         med_service = (we13.22b + we13.23b + we13.24b)*12,
         medicine = we13.31b*12,
         house_chemicals =  (we13.32b + we13.33b + we13.34b)*12,
         pets = we13.35b*12,
         credit = we13.72b*12)


##Prepare RMES dataset for the further imputation
rmes_sort = rmes[, c("WID_H", "w_nfm", "wc3", "wf11", "wf14", "bread", "cereal", "flour","pasta",
                     "vegetables","fruit","nuts","meat","milk","butter", "sugar","candy","eggs", "fish", 
                     "food","beverage","salt", "alcohol", "tabacco", "gum","restaurant", "clothes_adult", 
                     "clothes_child","electronics", "furniture", "vehicle", "estate", "build_materials",
                     "stationary", "sports", "auto_fuel", "fuel", "fix_cloth", "fix_electro","fix_build", 
                     "fix_vehicle", "cleaning","communication","other_services", "utilities", "education",
                     "vacation", "entertainment","med_service", "medicine", "house_chemicals","pets","credit")] %>%
  rename(id = WID_H, people_num = w_nfm, liv_type = wc3, disp_inc = wf11, tot_inc = wf14)%>%
  mutate(origin = "rmes")
rmes_sort$liv_type[rmes_sort$liv_type > 4] <- 6  #to make it similar with the VNDN variable for the living type


##Prepare VNDN dataset for the further imputation
vndn_sort = VNDN[, c("H00_06", "R_2_0", "H04_01", "R_H_DOXOD_RASP", "R_H_DOX_SOVK")]%>%
  rename(id = H00_06, people_num = R_2_0, liv_type = H04_01, disp_inc = R_H_DOXOD_RASP, tot_inc = R_H_DOX_SOVK)
vndn_sort$liv_type[vndn_sort$liv_type == 5] <- 6 #to make it similar with the RMES variable for the living type
vndn_sort$disp_inc = vndn_sort$disp_inc/12 #to get values for 1 month as it is in the RMES
vndn_sort$tot_inc = vndn_sort$tot_inc/12 #to get values for 1 month as it is in the RMES
vndn_sort = vndn_sort %>%
  mutate(bread = NA, 
         cereal = NA,
         flour = NA,
         pasta = NA,
         vegetables = NA,
         fruit = NA,
         nuts = NA,
         meat = NA,
         milk = NA,
         butter = NA,
         sugar = NA,
         candy = NA,
         eggs = NA,
         fish = NA,
         food = NA,
         beverage = NA,
         salt = NA,
         alcohol = NA,
         tabacco = NA,
         gum = NA,
         restaurant = NA,
         clothes_adult = NA,
         clothes_child = NA,
         electronics = NA,
         furniture = NA,
         vehicle = NA,
         estate = NA,
         build_materials = NA,
         stationary = NA,
         sports = NA,
         auto_fuel = NA,
         fuel = NA,
         fix_cloth = NA,
         fix_electro = NA,
         fix_build = NA,
         fix_vehicle = NA,
         cleaning = NA,
         communication = NA,
         other_services = NA,
         utilities = NA,
         education = NA,
         vacation = NA,
         entertainment = NA,
         med_service = NA,
         medicine = NA,
         house_chemicals = NA,
         pets = NA,
         credit = NA,
         origin = "vndn") #future variable for sonsumption spendings

##General dataset for imputation
df = rbind(vndn_sort,rmes_sort)
 
library(Hmisc)
library(rms)
###Дальше идет ошибка
impute_arg <- aregImpute(~ bread+cereal+flour+pasta+vegetables+fruit+nuts+meat+milk+butter+sugar+candy+eggs+
                          fish+food+beverage+salt+alcohol+tabacco+gum+restaurant+clothes_adult+clothes_child+
                          electronics+furniture+vehicle+estate+build_materials+stationary+sports+auto_fuel+
                          fuel+fix_cloth+fix_electro+fix_build+fix_vehicle+cleaning+communication+
                          +other_services+utilities+education+vacation+entertainment+med_service+medicine+
                          house_chemicals+pets+credit, data = df, n.impute = 5)
completed <- impute.transcan(impute_arg, imputation=1, data=df, list.out=TRUE,pr=FALSE, check=FALSE) 

fmi <- fit.mult.impute(~ bread+cereal+flour+pasta+vegetables+fruit+nuts+meat+milk+butter+sugar+candy+eggs+
                         fish+food+beverage+salt+alcohol+tabacco+gum+restaurant+clothes_adult+clothes_child+
                         electronics+furniture+vehicle+estate+build_materials+stationary+sports+auto_fuel+
                         fuel+fix_cloth+fix_electro+fix_build+fix_vehicle+cleaning+communication+
                         +other_services+utilities+education+vacation+entertainment+med_service+medicine+
                         house_chemicals+pets+credit, 
                        ols, impute_arg, data=df)

