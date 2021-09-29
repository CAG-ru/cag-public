
#load necessary libraries
library(tidyverse)
library(simpleboot)
library(texreg)
library(rms)
library(sjPlot)
library(stargazer)


#load data

load('replication_data.RData')

# or separately with 3 .scv files

#data <- read.csv('data_2015_2021.csv', row.names = 1)
#orv_info <- read.csv('meta_data_2013_2021.csv', row.names = 1)
#data_okved <- read.csv('data_okved_2013_2021.csv', row.names = 1)

###########################################
############### Figure 1 ##################
###########################################


df_n <- orv_info %>%
  group_by(year, D.aval.text) %>%
  summarise(n = n()) %>%
  group_by(year) %>%
  mutate(N = sum(n),
         s = n/N) 

orv_info %>%
  group_by(year, D.aval.text) %>%
  summarise(n = n()) %>%
  group_by(year) %>%
  mutate(N = sum(n),
         s = n/N) %>%
  ggplot(aes(x = year, y = s, fill = D.aval.text, color = D.aval.text))+
  geom_bar(stat = 'identity', width = 0.8)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'),
        legend.title = element_blank(),
        legend.position = 'bottom')+
  labs(title = NULL, x=NULL, y=NULL)+
  guides(color=guide_legend(nrow=2, byrow=TRUE),
         fill=guide_legend(nrow=2, byrow=TRUE))+
  scale_fill_brewer(palette = 'Dark2')+
  scale_color_brewer(palette = 'Dark2')+
  scale_x_continuous(breaks = seq(2012, 2021))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), 
                     breaks = seq(0,1,.2))





###########################################
############### Figure 2 ##################
###########################################



df_n <- orv_info %>% filter(year > 2014) %>%
  group_by(foiv, D.aval.text) %>%
  summarise(n = n()) %>%
  group_by(foiv) %>%
  mutate(pc = n/sum(n),
         N = sum(n),
         foiv = paste(foiv,  ' (', N, ')', sep = ''))

df_t <- df_n[df_n$D.aval.text == 'Текст отчёта разобран на графы',]

df_t <- df_t[order(df_t$pc, decreasing = T),]$foiv

df_n$foiv <- factor(df_n$foiv, 
                    levels = df_t)



df_n %>%
  ggplot(aes(y = foiv, x = pc, color = D.aval.text, fill = D.aval.text))+
  geom_bar(stat = 'identity', position = position_stack(reverse = T), width = 0.8)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'),
        legend.position = 'bottom',
        legend.title = element_blank())+
  labs(title = NULL, x=NULL, y=NULL)+
  guides(color=guide_legend(nrow=2, byrow=TRUE),
         fill=guide_legend(nrow=2, byrow=TRUE))+
  scale_fill_brewer(palette = 'Dark2')+
  scale_color_brewer(palette = 'Dark2')+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1))





###########################################
############### Figure 3 ##################
###########################################




orv_info$impact <- factor(orv_info$impact, levels = c( "Не определена", 'Низкая', "Средняя", "Высокая"))


df_n <- orv_info %>% group_by(year) %>%
  summarise(N = n())
df_n$impact <- NA
df_n$impact <- factor(df_n$impact, levels = c("Не определена", 'Низкая', "Средняя", "Высокая"))


df_t <- orv_info %>% group_by(year, impact) %>%
  summarise(n = n()) %>%
  as.data.frame()
df_t$impact <- factor(df_t$impact, levels = c("Не определена", 'Низкая', "Средняя", "Высокая"))




ggplot() +
  geom_text(data = df_n, aes(label=N, y = N, x = year), vjust=-.4,hjust = .5, size=5)+
  geom_bar(data = df_t, stat = 'identity', aes(y = n, x=year, fill = impact), position = position_stack(reverse = T), 
           width = 0.6)+
  theme_minimal()+
  labs(x=NULL, y = NULL)+
  theme(#axis.text.y = element_text(size  = 12, color = 'black'),
    plot.title = element_text(hjust = 0.5, face = 'bold'),
    legend.position = 'bottom')+
  scale_fill_brewer(palette = 'Dark2',  name = 'Степень воздействия')+
  scale_color_brewer(palette = 'Dark2', name = 'Степень воздействия')+
  scale_x_continuous(breaks = seq(2012, 2021))







###########################################
############### Figure 4 ##################
###########################################


orv_info$kind <- factor(orv_info$kind, levels = c("Проект ведомственного акта",
                                                  "Проект постановления Правительства",
                                                  "Проект федерального закона",
                                                  "Проект поправок к проекту ФЗ",
                                                  "Проект указа Президента",
                                                  "Проект решения ЕЭК"
)
)

orv_info$impact <- factor(orv_info$impact, levels = c('Не определена', 'Низкая', "Средняя", "Высокая"))



df_n <- orv_info %>%
  group_by(kind, impact) %>%
  summarise(n = n()) %>%
  group_by(impact) %>%
  mutate(N= sum(n),
         pc = n/N)



df_n %>%
  ggplot(aes(y = impact, x = pc, fill = kind, color = kind))+
  geom_bar(stat = 'identity', position = position_stack(reverse = T), width = 0.6)+
  theme_minimal()+
  theme(legend.position = 'bottom',
        legend.title = element_blank(),
        axis.title.x  = element_blank(),
        axis.title.y  = element_blank())+
  scale_fill_brewer(palette = 'Dark2')+
  scale_color_brewer(palette = 'Dark2')+
  guides(color=guide_legend(nrow=3, byrow=TRUE),
         fill=guide_legend(nrow=3, byrow=TRUE))+
  scale_x_continuous(breaks = seq(0, 1, .2), labels = scales::percent_format(accuracy = 1))



###########################################
############### Figure 5 ##################
###########################################





df_n <- orv_info %>%
  group_by(foiv) %>%
  summarise(n = n()) 

df_n <- df_n[order(df_n$n, decreasing = T),]

df_n$foiv <- factor(df_n$foiv, 
                         levels = df_n$foiv)



df_n %>%
  ggplot(aes(x = n, y = foiv)) +
  geom_bar(stat="identity", fill = 'lightgray', color = 'black', width = 0.8)+
  geom_text(aes(label=n), vjust=.5,hjust = -0.1, size=4)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'))+
  xlim(c(0, 1700))


###########################################
############### Figure 6 ##################
###########################################






df_n <- orv_info %>% filter(impact != "Не определена") %>%
  group_by(foiv, impact) %>%
  summarise(n = n()) %>%
  group_by(foiv) %>%
  mutate(pc = n/sum(n),
         N = sum(n),
         foiv = paste(foiv,  ' (', N, ')', sep = ''))

df_n$impact <- factor(df_n$impact, levels = c('Низкая', "Средняя", "Высокая"))

df_t <- df_n[df_n$impact== 'Низкая',]

df_t <- df_t[order(df_t$pc, decreasing = T),]$foiv

df_n$foiv <- factor(df_n$foiv, 
                    levels = df_t)




df_n %>%
  ggplot(aes(y = foiv, x = pc, color = impact, fill = impact))+
  geom_bar(stat = 'identity', position = position_stack(reverse = T), width = 0.8)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'),
        legend.position = 'bottom')+
  scale_fill_brewer(palette = 'Dark2',  name = 'Степень воздействия')+
  scale_color_brewer(palette = 'Dark2', name = 'Степень воздействия')+
  scale_x_continuous(breaks = seq(0, 1, .2), labels = scales::percent_format(accuracy = 1))


###########################################
############### Figure 7 ##################
###########################################



df_n <- orv_info %>% group_by(year) %>%
  summarise(n = median(views))



df_n %>%
  ggplot(aes(x = year, y = n))+
  geom_line()+
  geom_point()+
  theme_minimal()+
  labs(x=NULL, y = NULL)+
  ylim(c(0, 1200))+
  scale_x_continuous(breaks = seq(2013, 2021))


###########################################
############### Figure 8 ##################
###########################################



df_n <- orv_info %>% group_by(year) %>%
  summarise(`Голос "За"` = sum(likes > 0)/n(),
             `Голос "Против"` = sum(dislikes > 0)/n(),
                 Отзыв = sum(comments > 0, na.rm = T)/n()) %>%
  reshape2::melt(id.vars = 'year')

df_n$variable  <- as.character(df_n$variable )


ggplot(df_n, aes(x = year, y = value, color = variable, group =variable))+
  geom_line()+
  geom_point()+
  theme_minimal()+
  theme(legend.position = 'bottom',
        legend.title = element_blank())+
  labs(x=NULL, y = NULL)+
  scale_color_brewer(palette = 'Dark2')+
  scale_x_continuous(breaks = seq(2013, 2021))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     lim = c(0, 0.50))






###########################################
############### Figure 9 ##################
###########################################



df_n <- orv_info %>%
  mutate(res.b = ifelse(result == 'Не определено', 'Нет заключения', 'Есть заключение')) %>%
  group_by(year, res.b) %>%
  summarise(n = n()) %>%
  group_by(year) %>%
  mutate(N = sum(n),
        pc = n/N)

df_n %>%
  ggplot(aes(x = year, y = pc, fill = res.b, color = res.b))+
  geom_bar(stat = 'identity', width = 0.8)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'),
        legend.title = element_blank(),
        legend.position = 'bottom')+
  labs(title = NULL, x=NULL, y=NULL)+
  guides(color=guide_legend(nrow=2, byrow=TRUE),
         fill=guide_legend(nrow=2, byrow=TRUE))+
  scale_fill_brewer(palette = 'Dark2')+
  scale_color_brewer(palette = 'Dark2')+
  scale_x_continuous(breaks = seq(2012, 2021))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2))



###########################################
############### Figure 10 #################
###########################################



df_n <- orv_info %>% filter(active.d == 1 & 
                              result %in% c("Положительное", "Отрицательное")) %>%
  group_by(year, result) %>%
  summarise(n = n()) %>%
  group_by(year) %>%
  mutate(pc = n/sum(n),
         N = sum(n))


df_n$result <- factor(df_n$result, levels = c("Положительное", "Отрицательное"))



df_n %>%
  ggplot(aes(y = pc, x = year, color = result, fill = result))+
  geom_bar(stat = 'identity', position = position_stack(reverse = T), width = 0.8)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(
    plot.title = element_text(hjust = 0.5, face = 'bold'),
    legend.position = 'bottom')+
  scale_fill_brewer(palette = 'Dark2',  name = 'Заключение')+
  scale_color_brewer(palette = 'Dark2', name = 'Заключение')+
  scale_x_continuous(breaks = seq(2013, 2021))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2))





###########################################
############### Figure 11 #################
###########################################



data %>% filter(active.d == 1) %>%
  ggplot(aes(x = total_index/100))+
  geom_histogram(fill = 'lightgrey', alpha = 0.5, color = 'black', breaks = seq(0, 1, 0.04))+
  theme_minimal()+
  labs(x='Процент заполнения', y = 'Количество')+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2))+
  scale_y_continuous(breaks = seq(0, 1250, 250))



###########################################
############### Figure 12 #################
###########################################


df_n <- data %>% filter(active.d == 1) %>%
  group_by(impact, year) %>%
  summarise(pc = mean(total_index)) 

df_n$impact <- factor(df_n$impact, levels = c('Низкая', "Средняя", "Высокая"))


df_n %>% 
  ggplot(aes(x = year, y = pc/100, color = impact, group = impact)) +
  geom_point()+
  geom_line()+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(
    plot.title = element_text(hjust = 0.5, face = 'bold'),
    legend.position = 'bottom')+
  scale_color_brewer(palette = 'Dark2', name = 'Степень воздействия')+
  scale_x_continuous(breaks = seq(2015, 2021))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks =  seq(0, 0.8, 0.2),
                     lim = c(0, 0.8))




###########################################
############### Figure 13 #################
###########################################



grps <- levels(factor((str_split(colnames(data %>% select(ends_with('_valid'))),
                                 '@', simplify = T)[,1])))


df_g <- data.frame()
df_g2 <- data.frame()


for (grp in grps){
  
  
  df_t <- data %>% filter(active.d==1) %>% select(impact, starts_with(grp) & ends_with('_valid'))
  
  df_t$valid <- rowSums(df_t %>% select(ends_with('_valid')), na.rm = T)
  df_t$relevant <- apply(df_t %>% select(ends_with('_valid')), 1, function(x) length(which(!is.na(x))))
  
  df_t <- df_t %>% group_by(impact) %>%
    summarise(index = sum(valid)/sum(relevant))
  
  df_t$group <- grp
  df_g <- rbind(df_g, df_t)
  
  
  
  
  df_t <- data %>% filter(active.d==1) %>% select(impact, starts_with(grp) & ends_with('_valid'))
  df_t$valid <- rowSums(df_t %>% select(ends_with('_valid')), na.rm = T)
  df_t$relevant <- apply(df_t %>% select(ends_with('_valid')), 1, function(x) length(which(!is.na(x))))
  
  
  df_t <- df_t %>% 
    summarise(index = sum(valid)/sum(relevant))
  
  df_t$group <- grp
  
  df_g2 <- rbind(df_g2, df_t)
  
  
}



text2name <- c('general_info' = 'Общая\nинформация', 
               'problem' = 'Описание\nпроблемы',
               'int_exp' = 'Международный\nопыт', 
               'goals' = 'Цели\nрегулирования', 
               'description' = 'Описание\nспособа решения', 
               'degree' = 'Обоснование степени\nвоздействия',
               'groups' = 'Группа участников\nотношений',
               'group_changes' = 'Новое для\nгрупп участников', 
               'group_expenses' = 'Расходы (доходы)\nгрупп участников', 
               'risks' = 'Риски',
               'cancel_duties' = 'Отменяемые\nобязательства',
               'new_functions' = 'Новые\nфункции',
               'kpi' = 'KPI',
               'business' = 'Влияние\nна МСП',
               'necessary_measures' =  'Необходимые меры для\nдостижения целей')

df_g2 <- df_g2[order(df_g2$index, decreasing = T),]
df_g2$group <- text2name[as.character(df_g2$group)]


df_g$impact <- factor(df_g$impact, 
                      levels = c( 'Низкая', "Средняя", "Высокая"))


df_g$group <- text2name[as.character(df_g$group)]

df_g$group <- factor(df_g$group, 
                      levels = df_g2$group)

df_g %>%
  ggplot(aes(y = index, x = group, color = impact, fill = impact))+
  geom_col(position =position_dodge(width = 0.8), 
           width = 0.8)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'),
        legend.position = 'bottom',
        axis.text.x = element_text(size  = 12, color = 'black', angle = 0))+
  geom_text(aes(label=paste(round(100*index, 1), '%', sep = '')),
            size=3, hjust = -.2,
            vjust = 0.4,
            position = position_dodge(width = 0.8),
            color = 'black')+
  scale_fill_brewer(palette = 'Dark2',  name = 'Степень воздействия')+
  scale_color_brewer(palette = 'Dark2', name = 'Степень воздействия')+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks =  seq(0, 1, 0.2),
                     lim = c(0, 1.1))+
  coord_flip()






###########################################
############### Figure 14 #################
###########################################



data_okved$okved <- data_okved$okved
okved <- summary(as.factor(data_okved$okved))


data_okved[is.na(data_okved$okved),]$okved <- 'Все остальные'
data_okved[data_okved$okved %in% names(okved[okved < 100]),]$okved <- 'Все остальные'

df_n <- data_okved[!is.na(data_okved$okved),] %>% 
  group_by(okved) %>%
  summarise(pc = mean(total_index),
            n = n()) 


df_n <- df_n[order(df_n$pc, decreasing = T),]

df_n$okved <- factor(df_n$okved, 
                     levels = df_n$okved)



df_n %>%
  ggplot(aes(x = pc/100, y = okved)) +
  geom_bar(stat="identity", fill = 'lightgray', color = 'black', width = 0.7)+
  geom_text(aes(label=paste(round(pc, 1), '%', ' (',n , ')', sep = '')), vjust=.5,hjust = -0.1, size=4)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 10, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'))+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks =  seq(0, 1, 0.2),
                     lim = c(0, 1.2))





###########################################
############### Figure 15 #################
###########################################


df_n <- data %>% filter(active.d == 1) %>%
  group_by(foiv) %>%
  summarise(pc = mean(total_index),
            n = n()) 

df_n <- df_n[order(df_n$pc, decreasing = T),]

df_n$foiv <- factor(df_n$foiv, 
                    levels = df_n$foiv)


df_n %>% 
  ggplot(aes(x = pc/100, y = foiv)) +
  geom_bar(stat="identity", fill = 'lightgray', color = 'black', width = 0.7)+
  geom_text(aes(label=paste(round(pc, 1), '%', ' (',n , ')', sep = '')), vjust=.5,hjust = -0.1, size=4)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'))+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks =  seq(0, 1, 0.2),
                     lim = c(0, 1))


###########################################
############### Figure 16 #################
###########################################



df_tile <- data %>% filter(active.d==1) %>%
  mutate(
    bin_x = cut(total_index, breaks = 5)) %>%
  group_by(foiv) %>%
  count(bin_x) %>%
  group_by(foiv) %>%
  mutate(s = 100*n/sum(n, na.rm = T)) %>%
  tidyr::complete(bin_x, fill = list(s = 0)) %>%
  mutate(N = sum(n, na.rm = T), na.rm = T,
         foiv = paste(foiv, ' (', N, ')', sep=''))


df_tile$bin_x <- as.character(df_tile$bin_x)
df_tile[df_tile$bin_x == '(-0.1,20]',]$bin_x <- '[0,20]'

df_tile$bin_x <- factor(df_tile$bin_x, 
                        levels = c("[0,20]","(20,40]","(40,60]","(60,80]","(80,100]"))


df_t <- left_join(df_tile[df_tile$bin_x == "(80,100]",],
                  df_tile[df_tile$bin_x == "(60,80]",], by = 'foiv')

df_t <- df_t[order(df_t$s.x,df_t$s.y, decreasing = T),]

df_tile$foiv <- factor(df_tile$foiv, levels = df_t$foiv)



df_tile %>% 
  ggplot(aes(bin_x, foiv, fill = s)) + 
  geom_tile(height = 0.9)+
  scale_fill_gradient2(low = '#67a9cf',
                       mid =  '#f7f7f7',
                       high = '#ef8a62',
                       midpoint = 0,
                       name = "Процент отчётов ведомства")+
  labs(x = 'Уровень заполнения', y = NULL)+
  theme_minimal()+
  theme(legend.position = 'bottom')



###########################################
############### Figure 17 #################
###########################################




df_n <- data %>% filter(active.d ==1 )


df_t <- data.frame(var = factor(c('Количество участников\nотношений', 'Количество участников\nотношений',
                                  'Срок достижения\nцелей', 'Срок достижения\nцелей',
                                  'Оценка видов\nрасходов (доходов)','Оценка видов\nрасходов (доходов)',
                                  'Возможные\nпоступления', 'Возможные\nпоступления',
                                  'Единовременные\nрасходы', 'Единовременные\nрасходы', 
                                  'Периодические\nрасходы', 'Периодические\nрасходы'),
                                levels = c('Срок достижения\nцелей', 'Количество участников\nотношений',
                                           'Оценка видов\nрасходов (доходов)',
                                           'Единовременные\nрасходы', 
                                           'Периодические\nрасходы',
                                           'Возможные\nпоступления')),
                   type = c('Содержательное заполнение', 'Ненулевое заполнение',
                            'Содержательное заполнение', 'Ненулевое заполнение',
                            'Содержательное заполнение', 'Ненулевое заполнение',
                            'Содержательное заполнение', 'Ненулевое заполнение',
                            'Содержательное заполнение', 'Ненулевое заполнение',
                            'Содержательное заполнение', 'Ненулевое заполнение'),
                   val = c(sum(!is.na(df_n$`groups@count_num`)),NA,
                           sum(!is.na(df_n$`goals@timing_num`)),NA,
                           sum(!is.na(df_n$`group_expenses@expenses_num`)), sum(df_n$`group_expenses@expenses_num`>0, na.rm = T),
                           sum(!is.na(df_n$`expenses@income_num`)), sum(df_n$`expenses@income_num`>0, na.rm = T),
                           sum(!is.na(df_n$`expenses@one_exp_num`)), sum(df_n$`expenses@one_exp_num`>0, na.rm = T),
                           sum(!is.na(df_n$`expenses@period_exp_num`)), sum(df_n$`expenses@period_exp_num`>0, na.rm = T)))



df_t$pc <- 100*df_t$val/c(rep(dim(df_n)[1], 4), rep(dim(subset(df_n, impact != 'Низкая'))[1], 8))



pd = position_dodge2(1)

df_t %>%
  ggplot(aes(x = var, y = pc/100, fill = type, color = type))+
  geom_bar(stat = 'identity', position = pd)+
  geom_text(aes(label=paste(round(pc, 1), '%', sep = '')), vjust=-.4,hjust = 0.4, size=3,
            position = pd, color = 'black')+
  theme_minimal()+
  theme(legend.position = 'bottom',
        legend.title = element_blank())+
  labs(x=NULL, y = NULL)+
  scale_fill_brewer(palette = 'Dark2')+
  scale_color_brewer(palette = 'Dark2')+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks =  seq(0, 0.4, 0.1),
                     lim = c(0, 0.4))






###########################################
############### Figure 18 #################
###########################################

df_n <- data %>% filter(active.d == 1 & impact != 'Низкая') %>%
  group_by(foiv) %>%
  summarise(pc = mean(good_index),
            n = n()) 

df_n <- df_n[order(df_n$pc, decreasing = T),]

df_n$foiv <- factor(df_n$foiv, 
                    levels = df_n$foiv)


df_n %>% 
  ggplot(aes(x = pc/100, y = foiv)) +
  geom_bar(stat="identity", fill = 'lightgray', color = 'black', width = 0.7)+
  geom_text(aes(label=paste(round(pc, 1), '%', ' (',n , ')', sep = '')), vjust=.5,hjust = -0.1, size=4)+
  labs(title = NULL, x=NULL, y=NULL)+
  theme_minimal()+
  theme(axis.text.y = element_text(size  = 12, color = 'black'),
        plot.title = element_text(hjust = 0.5, face = 'bold'))+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks =  seq(0, 0.5, 0.1),
                     lim = c(0, 0.45))


###########################################
############### Figure 19 #################
###########################################


data %>% filter(active.d == 1 & result %in% c('Положительное', 'Отрицательное')) %>%
  ggplot(aes(x = total_index/100, fill = result, color = result))+
  geom_histogram(aes(y = ..density..), breaks = seq(0, 1, .04), alpha = 0.25, 
                 position = "identity")+
  theme_minimal()+
  labs(x='Процент заполнения', y = NULL)+
  theme(legend.position = 'bottom',
        legend.title = element_blank())+
  scale_fill_brewer(palette = 'Dark2')+
  scale_color_brewer(palette = 'Dark2')+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2))



##########################################################
##########################################################
# Create data for models in Table 5 and Figures 20, 21, 22
##########################################################
##########################################################


data.result  <- data %>% filter(result %in% c('Положительное', 'Отрицательное') &
                                  active.d == 1)
depart <- summary(as.factor(data.result$foivs))
data.result$foiv.10 <- ifelse(data.result$foivs %in% names(depart[depart>9]), 
                              data.result$foivs, 'Все остальные')
data.result$foiv.10 <- factor(data.result$foiv.10)

data.result$impact <- factor(data.result$impact, levels = c('Низкая', "Средняя", "Высокая"))

okveds <- summary(as.factor(data.result$okved))
data.result$okveds <- data.result$okved
data.result[is.na(data.result$okveds),]$okveds <- 'Все остальные'
data.result[data.result$okveds %in% names(okveds[okveds < 10]),]$okveds <- 'Все остальные'


fit.5 <- lrm(D.result ~ total_index+good_index+impact+ kind+
               lviews +lcomments+ llikes + ldislikes + year_+foiv.10, x=T, y=T, data=data.result)

fit.5  <- robcov(fit.5, cluster=data.result$department)



###########################################
############### Figure 20 #################
###########################################


plt <- get_model_data(fit.5 , type = "emm", terms = "impact")
plt$impact <- factor(c('Низкая', 'Средняя', 'Высокая'),
                   levels = c('Низкая', 'Средняя', 'Высокая'))


plt %>% 
  ggplot(aes(y = predicted, x = impact))+
  geom_point()+
  geom_errorbar(aes(ymin=conf.low, ymax=conf.high), width=0, size = 0.8)+
  theme_minimal()+
  labs(x = NULL, y = NULL)+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0.5, 1, 0.05))





###########################################
############### Figure 21 #################
###########################################


plt <- get_model_data(fit.5 , type = "emm", terms = "lcomments [all]")


plt %>%
  ggplot(aes(x = x, y = predicted))+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high), fill="lightgrey", alpha = 0.5) +
  geom_line(size = 0.6)+
  theme_minimal()+
  labs(x = 'Отзывы, log', y = NULL)+
  ggtitle(NULL)+
  scale_x_continuous(breaks = seq(0, 9, 1))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0.3, 1, 0.1))



###########################################
############### Figure 22 #################
###########################################




plt <- get_model_data(fit.5 , type = "emm", terms = "foiv.10")


plt$foiv <- levels(data.result$foiv.10 )

plt$foiv <- factor(plt$foiv, levels = plt[order(plt$predicted),]$foiv)


plt %>%
  ggplot( aes(x = predicted, y = foiv))+
  geom_point()+
  geom_errorbar(aes(xmin=conf.low, xmax=conf.high), width=0, size = 0.8)+
  theme_minimal()+
  labs(x = NULL, y = NULL)+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.1))



###########################################
############### Figure 23 #################
###########################################



data.refuse <- data %>% filter(status %in% c('Отказ от продолжения разработки',
                                             "Разработка завершена") &
                                 result != "Не определено" )

data.refuse$impact <- factor(data.refuse$impact, levels = c('Низкая', "Средняя", "Высокая"))

depart <- summary(as.factor(data.refuse$foivs))

data.refuse$foiv.10 <- ifelse(data.refuse$foivs %in% names(depart[depart>9]), 
                              data.refuse$foivs, 'Все остальные')

fit.ref <- lrm(D.refuse ~ total_index+good_index+result+
                 lviews +lcomments+ llikes + ldislikes +
                 impact +kind, x=T, y=T, 
               data=data.refuse)

fit.ref <- robcov(fit.ref, cluster=data.refuse$department)

fit.ref.f <- lrm(D.refuse ~ total_index+good_index+result+
                   lviews +lcomments+ llikes + ldislikes +
                   impact +kind + foiv.10 + year_, x=T, y=T, 
                 data=data.refuse)
fit.ref.f <- robcov(fit.ref.f, cluster=data.refuse$department)







plt <- get_model_data(fit.ref , type = "emm", terms = "result")
plt$result <- factor(c('Положительное', 'Отрицательное'),
                   levels = c('Отрицательное', 'Положительное'))

plt%>%
  ggplot( aes(y = predicted, x = result))+
  geom_point()+
  geom_errorbar(aes(ymin=conf.low, ymax=conf.high), width=0, size = 0.8)+
  theme_minimal()+
  labs(x = NULL, y = NULL)+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1))





###########################################
############### Figure 24 #################
###########################################



data.refuse <- data %>% filter(status %in% c('Отказ от продолжения разработки',
                                             "Обсуждение завершено") &
                                 result == "Не определено" )
depart <- summary(as.factor(data.refuse$foivs))

data.refuse$foiv.10 <- ifelse(data.refuse$foivs %in% names(depart[depart>9]), 
                              data.refuse$foivs, 'Все остальные')

data.refuse$impact <- factor(data.refuse$impact, levels = c('Низкая', "Средняя", "Высокая"))

fit.ref2 <- lrm(D.refuse ~ total_index+good_index+
                  lviews +lcomments+ llikes + ldislikes +
                  impact +kind, x=T, y=T, 
                data=data.refuse)


fit.ref2 <- robcov(fit.ref2, cluster=data.refuse$department)

fit.ref2f <- lrm(D.refuse ~ total_index+good_index+
                   lviews +lcomments+ llikes + ldislikes +
                   impact +kind + year_ +foiv.10, x=T, y=T, 
                 data=data.refuse)


fit.ref2f <- robcov(fit.ref2f, cluster=data.refuse$department)



plt <- get_model_data(fit.ref2 , type = "emm", terms = "lcomments [all]")

plt %>%
  ggplot(aes(x = x, y = predicted))+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high), fill="lightgrey", alpha = 0.5) +
  geom_line(size = 0.6)+
  theme_minimal()+
  labs(x = 'Отзывы, log', y = NULL)+
  ggtitle(NULL)+
  scale_x_continuous(breaks = seq(0, 9, 1))+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.1))




#######################################################
#######################################################
# Create data for models in Table 7 and Figures 25, 26
#######################################################
#######################################################


GD_data <- subset(data, kind == 'Проект федерального закона' & result != 'Не определено' )

depart <- summary(as.factor(GD_data$foivs))

GD_data$foiv.10 <- ifelse(GD_data$foivs %in% names(depart[depart>9]), 
                          GD_data$foivs, 'Все остальные')


GD_data$impact <- factor(GD_data$impact, levels = c('Низкая', "Средняя", "Высокая"))

GD_data <- GD_data[!is.na(GD_data$department),]

GD_data$foiv.10 <- factor(GD_data$foiv.10)


GD_data$okveds <- GD_data$okved

GD_data[is.na(GD_data$okveds),]$okveds <- 'Все остальные'

GD_data[GD_data$okveds %in% names(okveds[okveds < 10]),]$okveds <- 'Все остальные'



fit.5 <- lrm(GD ~ total_index+good_index+impact+ result+
               lviews +lcomments+ llikes + ldislikes + year_+foiv.10, x=T, y=T, data=GD_data)

fit.5  <- robcov(fit.5, cluster=GD_data$department)



###########################################
############### Figure 25 #################
###########################################



plt <- get_model_data(fit.5 , type = "emm", terms = "result")
plt$result <- factor(c('Положительное', 'Отрицательное'),
                     levels = c('Отрицательное', 'Положительное'))


plt%>%
  ggplot( aes(y = predicted, x = result))+
  geom_point()+
  geom_errorbar(aes(ymin=conf.low, ymax=conf.high), width=0, size = 0.8)+
  theme_minimal()+
  labs(x = NULL, y = NULL)+
  scale_y_continuous(labels = scales::percent_format(accuracy = 1))






###########################################
############### Figure 26 #################
###########################################


plt <- get_model_data(fit.5 , type = "emm", terms = "foiv.10")


plt$foiv <- levels(GD_data$foiv.10 )

plt$foiv <- factor(plt$foiv, levels = plt[order(plt$predicted),]$foiv)


plt %>%
  ggplot( aes(x = predicted, y = foiv))+
  geom_point()+
  geom_errorbar(aes(xmin=conf.low, xmax=conf.high), width=0, size = 0.8)+
  theme_minimal()+
  labs(x = NULL, y = NULL)+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.1))



###########################################
################ Table 3 ##################
###########################################


stargazer(as.data.frame(orv_info[c('views', 'comments', 'likes', 'dislikes')]), 
          type = 'text',
          decimal.mark = ',', 
          digits = 2,
          digit.separator = '', 
          summary.stat = c('min', 'mean', 'median', 'max', 'sd'),
          covariate.labels = c('Просмотры','Отзывы','Голоса "За"', 'Голоса "Против"'))





###########################################
################ Table 4 ##################
###########################################


t.test(total_index ~ result,
       data = data %>% filter(active.d == 1 & result %in% c('Положительное', 'Отрицательное')))



wilcox.test(subset(data, active.d == 1 & result %in% c('Положительное'))$total_index,
            subset(data, active.d == 1 & result %in% c('Отрицательное'))$total_index)


set.seed(57)
bootstrapped <- two.boot(subset(data, active.d == 1 & result %in% c('Отрицательное'))$total_index, 
                         subset(data, active.d == 1 & result %in% c('Положительное'))$total_index,
                         mean, 10000)
quantile(bootstrapped$t, c(0.025, 0.975))

set.seed(59)
bootstrapped <- two.boot(subset(data, active.d == 1 & result %in% c('Отрицательное'))$total_index, 
                         subset(data, active.d == 1 & result %in% c('Положительное'))$total_index,
                         median, 10000)

quantile(bootstrapped$t, c(0.025, 0.975))






###########################################
################ Table 5 ##################
###########################################



fit.1 <- lrm(D.result ~ total_index+good_index, x=T, y=T, data=data.result)

fit.2 <- lrm(D.result ~ total_index+good_index+impact + kind, x=T, y=T, data=data.result)

fit.3 <- lrm(D.result ~ total_index+good_index+impact+ kind+
               lviews +lcomments+ llikes + ldislikes, x=T, y=T, data=data.result)

fit.4 <- lrm(D.result ~ total_index+good_index+impact+ kind+
               lviews +lcomments+ llikes + ldislikes + year_, x=T, y=T, data=data.result)

fit.5 <- lrm(D.result ~ total_index+good_index+impact+ kind+
               lviews +lcomments+ llikes + ldislikes + year_+foiv.10, x=T, y=T, data=data.result)

fit.6 <- lrm(D.result ~ total_index+good_index+impact+ kind+
               lviews +lcomments+ llikes + ldislikes + year_+foiv.10 + okveds, x=T, y=T, data=data.result)



fit.1  <- robcov(fit.1, cluster=data.result$department)
fit.2  <- robcov(fit.2, cluster=data.result$department)
fit.3  <- robcov(fit.3, cluster=data.result$department)
fit.4  <- robcov(fit.4, cluster=data.result$department)
fit.5  <- robcov(fit.5, cluster=data.result$department)
fit.6  <- robcov(fit.6, cluster=data.result$department)



screenreg(list(fit.1, fit.2, fit.3, fit.4, fit.5, fit.6), 
          digits = 3, stars = c(0.01, 0.05, 0.1),
          omit.coef = "(okveds)|(foiv)|(year)")






###########################################
################ Table 6 ##################
###########################################

# corresponding models are created in Figure 23 and Figure 24

screenreg(list( fit.ref, fit.ref.f, fit.ref2, fit.ref2f), 
          digits = 3, stars = c(0.01, 0.05, 0.1),
          omit.coef = "(okveds)|(foiv)|(year)")


###########################################
################ Table 7 ##################
###########################################





fit.1 <- lrm(GD ~ total_index+good_index+ result, x=T, y=T, data=GD_data)

fit.2 <- lrm(GD ~ total_index+good_index+ result+impact, x=T, y=T, data=GD_data)

fit.3 <- lrm(GD ~ total_index+good_index+impact+ result+
               lviews +lcomments+ llikes + ldislikes, x=T, y=T, data=GD_data)

fit.4 <- lrm(GD ~ total_index+good_index+impact+ result+
               lviews +lcomments+ llikes + ldislikes + year_, x=T, y=T, data=GD_data)

fit.5 <- lrm(GD ~ total_index+good_index+impact+ result+
               lviews +lcomments+ llikes + ldislikes + year_+foiv.10, x=T, y=T, data=GD_data)

fit.6 <- lrm(GD ~ total_index+good_index+impact+ result+
               lviews +lcomments+ llikes + ldislikes + year_+foiv.10 + okveds, x=T, y=T, data=GD_data)



fit.1  <- robcov(fit.1, cluster=GD_data$department)
fit.2  <- robcov(fit.2, cluster=GD_data$department)
fit.3  <- robcov(fit.3, cluster=GD_data$department)
fit.4  <- robcov(fit.4, cluster=GD_data$department)
fit.5  <- robcov(fit.5, cluster=GD_data$department)
fit.6  <- robcov(fit.6, cluster=GD_data$department)


screenreg(list(fit.1, fit.2, fit.3, fit.4, fit.5, fit.6), 
          digits = 3, stars = c(0.01, 0.05, 0.1),
          omit.coef = "(okveds)|(foiv)|(year)")

