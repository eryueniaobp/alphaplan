#!/bin/sh
source ~/.bashrc

cat ./season_1/training_data/order_data/or* > ./season_1/training_data/order_data/all
cat ./season_1/training_data/traffic_data/tr* >./season_1/training_data/traffic_data/all
cat ./season_1/training_data/weather_data/we* >./season_1/training_data/weather_data/all



cat ./season_1/test_set_1/order_data/or* > ./season_1/test_set_1/order_data/all
cat ./season_1/test_set_1/traffic_data/tr* >./season_1/test_set_1/traffic_data/all
cat ./season_1/test_set_1/weather_data/we* >./season_1/test_set_1/weather_data/all


