#!/bin/sh
rm -rf utils/report_parser # на случай, если он уже был предустановлен
rm -rf report_parser # на случай, если он уже был предустановлен
git clone https://github.com/CAG-ru/report_parser.git
mv report_parser utils/
